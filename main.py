import os, sys
from Core.Frontend import HomePageUI
from Core import EnvironmentChecker
from Core import LogUtils

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
        mainLogger = LogUtils.LogUtils(shouldAttachTime = True)
        mainLogger.setLogLevel("T")
        if os.path.join(os.getcwd(), "Core", "Frontend") not in sys.path:
            print("Adding frontend dir to system path.")
            mainLogger.log("I", "Adding frontend dir to system path.", TAG)
            sys.path.insert(0, os.path.join(os.getcwd(), "Core", "Frontend"))
        print("Current work directory: " + os.getcwd())
        mainLogger.log("I", "Current working directory: " + os.getcwd(), TAG)
        pythonHeader = EnvironmentChecker.EnvironmentChecker.detect_python_command()
        print("Python command header: " + str(pythonHeader))
        mainLogger.log("I", "Python command: " + str(pythonHeader), TAG)
        print("Platform: " + os.name)
        mainLogger.log("I", "OS name: " + os.name, TAG)
    except Exception as e:
        print("Exception happened during early init: " + str(e))
        mainLogger.log("F", "Exception happened during early init: " + str(e), TAG)
        exit()
    try:
        EnvironmentChecker.EnvironmentChecker.check_necessary_folders(mainLogger)
        print("Folder check passed.")
        mainLogger.log("I", "Folder check passed.", TAG)
    except Exception as e:
        print("Exception happened when checking necessary folders: " + str(e))
        mainLogger.log("F", "Exception happened when checking necessary folders: " + str(e), TAG)
        exit()
    try:
        print("Starting interface.")
        mainLogger.log("I", "Starting interface.", TAG)
        mainUIInstance = HomePageUI.HomePageUI(logger = mainLogger)
        print("Successfully created UI instance.")
        mainLogger.log("I", "Successfully created UI instance.", TAG)
    except Exception as e:
        print("Exception happened while creating main UI: " + str(e))
        mainLogger.log("F", "Exception happened while creating main UI: " + str(e), TAG)
        exit()
    try:
        while 1:
            mainUIInstance.entry()
    except Exception as e:
        print("Exception happened in main UI:", e)
        mainLogger.log("F", "Exception happened in main UI: " + str(e), TAG)