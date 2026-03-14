import os, subprocess

import Core.LogUtils as LogUtils
import Core.EnvironmentChecker as EnvironmentChecker

class KeyDirUtils:

    def __init__(self, logger = None) -> None:
        if not logger:
            self.myLogger = LogUtils.LogUtils()
            self.myLogger.log("W", "Logger not given, created an instance just now.", "KeyDirUtils")
        else:
            self.myLogger = logger
        self.myLogger.log("I", "Instance of KeyDirUtils successfully created.", "KeyDirUtils")
    def generate_key_file_cache(self, key_file_dir = None, cache_file_name ="keyCache.cache"):
        if key_file_dir is None:
            key_file_dir = os.path.join(os.getcwd(), "Core", "currentKeySet")
        try:
            os.remove(key_file_dir + cache_file_name)
        except FileNotFoundError:
            pass
        try:
            with open(key_file_dir + cache_file_name, "w+") as myFile:
                for root, dirs, fileNames in os.walk(key_file_dir):
                    for fileName in fileNames:
                        if fileName.endswith(".pem"):
                            self.myLogger.log("T", "Key file detected:" + fileName)
                            myFile.write(fileName + ", " + self.__get_sha1(key_file_dir, fileName) + "\n")
        except FileNotFoundError:
            pass
    
    @staticmethod
    def __get_sha1(key_file_dir, file_name):
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
            return subprocess.run(["certutil",
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
            return subprocess.run(["sha1sum",
                                   os.path.join(key_file_dir, file_name.strip(".pem") + "_pub.bin")],
                                  capture_output = True,
                                  text = True).stdout.split("  ")[0]