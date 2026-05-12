#!/usr/bin/env python3

import os
import time

import Core.CLIHandler as CLIHandler
import Core.EnvironmentChecker as EnvironmentChecker
import Frontend.HomePageUI as HomePageUI
import Core.LogUtils as LogUtils
import Core.GlobalConfigUtils as GlobalConfigUtils
from Core.LogUtils import ConsoleLog as cLog

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

    if bool(global_config_info.get_value("check_wsl")):
        check_wsl()

    initialize_logger()

    my_environment_setup = EnvironmentChecker.EnvironmentSetup()
    check_work_directory_correctness()
    should_install = bool(global_config_info.get_value("install_missing_libs"))
    should_check = bool(global_config_info.get_value("check_missing_libs"))
    my_environment_setup.check_libraries(should_install, should_check)
    my_environment_setup.add_frontend_dir_to_path()
    my_environment_setup.check_necessary_folders()

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