"""Cross-platform FEC encoder for AVB signing.

Uses numpy for fast vectorized Reed-Solomon RS(255, N) encoding,
with optional fallback to the platform 'fec' binary or reedsolo.

Algorithm: RS(255, N) over GF(256) with fcr=1 (conventional RS)
  - N = 255 - num_roots
  - Data is split into chunks of (255 - num_roots) bytes
  - Each chunk is independently RS-encoded, producing num_roots parity bytes
  - Parity bytes from all chunks are concatenated to form the FEC data
"""

import math
import os
import shutil
import struct
import subprocess
import tempfile
import time

import numpy as np

from LogUtils import LogUtils

try:
    from reedsolo import RSCodec as _RSCodec
    _HAS_REEDSOLO = True
except ImportError:
    _HAS_REEDSOLO = False

_TAG = "FecEncoder"
_logger = None


def _get_logger():
    """Lazily acquire the LogUtils singleton."""
    global _logger
    if _logger is None:
        _logger = LogUtils(output="file")
    return _logger


# ---------------------------------------------------------------------------
# GF(256) tables and primitives
# ---------------------------------------------------------------------------

_GF_PRIMITIVE = 0x11d
_RS_CODEWORD_SIZE = 255

# Table: gf_mul[a, b] = a * b in GF(256), shape (256, 256) uint8
_gf_mul_table = None

# Encoding matrix cache: {nsym: np.ndarray(chunk_size, nsym) uint8}
_enc_matrices = {}


def _init_gf_tables():
    """Build the full GF(256) multiplication lookup table (64 KB)."""
    global _gf_mul_table
    if _gf_mul_table is not None:
        return

    gf_exp = [0] * 512
    gf_log = [0] * 256
    x = 1
    for i in range(255):
        gf_exp[i] = x
        gf_log[x] = i
        x <<= 1
        if x & 0x100:
            x ^= _GF_PRIMITIVE
    gf_exp[255:512] = gf_exp[0:255]
    gf_log[0] = 0

    table = np.zeros((256, 256), dtype=np.uint8)
    for a in range(256):
        for b in range(256):
            if a == 0 or b == 0:
                table[a, b] = 0
            else:
                table[a, b] = gf_exp[gf_log[a] + gf_log[b]]
    _gf_mul_table = table


def _gf_mul_vector(a_col, b_scalar):
    """Multiply every element of uint8 array a_col by uint8 scalar b_scalar.

    Uses the precomputed lookup table for fast vectorized GF(256) multiply.
    """
    _init_gf_tables()
    if b_scalar == 0:
        return np.zeros_like(a_col)
    if b_scalar == 1:
        return a_col.copy()
    return _gf_mul_table[a_col, b_scalar] # type: ignore


# ---------------------------------------------------------------------------
# RS generator polynomial and encoding matrix
# ---------------------------------------------------------------------------

def _rs_generator_poly(nsym, fcr=1):
    """Compute generator polynomial for RS(nsym) with first root α^fcr.

    g(x) = Π_{i=0}^{nsym-1} (x - α^{fcr + i})

    Returns uint8 numpy array of length nsym+1 where g[0] is the
    constant term and g[nsym] is the leading coefficient (always 1).
    """
    _init_gf_tables()
    g = np.zeros(nsym + 1, dtype=np.uint8)
    g[0] = 1

    for i in range(nsym):
        r = fcr + i
        alpha_r = 1
        for _ in range(r):
            alpha_r = _gf_mul_table[alpha_r, 2]  # type: ignore # multiply by α = 2

        g_new = np.zeros(nsym + 1, dtype=np.uint8)
        g_new[1:] = g[:-1]

        for j in range(len(g)):
            if g[j] != 0:
                g_new[j] ^= _gf_mul_table[g[j], alpha_r] # type: ignore

        g = g_new

    return g


def _compute_enc_matrix(nsym):
    """Return the RS encoding matrix (chunk_size × nsym).

    Row i gives the nsym parity bytes contributed by a single 1
    at message position i, computed via the full RS LFSR encoder.

    Uses reedsolo for guaranteed correctness if available, otherwise
    falls back to a numpy LFSR simulation.
    """
    if nsym in _enc_matrices:
        return _enc_matrices[nsym]

    _init_gf_tables()
    chunk_size = _RS_CODEWORD_SIZE - nsym

    if _HAS_REEDSOLO:
        rs = _RSCodec(nsym=nsym, fcr=1)
        M = np.zeros((chunk_size, nsym), dtype=np.uint8)
        msg = bytearray(chunk_size)
        for i in range(chunk_size):
            msg[i] = 1
            encoded = rs.encode(bytes(msg))
            M[i] = list(encoded[chunk_size:])
            msg[i] = 0
        _enc_matrices[nsym] = M
        return M

    # Fallback: simulate the RS LFSR encoder in numpy
    gen = _rs_generator_poly(nsym, fcr=1)
    g_lower = gen[:-1].copy()

    M = np.zeros((chunk_size, nsym), dtype=np.uint8)

    for pos in range(chunk_size):
        total_len = chunk_size + nsym
        par = np.zeros(total_len, dtype=np.uint8)

        for j in range(nsym):
            par[pos + 1 + j] = g_lower[j]

        for i in range(pos + 1, chunk_size):
            coef = par[i]
            if coef:
                for j in range(nsym):
                    idx = i + 1 + j
                    if idx < total_len:
                        par[idx] ^= _gf_mul_table[int(coef), int(g_lower[j])] # type: ignore

        M[pos] = par[chunk_size:chunk_size + nsym]

    _enc_matrices[nsym] = M
    return M


# ---------------------------------------------------------------------------
# Numpy-based encoding (primary implementation)
# ---------------------------------------------------------------------------

# Files larger than this trigger progress logging
_LARGE_FILE_THRESHOLD = 100 * 1024 * 1024  # 100 MB


def _generate_fec_data_numpy(image_filename, num_roots):
    """Generate FEC parity using numpy vectorized RS encoding.

    Reads the image in batches (~256 MB raw input) to control memory,
    precomputes the encoding matrix, and does GF(256) matmul across
    all chunks in a batch via vectorized multiply + XOR reduction.
    """
    _init_gf_tables()
    chunk_size = _RS_CODEWORD_SIZE - num_roots
    M = _compute_enc_matrix(num_roots)

    file_size = os.path.getsize(image_filename)
    logger = _get_logger()

    if file_size >= _LARGE_FILE_THRESHOLD:
        logger.log("W",
            "FEC encoding large file ({} MB) using numpy, this will take a while..."
            .format(round(file_size / (1024 * 1024))), _TAG)

    target_batch_bytes = 256 * 1024 * 1024
    chunks_per_batch = max(1, target_batch_bytes // chunk_size)
    batch_bytes = chunks_per_batch * chunk_size

    fec_data = bytearray()
    t_last_log = time.time()
    total_read = 0

    with open(image_filename, 'rb') as f:
        while True:
            buf = f.read(batch_bytes)
            if not buf:
                break

            buf = bytearray(buf)
            buf_len = len(buf)

            pad_len = (chunk_size - buf_len % chunk_size) % chunk_size
            if pad_len:
                buf.extend(b'\0' * pad_len)
                buf_len += pad_len

            n_chunks = buf_len // chunk_size
            data_2d = np.frombuffer(buf, dtype=np.uint8).reshape(
                n_chunks, chunk_size)

            parity = np.zeros((n_chunks, num_roots), dtype=np.uint8)
            for j in range(num_roots):
                col = np.zeros(n_chunks, dtype=np.uint8)
                for i in range(chunk_size):
                    m_ij = M[i, j]
                    if m_ij:
                        col ^= _gf_mul_vector(data_2d[:, i], m_ij)
                parity[:, j] = col

            fec_data.extend(parity.tobytes())
            total_read += buf_len

            now = time.time()
            if now - t_last_log >= 30:
                pct = 100.0 * total_read / max(file_size, 1)
                logger.log("W",
                    "FEC encoding progress: {}/{} MB ({:.0f}%)".format(
                        round(total_read / (1024 * 1024)),
                        round(file_size / (1024 * 1024)),
                        pct),
                    _TAG)
                t_last_log = now

    return bytes(fec_data)


_REEDSOLO_WARN_THRESHOLD = 10 * 1024 * 1024  # 10 MB


def _generate_fec_data_reedsolo(image_filename, num_roots):
    """Generate FEC parity using the reedsolo library (slow pure Python).

    Only used as a fallback when numpy is unavailable.
    """
    file_size = os.path.getsize(image_filename)
    chunk_size = _RS_CODEWORD_SIZE - num_roots

    if file_size >= _REEDSOLO_WARN_THRESHOLD:
        n_chunks = math.ceil(file_size / chunk_size)
        est_min = n_chunks * 0.0002 / 60
        _get_logger().log("W",
            "FEC: reedsolo fallback for {} MB file ({} chunks). "
            "This is SLOW — estimated {:.0f} minutes. "
            "Install numpy for fast encoding."
            .format(round(file_size / (1024 * 1024)), n_chunks, max(est_min, 0.1)),
            _TAG)

    rs = _RSCodec(nsym=num_roots, fcr=1)
    fec_data = bytearray()
    carryover = b''
    total = 0
    t_last = time.time()

    with open(image_filename, 'rb') as f:
        while True:
            buffer = f.read(1024 * 1024)
            if not buffer:
                break
            data = carryover + buffer
            carryover = b''

            num_full = len(data) // chunk_size
            for k in range(num_full):
                chunk = data[k * chunk_size:(k + 1) * chunk_size]
                encoded = rs.encode(chunk)
                fec_data.extend(encoded[-num_roots:])

            leftover_start = num_full * chunk_size
            carryover = data[leftover_start:]

            total += len(buffer)
            now = time.time()
            if now - t_last >= 30 and file_size >= _REEDSOLO_WARN_THRESHOLD:
                _get_logger().log("W",
                    "FEC (reedsolo) progress: {}/{} MB ({:.0f}%)".format(
                        round(total / (1024 * 1024)),
                        round(file_size / (1024 * 1024)),
                        100.0 * total / max(file_size, 1)),
                    _TAG)
                t_last = now

    if carryover:
        chunk = carryover.ljust(chunk_size, b'\0')
        encoded = rs.encode(chunk)
        fec_data.extend(encoded[-num_roots:])

    return bytes(fec_data)


# ---------------------------------------------------------------------------
# Binary fallback
# ---------------------------------------------------------------------------

_FEC_FOOTER_FORMAT = '<LLLLLQ32s'
_FEC_MAGIC = 0xfecfecfe
_FEC_FOOTER_SIZE = struct.calcsize(_FEC_FOOTER_FORMAT)
_FEC_BINARY = shutil.which('fec')


def _is_fec_binary_available():
    return _FEC_BINARY is not None


def _calc_fec_data_size_binary(image_size, num_roots):
    p = subprocess.Popen(
        [_FEC_BINARY, '--print-fec-size', str(image_size), # type: ignore
         '--roots', str(num_roots)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE) # type: ignore
    pout, perr = p.communicate()
    retcode = p.wait()
    if retcode != 0:
        raise ValueError('Error invoking fec: {}'.format(
            perr.decode('utf-8', errors='replace')))
    return int(pout)


def _generate_fec_data_binary(image_filename, num_roots):
    with tempfile.NamedTemporaryFile() as fec_tmpfile:
        try:
            subprocess.check_call(
                [_FEC_BINARY, '--encode', '--roots', str(num_roots), # type: ignore
                 image_filename, fec_tmpfile.name],
                stderr=open(os.devnull, 'wb'))
        except subprocess.CalledProcessError as e:
            raise ValueError(
                "Execution of 'fec' tool failed: {}.".format(e)) from e
        fec_data = fec_tmpfile.read()

    footer_data = fec_data[-_FEC_FOOTER_SIZE:]
    (magic, _, _, footer_num_roots, fec_size, _, _) = struct.unpack(
        _FEC_FOOTER_FORMAT, footer_data)
    if magic != _FEC_MAGIC:
        raise ValueError('Unexpected magic in FEC footer')
    if footer_num_roots != num_roots:
        raise ValueError(
            'FEC footer num_roots ({}) does not match requested ({})'.format(
                footer_num_roots, num_roots))
    return fec_data[0:fec_size]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def calc_fec_data_size(image_size, num_roots):
    """Calculate how much space FEC data will take.

    Arguments:
      image_size: The size of the image in bytes.
      num_roots: Number of FEC roots (parity bytes per codeword).

    Returns:
      The number of bytes needed for FEC data.

    Raises:
      ValueError: If the 'fec' binary produces invalid output.
      RuntimeError: If no FEC encoding method is available.
    """
    if _is_fec_binary_available():
        return _calc_fec_data_size_binary(image_size, num_roots)
    # Numpy is required — pure math is always available
    chunk_size = _RS_CODEWORD_SIZE - num_roots
    return num_roots * math.ceil(image_size / chunk_size)


def generate_fec_data(image_filename, num_roots):
    """Generate FEC codes for an image.

    Priority:
      1. External 'fec' binary (exact AOSP match)
      2. Numpy vectorized encoder (fast, cross-platform)
      3. Reedsolo library (slow fallback, warns for files > 10 MB)

    Arguments:
      image_filename: Path to the image file.
      num_roots: Number of FEC roots.

    Returns:
      The FEC parity data as bytes.

    Raises:
      ValueError: If the image doesn't exist or encoding fails.
      RuntimeError: If no FEC encoding method is available.
    """
    if not os.path.exists(image_filename):
        raise ValueError("Image file not found: {}".format(image_filename))

    if _is_fec_binary_available():
        _get_logger().log("I",
            "FEC: using external fec binary for {}".format(image_filename),
            _TAG)
        return _generate_fec_data_binary(image_filename, num_roots)

    # Numpy is the required primary path
    file_size = os.path.getsize(image_filename)
    method = "numpy"
    _get_logger().log("I",
        "FEC: using {} encoder for {} ({} MB, {} roots)".format(
            method, os.path.basename(image_filename),
            round(file_size / (1024 * 1024)), num_roots),
        _TAG)
    return _generate_fec_data_numpy(image_filename, num_roots)
