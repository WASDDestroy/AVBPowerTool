import os
import platform
import shutil
import subprocess
import sys
import threading

from Core.GlobalConfigUtils import GlobalConfigInfo
from Core.LogUtils import ConsoleLog as cLog
from Core.LogUtils import LogUtils

global_config = GlobalConfigInfo()

class EnvironmentChecker:
    @staticmethod
    def detect_python_command():
        """
        Detect available command for starting Python 3 on current system.
        
        Note:
            - Detects Python 3 only.
            - Return first available command when multiple command are available.

        :return: Available Python command, such as python3, python and py.
        :rtype: str
        """

        if os.name == 'nt':
            commands_to_try = [
                'py',        # Python launcher for Windows
                'python',    # Newer Python version, for instance, Python 3.13
                'python3',   # Backup
            ]
        else: # Posix
            commands_to_try = [
                'python3',   # Typical situation
                'python',    # Backup
            ]

        for cmd in commands_to_try:
            try:
                result = subprocess.run(
                    [cmd, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=2,
                    check=False
                )

                if result.returncode == 0:
                    version_output = (result.stdout + result.stderr).lower()

                    if 'python' in version_output and 'python 2' not in version_output:
                        return cmd
                        
            except (subprocess.SubprocessError, FileNotFoundError, PermissionError, OSError):
                continue

        # Return None if no command available
        return None
    
    @staticmethod
    def check_necessary_folders(logger):
        """
        Check necessary folders when program starts up.

        Necessary folders:

        - <root_dir>/Images
        - <root_dir>/Configs
        - <root_dir>/Core/currentConfigs
        - <root_dir>/Core/currentKeySet

        :param logger: logger instance.
        """
        tag = "FolderChecker"
        folder_tuple = ("Images",
                       "Configs",
                        "Keys",
                       os.path.join("Core", "currentConfigs"),
                       os.path.join("Core", "currentKeySet"))
        work_dir = os.getcwd()
        for i in folder_tuple:
            current_dir = os.path.join(work_dir, i)
            if not os.path.exists(current_dir):
                os.mkdir(current_dir)
                logger.log("I", "Folder %s does not exist, automatically created it." % i, tag)
            else:
                logger.log("I", "Folder %s exists." % i, tag)

    @staticmethod
    def is_wsl():
        wsl_env_vars = [
            'WSLENV',
            'WSL_DISTRO_NAME',
            'WSL_INTEROP',
            'WSL_UTF8'
        ]

        env_results = {}
        for var in wsl_env_vars:
            env_results[var] = os.environ.get(var, 'Not set')

        is_wsl = any(os.environ.get(var) for var in wsl_env_vars)
        return env_results, is_wsl

    @staticmethod
    def check_fec_state():
        return False
        # Check system-level fec first
        # if os.name == "nt":
        #     return False
        # else:
        #     # noinspection PyDeprecation
        #     path = shutil.which("fec")
        #     if path:
        #         return True
        # return False

    @staticmethod
    def is_packed_fec_available():
        FEC_PATH = os.path.join(global_config.get_value("bin_dir"), "fec")
        # Check packed fec
        architecture_name = platform.architecture()
        if architecture_name == "AMD64" and os.path.exists(os.path.join(FEC_PATH, "x86_64", "fec")):
            return True
        if architecture_name == "aarch64" and os.path.exists(os.path.join(FEC_PATH, "aarch64", "fec")):
            return True
        return False

    @staticmethod
    def check_libs():
        """
        Check whether necessary libraries are installed.

        Will return True, [] when all requirements are satisfied, else, False with a list of missing libraries will be returned.
        """
        import importlib.util
        lack_libs = []
        # TODO: Use lib names from requirements.txt instead of hardcoded library import string
        for library_name in ("reedsolo", "numpy"):
            if importlib.util.find_spec(library_name) is None:
                lack_libs.append(library_name)
        if lack_libs:
            return False, lack_libs
        else:
            return True, []

    @staticmethod
    def is_in_ide():
        if os.getenv('PYCHARM_HOSTED') == '1':
            return True
        if os.getenv('VSCODE_PID') is not None:
            return True
        return False
                 


class EnvironmentInfo:

    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if EnvironmentInfo._initialized:
            return
        with EnvironmentInfo._lock:
            if EnvironmentInfo._initialized:
                return
        self.python_command = None
        EnvironmentInfo._initialized = True
        pass

    def get_python_command(self):
        if self.python_command is None:
            self.python_command = EnvironmentChecker.detect_python_command()
        return self.python_command

class EnvironmentSetup:

    __TAG = "EnvironmentSetup"

    @staticmethod
    def check_libraries(should_install=True, should_check=True):
        if not should_check:
            return
        missing_libs = EnvironmentChecker.check_libs()[1]
        if missing_libs:
            missing_libs_string = ""
            for i in missing_libs:
                missing_libs_string += i + " "
            print("Missing lib(s):", missing_libs_string)
            if should_install:
                print("Installing dependencies automatically.")
                try:
                    import subprocess
                    subprocess.run(["pip", "install"] + missing_libs)
                except ImportError:
                    print("Failed to import subprocess, exiting.")
                    exit(1)
                except Exception as e:
                    print("Unhandled exception:", e)
                    exit(1)
            else:
                print("Run pip install " + missing_libs_string)
                exit(1)

    def check_necessary_folders(self):
        logger = LogUtils()
        try:
            EnvironmentChecker.check_necessary_folders(logger)
            # print("Folder check passed.")
            logger.log("I", "Folder check passed.", self.__TAG)
        except Exception as e:
            cLog.fatal("Exception happened when checking necessary folders: " + str(e))
            logger.log("F", "Exception happened when checking necessary folders: " + str(e), self.__TAG)
            exit(1)

    def add_frontend_dir_to_path(self):
        logger = LogUtils()
        try:
            if os.path.join(os.getcwd(), "Core", "Frontend") not in sys.path:
                # print("Adding frontend dir to system path.")
                logger.log("I", "Adding frontend dir to system path.", self.__TAG)
                sys.path.insert(0, os.path.join(os.getcwd(), "Core", "Frontend"))
        except Exception as e:
            cLog.fatal("Exception happened when processing frontend folder: " + str(e))
            logger.log("F", "Exception happened when processing frontend folder: " + str(e), self.__TAG)
            exit(1)

    @staticmethod
    def setup_fec():
        # fec_dir = "/usr/local/bin"
        # deps_dir = "/usr/lib"
        logger = LogUtils()
        fec_state = EnvironmentChecker.check_fec_state()
        logger.info("FEC state: " + str(fec_state))
        packed_fec_availability = EnvironmentChecker.is_packed_fec_available()
        logger.info("Packed FEC availability: " + str(packed_fec_availability))
        if (not fec_state) and packed_fec_availability:
            logger.info("Set up fec environment with packed fec")


