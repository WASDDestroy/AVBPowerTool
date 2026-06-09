import argparse
import os

from Core.ConfigManager import ConfigManager
from Core.GlobalConfigUtils import GlobalConfigInfo
from Core.Localization import StringResourceChecker, t
from Core.LogUtils import ConsoleLog as cLog
from Core.LogUtils import LogUtils

TAG_CLI = "CLI"

# Command handlers (placeholders with logging)
def handle_sign(args, logger):
    logger.log("I", f"Sign command invoked with images: {args.images}", TAG_CLI)
    import Core.SignImages as SignImages
    my_signer = SignImages.SignImages()
    if args.images is None:
        cLog.warn(t("cli.image_list_missing"))
        logger.warn(t("cli.image_list_missing"), TAG_CLI)
        try:
            my_signer.sign_images_batch(remove_vb=args.remove_vbmeta, remove_footers_first=args.remove_footer)
        except RuntimeError as e:
            cLog.error(str(e))
    else:
        import Core.ConfigParser as ConfigParser
        my_config_parser = ConfigParser.ConfigParser()
        cherry_pick_result = my_config_parser.cherry_pick_from_config(args.images)
        if not cherry_pick_result:
            cLog.error(t("cli.cherry_pick_failed"))
            logger.error("Failed to cherry pick config from complete config file.", TAG_CLI)
            exit(1)
        try:
            batch_sign_result = my_signer.sign_images_batch(
                os.path.join(os.getcwd(), "Core", "currentConfigs", "tempImageInfo.json"),
                remove_vb=args.remove_vbmeta, remove_footers_first=args.remove_footer)
            if batch_sign_result[0]:
                cLog.info(t("cli.sign_selected_success"))
            else:
                cLog.error(t("cli.sign_selected_failed", error=str(batch_sign_result[1])))
        except RuntimeError as e:
            cLog.error(str(e))
        my_config_parser.remove_cherry_pick_file()


def handle_read(args, logger):
    logger.log("I", f"Read command invoked with images: {args.images}", TAG_CLI)
    import Core.ImageInfoUtils as ImageInfoUtils
    import Core.ConfigParser as ConfigParser
    my_image_info_utils = ImageInfoUtils.ImageInfoUtils()
    if args.images is None:
        cLog.warn(t("cli.image_list_missing"))
        my_config_parser = ConfigParser.ConfigParser()
        my_image_info_utils.read_image_info_batch(my_config_parser.get_image_list())
    else:
        cLog.info(t("cli.reading_vbmeta_info"))
        my_image_info_utils.read_image_info_batch(args.images)

def handle_save(args, logger):
    logger.log("I", f"Save command invoked with name: {args.name}", TAG_CLI)
    import Core.ConfigManager as ConfigManager
    my_config_manager = ConfigManager.ConfigManager()
    if my_config_manager.save_as_persistent_config(args.name):
        cLog.info(t("cli.save_config_success"))
    else:
        cLog.error(t("cli.save_config_failed"))

def handle_set_active(args, logger):
    logger.log("I", f"Set active command invoked with name: {args.name}", TAG_CLI)
    import Core.ConfigManager as ConfigManager
    my_config_manager = ConfigManager.ConfigManager()
    if my_config_manager.set_config_active(args.name):
        cLog.info(t("cli.activate_config_success"))
    else:
        cLog.error(t("cli.activate_config_failed"))

def handle_import(args, logger):
    logger.log("I", f"Import command invoked with file: {args.file}", TAG_CLI)
    import Core.ConfigManager as ConfigManager
    my_config_manager = ConfigManager.ConfigManager()
    archive_type = my_config_manager.check_config_type(file_name=args.file)
    logger.log("I", "Archive type is %s" % archive_type, TAG_CLI)
    if archive_type == "SINGLE":
        try:
            my_config_manager.import_single_config(import_from_file_name=args.file)
            cLog.info(t("cli.import_single_success", file=args.file))
        except Exception as e:
            logger.log("W", e, TAG_CLI)
            cLog.error(t("cli.import_failed"))
    elif archive_type == "BATCH":
        try:
            my_config_manager.batch_import_config(import_from_file_name=args.file)
            cLog.info(t("cli.import_batch_success"))
        except Exception as e:
            logger.log("W", e, TAG_CLI)
            cLog.error(t("cli.import_failed_with_log"))
    else:
        cLog.error(t("cli.invalid_archive_file"))

def handle_export(args, logger):
    import Core.ConfigManager as ConfigManager
    my_config_manager = ConfigManager.ConfigManager()
    logger.log("I", f"Export command invoked with file: {args.config}", TAG_CLI)
    export_result = my_config_manager.export_single_config(
                    export_config_folder_name=args.config, export_to_file_name=args.config + ".zip")
    if export_result:
        cLog.info(t("cli.export_success"))
    else:
        cLog.error(t("cli.export_failed"))

def handle_about():
    global_config = GlobalConfigInfo()
    print(t("cli.about.version", version=global_config.get_value("tool_version")))

def handle_get_all_configs():
    configs = ConfigManager.get_all_configs()
    config_string = ""
    for config in configs:
        config_string += config + " "
    print(config_string)

def handle_check_l10n():
    global_config = GlobalConfigInfo()
    language = global_config.get_value("language") or "en"
    missing_strings = StringResourceChecker.get_missing_strings()
    if not missing_strings:
        print(t("cli.check_l10n.no_missing", language=language))
        return
    print(t("cli.check_l10n.missing_header", language=language, count=len(missing_strings)))
    for key in sorted(missing_strings.keys()):
        print(StringResourceChecker.build_xml_string_entry(key, missing_strings[key]))

def setup_argparse():
    parser = argparse.ArgumentParser(prog="AVBPowerTool", description=t("cli.description"))
    subparsers = parser.add_subparsers(dest="command", help=t("cli.available_commands"), required=False)

    # sign command
    parser_sign = subparsers.add_parser("sign", help=t("cli.sign.help"))
    parser_sign.add_argument("--images", nargs="+", help=t("cli.sign.images_help"))
    parser_sign.add_argument("--remove_footer", help=t("cli.sign.remove_footer_help"), action="store_true")
    parser_sign.add_argument("--remove_vbmeta", help=t("cli.sign.remove_vbmeta_help"), action="store_true")

    # read command
    parser_read = subparsers.add_parser("read", help=t("cli.read.help"))
    parser_read.add_argument("--images", nargs="+", help=t("cli.read.images_help"))

    # save command
    parser_save = subparsers.add_parser("save", help=t("cli.save.help"))
    parser_save.add_argument("--name", required=True, help=t("cli.save.name_help"))

    # set_active command
    parser_set_active = subparsers.add_parser("activate", help=t("cli.activate.help"))
    parser_set_active.add_argument("--name", required=True, help=t("cli.activate.name_help"))

    # import command
    parser_import = subparsers.add_parser("import", help=t("cli.import.help"))
    parser_import.add_argument("--file", required=True, help=t("cli.import.file_help"))

    # export command
    parser_export = subparsers.add_parser("export", help=t("cli.export.help"))
    parser_export.add_argument("--config", required=True, help=t("cli.export.config_help"))

    # get_all_configs_command
    subparsers.add_parser("get_all_config", help=t("cli.get_all_config.help"))

    # check_l10n command
    subparsers.add_parser("check_l10n", help=t("cli.check_l10n.help"))

    # about command
    subparsers.add_parser("about", help=t("cli.about.help"))

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
        elif args.command == "activate":
            handle_set_active(args, logger)
        elif args.command == "import":
            handle_import(args, logger)
        elif args.command == "export":
            handle_export(args, logger)
        elif args.command == "about":
            handle_about()
        elif args.command == "get_all_config":
            handle_get_all_configs()
        elif args.command == "check_l10n":
            handle_check_l10n()
        else:
            logger.log("E", f"Unknown command: {args.command}", TAG_CLI)
            return 2
    return 0
