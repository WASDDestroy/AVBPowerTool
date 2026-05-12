import argparse
import os

from Core.GlobalConfigUtils import GlobalConfigInfo
from Core.LogUtils import ConsoleLog as cLog
from Core.LogUtils import LogUtils

TAG_CLI = "CLI"

# Command handlers (placeholders with logging)
def handle_sign(args, logger):
    logger.log("I", f"Sign command invoked with images: {args.images}", TAG_CLI)
    import Core.SignImages as SignImages
    my_signer = SignImages.SignImages()
    if args.images is None:
        cLog.warn("Image list not given! Defaulting to all images.")
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
    import Core.ImageInfoUtils as ImageInfoUtils
    import Core.ConfigParser as ConfigParser
    my_image_info_utils = ImageInfoUtils.ImageInfoUtils()
    if args.images is None:
        cLog.warn("Image list not given! Defaulting to all images.")
        my_config_parser = ConfigParser.ConfigParser()
        my_image_info_utils.read_image_info_batch(my_config_parser.get_image_list())
    else:
        cLog.info("Reading vbmeta info from image file.")
        my_image_info_utils.read_image_info_batch(args.images)

def handle_save(args, logger):
    logger.log("I", f"Save command invoked with name: {args.name}", TAG_CLI)
    import Core.ConfigManager as ConfigManager
    my_config_manager = ConfigManager.ConfigManager()
    if my_config_manager.save_as_persistent_config(args.name):
        cLog.info("Successfully saved config to persistent storage.")
    else:
        cLog.error("Failed to save config to persistent storage. Refer to log for further information.")

def handle_set_active(args, logger):
    logger.log("I", f"Set active command invoked with name: {args.name}", TAG_CLI)
    import Core.ConfigManager as ConfigManager
    my_config_manager = ConfigManager.ConfigManager()
    if my_config_manager.set_config_active(args.name):
        cLog.info("Successfully activated config.")
    else:
        cLog.error("Failed to activate config. Refer to log for further information.")

def handle_import(args, logger):
    logger.log("I", f"Import command invoked with file: {args.file}", TAG_CLI)
    import Core.ConfigManager as ConfigManager
    my_config_manager = ConfigManager.ConfigManager()
    archive_type = my_config_manager.check_config_type(file_name=args.file)
    logger.log("I", "Archive type is %s" % archive_type, TAG_CLI)
    if archive_type == "SINGLE":
        try:
            my_config_manager.import_single_config(import_from_file_name=args.file)
            cLog.info("Successfully imported single config archive %s." % args.file)
        except Exception as e:
            logger.log("W", e, TAG_CLI)
            cLog.error("Import failed!")
    elif archive_type == "BATCH":
        try:
            my_config_manager.batch_import_config(import_from_file_name=args.file)
            cLog.info("Successfully imported config.")
        except Exception as e:
            logger.log("W", e, TAG_CLI)
            cLog.error("Import failed! Refer to log file for further information.")
    else:
        cLog.error("Invalid archive file.")

def handle_export(args, logger):
    import Core.ConfigManager as ConfigManager
    my_config_manager = ConfigManager.ConfigManager()
    logger.log("I", f"Export command invoked with file: {args.config}", TAG_CLI)
    export_result = my_config_manager.export_single_config(
                    export_config_folder_name=args.config, export_to_file_name=args.config + ".zip")
    if export_result:
        cLog.info("Successfully exported selected config to root directory as an archive.")
    else:
        cLog.error("Failed to export config!")

def handle_about():
    global_config = GlobalConfigInfo()
    print("AVBPowerTool Version " + global_config.get_value("tool_version"))

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
    parser_export.add_argument("--config", required=True, help="Name of single config to export")

    # about command
    subparsers.add_parser("about", help="Show about message")

    return parser

def parse_tool_args(args):
    # Exit code: 0 - CLI mode exited successfully, 1 - start interactive UI, 2 - exception happened
    logger = LogUtils()
    if args.command is None:
        # No command: run UI
        return 1
    else:
        # Dispatch to appropriate handler
        if args.command == "sign":
            handle_sign(args, logger)
        elif args.command == "read":
            handle_read(args, logger)
        elif args.command == "save":
            handle_save(args, logger)
        elif args.command == "set_active":
            handle_set_active(args, logger)
        elif args.command == "import":
            handle_import(args, logger)
        elif args.command == "export":
            handle_export(args, logger)
        elif args.command == "about":
            handle_about()
        else:
            logger.log("E", f"Unknown command: {args.command}", TAG_CLI)
            return 2
    return 0