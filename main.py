import os
import sys
import time
import Core.Frontend.HomePageUI as HomePageUI
import Core.EnvironmentChecker as EnvironmentChecker
import Core.LogUtils as LogUtils
import Core.Frontend.UIUtils as UIUtils

def print_logo():
    try:
        for i in range(5):
            print("")
        with open(os.path.join(os.getcwd(), "Core", "Frontend", "text_logo.txt"), "r") as f:
            logo_lines = f.readlines()
            for i in logo_lines:
                print(i, end="")
        for i in range(5):
            print("")
        time.sleep(0.5)
    except FileNotFoundError:
        pass
try:
    if __name__ == "__main__":
        TAG = "Main"
        try:
            print("Checking directory correctness.")
            current_file = os.path.abspath(__file__)
            current_dir = os.path.dirname(current_file)
            os.chdir(current_dir)
            print("Current work directory: " + os.getcwd())
        except Exception as e:
            print("Exception happened when handling working directory:", e)
            exit()
        try:
            main_logger = LogUtils.LogUtils(should_attach_time=True)
            main_logger.set_log_level("T")
            if os.path.join(os.getcwd(), "Core", "Frontend") not in sys.path:
                print("Adding frontend dir to system path.")
                main_logger.log("I", "Adding frontend dir to system path.", TAG)
                sys.path.insert(0, os.path.join(os.getcwd(), "Core", "Frontend"))
            print("Current work directory: " + os.getcwd())
            main_logger.log("I", "Current working directory: " + os.getcwd(), TAG)
            pythonHeader = EnvironmentChecker.EnvironmentChecker.detect_python_command()
            print("Python command header: " + str(pythonHeader))
            main_logger.log("I", "Python command: " + str(pythonHeader), TAG)
            print("Platform: " + os.name)
            main_logger.log("I", "OS name: " + os.name, TAG)
        except Exception as e:
            print("Exception happened during early init: ", e)
            exit()
        try:
            EnvironmentChecker.EnvironmentChecker.check_necessary_folders(
                main_logger)
            print("Folder check passed.")
            main_logger.log("I", "Folder check passed.", TAG)
        except Exception as e:
            print("Exception happened when checking necessary folders: " + str(e))
            main_logger.log(
                "F", "Exception happened when checking necessary folders: " + str(e), TAG)
            exit()
        try:
            print("Prepare essential components.")
            ui_util = UIUtils.UIUtils(main_logger)
        except Exception as e:
            print("Exception happened during essentials preparation: " + str(e))
            main_logger.log("F", "Exception happened during essentials preparation: " + str(e), TAG)
            exit()
        try:
            print("Starting interface.")
            main_logger.log("I", "Starting interface.", TAG)
            mainUIInstance = HomePageUI.HomePageUI(logger=main_logger, ui_utils=ui_util)
            print("Successfully created UI instance.")
            main_logger.log("I", "Successfully created UI instance.", TAG)
        except Exception as e:
            print("Exception happened while creating main UI: " + str(e))
            main_logger.log(
                "F", "Exception happened while creating main UI: " + str(e), TAG)
            exit()
        print_logo()
        try:
            while 1:
                mainUIInstance.entry()
        except Exception as e:
            print("Exception happened in main UI:", e)
            print("Please refer to log file for further information.")
            main_logger.log("F", "Exception happened in main UI: " + str(e), TAG)
except KeyboardInterrupt:
    print("\nCtrl + C is pressed, exiting.")