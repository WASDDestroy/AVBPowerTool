import os, subprocess
from typing import List

import Core.LogUtils as LogUtils
import Core.EnvironmentChecker as EnvironmentChecker

class KeyDirUtils:

    def __init__(self) -> None:
        self.TAG = "KeyDirUtils"
        self.my_logger = LogUtils.LogUtils()
        self.my_logger.log("I", "Instance of KeyDirUtils successfully created.", self.TAG)

    def generate_key_file_cache(self, key_file_dir = None, cache_file_name ="keyCache.cache"):
        """
        Generate a key file cache.
        This cache file contains all .pem files' names and corresponding SHA1 digests.
        :param key_file_dir: Directory containing .pem files.
        :param cache_file_name: Name of .cache file, defaults to keyCache.cache.
        """
        if key_file_dir is None:
            key_file_dir = os.path.join(os.getcwd(), "Core", "currentKeySet")
        try:
            os.remove(os.path.join(key_file_dir, cache_file_name))
        except FileNotFoundError:
            pass
        try:
            with open(key_file_dir + cache_file_name, "w+") as my_file:
                for root, dirs, fileNames in os.walk(key_file_dir):
                    for fileName in fileNames:
                        if fileName.endswith(".pem"):
                            self.my_logger.log("T", "Key file detected:" + fileName, self.TAG)
                            my_file.write(fileName + ", " + self.__get_sha1(key_file_dir, fileName) + "\n")
        except FileNotFoundError:
            pass

    def __get_sha1(self, key_file_dir, file_name) -> str:
        """
        Extract key SHA1 from .pem files.
        :param key_file_dir: Directory containing .pem files.
        :param file_name: Name of .pem file.
        :return: SHA1 digest in HEX format.
        """
        command_header = EnvironmentChecker.EnvironmentChecker.detect_python_command()
        if command_header is None:
            raise RuntimeError("Unable to find proper Python")
        if os.name == 'nt':
            subprocess.run([command_header,
                            os.path.join(os.getcwd(), "Core", "avbtool.py"),
                            "extract_public_key",
                            "--key",
                            os.path.join(key_file_dir, file_name),
                            "--output",
                            os.path.join(key_file_dir, file_name.strip(".pem") + "_pub.bin")])
            sha1_result = subprocess.run(["certutil",
                                   "-hashfile",
                                   os.path.join(key_file_dir, file_name.strip(".pem") + "_pub.bin"),
                                   "sha1"],
                                   capture_output = True,
                                   text = True).stdout.split("\n")[1]
        else:
            subprocess.run([command_header,
                            os.path.join(os.getcwd(), "Core", "avbtool.py"),
                            "extract_public_key",
                            "--key",
                            os.path.join(key_file_dir, file_name),
                            "--output",
                            os.path.join(key_file_dir, file_name.strip(".pem") + "_pub.bin")])
            sha1_result = subprocess.run(["sha1sum",
                                   os.path.join(key_file_dir, file_name.strip(".pem") + "_pub.bin")],
                                  capture_output = True,
                                  text = True).stdout.split("  ")[0]
        self.my_logger.log("I", "Filename: %s, SHA1 digest: %s" % (file_name, sha1_result), self.TAG)
        return sha1_result

    def get_pem_filenames(self, config_name: str = "current") -> List[str]:
        """
        Get all .pem file names in folder, not in cache file.
        :param config_name: Config directory containing .pem files, defaults to "current".
        """
        directory_name = os.path.join(os.getcwd(), "Keys", config_name)
        if directory_name == "current":
            self.my_logger.log("I", "Traverse active config dir", "KeyDirUtils")
            directory_name = os.path.join(os.getcwd(), "Core", "currentKeySet")
        else:
            self.my_logger.log("I", "Traverse config dir %s in persistent config" % config_name, "KeyDirUtils")

        pem_filenames = []

        for i in os.listdir(directory_name):
            if i.endswith(".pem"):
                pem_filenames.append(i)

        self.my_logger.log("I", "Pem file names: %s" % str(pem_filenames), self.TAG)
        return pem_filenames

    def get_cached_info(self, config_name: str = "current") -> list:
        """
        Get filename with corresponding SHA1 digest in a list.
        Format: [[Filename, SHA1 digest], [Another Filename, Another SHA1 digest]]
        :param config_name: Config directory containing .pem files, defaults to "current".
        :return: Filename with corresponding SHA1 digest in a list.
        """
        cache_path = os.path.join(os.getcwd(), "Keys", config_name, "keyCache.cache")
        if config_name == "current":
            cache_path = os.path.join(os.getcwd(), "Core", "currentKeySet", "keyCache.cache")
            self.my_logger.log("I", "Get key info of active config", self.TAG)
        with open(cache_path, "r") as my_file:
            result_list = []
            file_lines = my_file.readlines()
            for file_line in file_lines:
                self.my_logger.log("I", "Line: " % file_line, self.TAG)
                file_line : str = file_line.strip()
                splitter_position = file_line.find(", ")
                file_name : str = file_line[:splitter_position]
                key_digest : str = file_line[splitter_position + 2:]
                result_list.append([file_name, key_digest])
        return result_list