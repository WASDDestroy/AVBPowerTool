#!/usr/bin/env python3

import os
import sys
import time

import Core.CLIHandler as CLIHandler
import Core.EnvironmentChecker as EnvironmentChecker
import Frontend.HomePageUI as HomePageUI
import Core.LogUtils as LogUtils
import Core.GlobalConfigUtils as GlobalConfigUtils
from Core.LogUtils import ConsoleLog as cLog

TAG_CLI = "CLI"
TAG = "Main"
CONFIG_PATH = os.path.join(os.getcwd(), "GlobalConfig.cfg")

def print_logo():
    try:
        for i in range(5):
            print("")
        global_config_info = GlobalConfigUtils.GlobalConfigInfo()
        logo_path = global_config_info.get_value("logo_path")
        with open(logo_path, "r") as f:
            logo_lines = f.readlines()
            for i in logo_lines:
                print(i, end="")
        for i in range(5):
            print("")
        time.sleep(0.5)
    except FileNotFoundError:
        pass

def run_ui():
    """Start the interactive UI."""
    logger = LogUtils.LogUtils()
    logger.log("I", "Starting interface.", "Main")
    main_ui_instance = HomePageUI.HomePageUI()
    logger.log("I", "Successfully created UI instance.", "Main")
    print_logo()
    while True:
        main_ui_instance.entry()

def initialize_logger():
    global_config_info = GlobalConfigUtils.GlobalConfigInfo()
    logger = LogUtils.LogUtils(should_attach_time=int(global_config_info.get_value("log_attach_time")),
                               flush_threshold=int(global_config_info.get_value("log_flush_threshold")),
                               log_dir=global_config_info.get_value("log_destination"))
    logger.set_log_level(global_config_info.get_value("log_level"))

def check_wsl():
    if EnvironmentChecker.EnvironmentChecker.is_wsl()[1] and os.getcwd().startswith("/mnt"):
        print("NEVER RUN THIS PROGRAM IN WSL WITH SCRIPTS STORED IN NTFS WORLD")
        print("MAY RESULT IN PERMISSION DENIAL OF NUMEROUS FILES")
        print("COPY THIS FOLDER TO LINUX WORLD AND TRY AGAIN")
        exit(1)

def check_work_directory_correctness():
    try:
        # print("Checking directory correctness.")
        current_file = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file)
        os.chdir(current_dir)
        # print("Current work directory: " + os.getcwd())
    except Exception as e:
        cLog.fatal("Exception happened when handling working directory:" + str(e))
        exit(1)

def check_libraries(should_install = True):
    missing_libs = EnvironmentChecker.EnvironmentChecker.check_libs()[1]
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

def check_necessary_folders():
    logger = LogUtils.LogUtils()
    try:
        EnvironmentChecker.EnvironmentChecker.check_necessary_folders(logger)
        # print("Folder check passed.")
        logger.log("I", "Folder check passed.", TAG)
    except Exception as e:
        cLog.fatal("Exception happened when checking necessary folders: " + str(e))
        logger.log("F", "Exception happened when checking necessary folders: " + str(e), TAG)
        exit(1)

def add_frontend_dir_to_path():
    logger = LogUtils.LogUtils()
    try:
        if os.path.join(os.getcwd(), "Core", "Frontend") not in sys.path:
            # print("Adding frontend dir to system path.")
            logger.log("I", "Adding frontend dir to system path.", TAG)
            sys.path.insert(0, os.path.join(os.getcwd(), "Core", "Frontend"))
    except Exception as e:
        cLog.fatal("Exception happened when processing frontend folder: " + str(e))
        logger.log("F", "Exception happened when processing frontend folder: " + str(e), TAG)
        exit(1)

def log_system_info():
    logger = LogUtils.LogUtils()
    # print("Current work directory: " + os.getcwd())
    logger.log("I", "Current working directory: " + os.getcwd(), TAG)
    python_header = EnvironmentChecker.EnvironmentChecker.detect_python_command()
    # print("Python command header: " + str(pythonHeader))
    logger.log("I", "Python command: " + str(python_header), TAG)
    # print("Platform: " + os.name)
    logger.log("I", "OS name: " + os.name, TAG)

def main():
    # Initialization
    global_config_utils = GlobalConfigUtils.GlobalConfigUtils()
    global_config_info = GlobalConfigUtils.GlobalConfigInfo()
    global_config_info.set_values_by_dict(global_config_utils.parse_key_value_file(CONFIG_PATH))
    if int(global_config_info.get_value("check_wsl")):
        check_wsl()
    initialize_logger()
    check_work_directory_correctness()
    check_libraries()
    add_frontend_dir_to_path()
    check_necessary_folders()

    # Parse command line arguments
    parser = CLIHandler.setup_argparse()
    args = parser.parse_args()
    retval = CLIHandler.parse_tool_args(args)
    if retval == 0:
        exit(0)
    elif retval == 1:
        run_ui()
    elif retval == 2:
        exit(1)

try:
    if __name__ == "__main__":
        main()
except KeyboardInterrupt:
    print("\nCtrl + C is pressed, exiting.")