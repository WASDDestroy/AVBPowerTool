import argparse
import os
import sys
import time

import Core.EnvironmentChecker as EnvironmentChecker
import Core.Frontend.HomePageUI as HomePageUI
import Core.LogUtils as LogUtils
from Core.LogUtils import ConsoleLog as cLog

TAG_CLI = "CLI"
TAG = "Main"

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

# Command handlers (placeholders with logging)
def handle_sign(args, logger):
    logger.log("I", f"Sign command invoked with images: {args.images}", TAG_CLI)
    import Core.SignImages as SignImages
    my_signer = SignImages.SignImages()
    if args.images is None:
        logger.warn("Image list not given! Defaulting to all images.", TAG_CLI)
        try:
            my_signer.sign_images_batch(remove_vb=args.remove_vbmeta, remove_footers_first=args.remove_footer)
        except RuntimeError as e:
            cLog.error(str(e))
    else:
        import Core.ConfigParser as ConfigParser
        my_config_parser = ConfigParser.ConfigParser()
        cherry_pick_result = my_config_parser.cherry_pick_from_config(args.images)
        if not cherry_pick_result:
            cLog.error("Failed to cherry pick from config.")
            logger.error("Failed to cherry pick config from complete config file.", TAG_CLI)
            exit(1)
        try:
            batch_sign_result = my_signer.sign_images_batch(
                os.path.join(os.getcwd(), "Core", "currentConfigs", "tempImageInfo.json"),
                remove_vb=args.remove_vbmeta, remove_footers_first=args.remove_footer)
            if batch_sign_result[0]:
                cLog.info("Successfully signed selected images!")
            else:
                cLog.error("Failed to sign selected images! Error: " + str(batch_sign_result[1]))
        except RuntimeError as e:
            cLog.error(str(e))
        my_config_parser.remove_cherry_pick_file()


def handle_read(args, logger):
    logger.log("I", f"Read command invoked with images: {args.images}", TAG_CLI)
    # TODO: implement read logic
    pass

def handle_save(args, logger):
    logger.log("I", f"Save command invoked with name: {args.name}", TAG_CLI)
    # TODO: implement save logic
    pass

def handle_set_active(args, logger):
    logger.log("I", f"Set active command invoked with name: {args.name}", TAG_CLI)
    # TODO: implement set_active logic
    pass

def handle_import(args, logger):
    logger.log("I", f"Import command invoked with file: {args.file}", TAG_CLI)
    # TODO: implement import logic
    pass

def handle_export(args, logger):
    logger.log("I", f"Export command invoked with file: {args.file}", TAG_CLI)
    # TODO: implement export logic
    pass

def run_ui(logger):
    """Start the interactive UI."""
    logger.log("I", "Starting interface.", "Main")
    main_ui_instance = HomePageUI.HomePageUI()
    logger.log("I", "Successfully created UI instance.", "Main")
    print_logo()
    while True:
        main_ui_instance.entry()

def handle_about():
    print("AVBPowerTool Version")

def setup_argparse():
    parser = argparse.ArgumentParser(prog="AVBPowerTool", description="Image signing and configuration tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands", required=False)

    # sign command
    parser_sign = subparsers.add_parser("sign", help="Sign given images")
    parser_sign.add_argument("--images", nargs="+", help="List of partition names (e.g., boot dtbo vbmeta)")
    parser_sign.add_argument("--remove_footer", help="Remove footers of selected images before signing.", action="store_true")
    parser_sign.add_argument("--remove_vbmeta", help="Remove vbmeta images before signing.", action="store_true")

    # read command
    parser_read = subparsers.add_parser("read", help="Read vbmeta info of given images")
    parser_read.add_argument("--images", nargs="+", help="List of partition names")

    # save command
    parser_save = subparsers.add_parser("save", help="Save current config to persistent storage")
    parser_save.add_argument("--name", required=True, help="Name to assign to the saved config")

    # set_active command
    parser_set_active = subparsers.add_parser("set_active", help="Set a config as active")
    parser_set_active.add_argument("--name", required=True, help="Name of the config to activate")

    # import command
    parser_import = subparsers.add_parser("import", help="Import config from zip archive")
    parser_import.add_argument("--file", required=True, help="Path to the zip archive")

    # export command
    parser_export = subparsers.add_parser("export", help="Export config to zip archive")
    parser_export.add_argument("--file", required=True, help="Destination path for the zip archive")

    # about command
    subparsers.add_parser("about", help="Show about message")

    return parser

try:
    if __name__ == "__main__":
        try:
            # print("Checking directory correctness.")
            current_file = os.path.abspath(__file__)
            current_dir = os.path.dirname(current_file)
            os.chdir(current_dir)
            # print("Current work directory: " + os.getcwd())
        except Exception as e:
            cLog.fatal("Exception happened when handling working directory:" + str(e))
            exit()
        try:
            main_logger = LogUtils.LogUtils(should_attach_time=True)
            main_logger.set_log_level("T")
            if os.path.join(os.getcwd(), "Core", "Frontend") not in sys.path:
                # print("Adding frontend dir to system path.")
                main_logger.log("I", "Adding frontend dir to system path.", TAG)
                sys.path.insert(0, os.path.join(os.getcwd(), "Core", "Frontend"))
            # print("Current work directory: " + os.getcwd())
            main_logger.log("I", "Current working directory: " + os.getcwd(), TAG)
            pythonHeader = EnvironmentChecker.EnvironmentChecker.detect_python_command()
            # print("Python command header: " + str(pythonHeader))
            main_logger.log("I", "Python command: " + str(pythonHeader), TAG)
            # print("Platform: " + os.name)
            main_logger.log("I", "OS name: " + os.name, TAG)
        except Exception as e:
            cLog.fatal("Exception happened during early init: " + str(e))
            exit()
        try:
            EnvironmentChecker.EnvironmentChecker.check_necessary_folders(main_logger)
            # print("Folder check passed.")
            main_logger.log("I", "Folder check passed.", TAG)
        except Exception as e:
            cLog.fatal("Exception happened when checking necessary folders: " + str(e))
            main_logger.log("F", "Exception happened when checking necessary folders: " + str(e), TAG)
            exit()

        # Parse command line arguments
        parser = setup_argparse()
        args = parser.parse_args()

        if args.command is None:
            # No command: run UI
            run_ui(main_logger)
        else:
            # Dispatch to appropriate handler
            if args.command == "sign":
                handle_sign(args, main_logger)
            elif args.command == "read":
                handle_read(args, main_logger)
            elif args.command == "save":
                handle_save(args, main_logger)
            elif args.command == "set_active":
                handle_set_active(args, main_logger)
            elif args.command == "import":
                handle_import(args, main_logger)
            elif args.command == "export":
                handle_export(args, main_logger)
            elif args.command == "about":
                handle_about()
            else:
                main_logger.log("E", f"Unknown command: {args.command}", TAG_CLI)
                sys.exit(1)
except KeyboardInterrupt:
    print("\nCtrl + C is pressed, exiting.")