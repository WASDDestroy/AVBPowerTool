"""
AVB (Android Verified Boot) information display helpers.
"""
from typing import Any, Dict
import os

import Core.ConfigParser as ConfigParser
import Frontend.UIUtils as UIUtils
from Core.Localization import t


def load_avb_data() -> Dict[str, Any]:
    my_config_parser = ConfigParser.ConfigParser()
    return my_config_parser.json2_dic()


def _resource_key_for_avb_key(key: str) -> str:
    normalized_key = key.replace("(", "").replace(")", "")
    normalized_key = normalized_key.replace("-", "_").replace(" ", "_")
    return "display_avb.key." + normalized_key


def get_display_key_name(key: str) -> str:
    translated = t(_resource_key_for_avb_key(key))
    return translated if not translated.startswith("display_avb.key.") else key


def format_bytes(size_str: str) -> str:
    try:
        size = int(size_str)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"
    except (ValueError, TypeError):
        return size_str


def print_props(props: Dict[str, str], indent: int = 4, simplify=False):
    if not props:
        print(" " * indent + "`- " + t("display_avb.empty"))
        return

    items = list(props.items())
    for i, (key, value) in enumerate(items):
        is_last = (i == len(items) - 1)
        prefix = "`- " if is_last else "|- "

        simplified_key = key
        if simplify:
            if key.startswith("com.android.build."):
                simplified_key = key.replace("com.android.build.", "")
            elif key.startswith("com.android."):
                simplified_key = key.replace("com.android.", "")

        print(" " * indent + prefix + f"{simplified_key}: {value}")


def print_list_value(key: str, value: list, indent: int = 4):
    if not value:
        print(" " * indent + f"`- {key}: {t('display_avb.empty')}")
        return

    print(" " * indent + f"|- {key}:")
    for i, item in enumerate(value):
        is_last = (i == len(value) - 1)
        prefix = "`- " if is_last else "|- "
        print(" " * (indent + 4) + prefix + str(item))


def print_partition(partition_name: str, partition_data: Dict[str, Any]):
    print("\n" + t("display_avb.partition_title", partition=partition_name.upper()))
    print("=" * 60)

    keys = sorted(partition_data.keys())
    props = partition_data.get("Props", {})

    for key in keys:
        if key == "Props":
            continue

        value = partition_data[key]
        display_key = get_display_key_name(key)

        if key in ["Chain", "Chain partition key", "Hash", "Hashtree"]:
            print_list_value(display_key, value)
        elif key == "Image size":
            print(f"{display_key}: {value} ({format_bytes(value)})")
        elif isinstance(value, list):
            print(f"{display_key}: {', '.join(map(str, value))}")
        else:
            print(f"{display_key}: {value}")

    props_key = get_display_key_name("Props")
    if props:
        print(f"{props_key}:")
        print_props(props, indent=4)
    elif "vbmeta" not in partition_name:
        print(f"{props_key}: {t('display_avb.empty')}")


def entry(partitions=()):
    os.system("cls") if os.name == "nt" else os.system("clear")
    my_ui_utils = UIUtils.UIUtils()
    avb_data = load_avb_data()
    if avb_data == {}:
        my_ui_utils.press_enter_to_continue(t("display_avb.no_config_info"))
        return

    print("=" * 80)
    print(t("display_avb.config_info_title"))
    print("=" * 80)

    if partitions:
        partition_order = list(partitions)
    else:
        my_config_parser = ConfigParser.ConfigParser()
        partition_order = my_config_parser.get_image_list() or [
            "vbmeta", "vbmeta_system", "boot", "init_boot", "vendor_boot",
            "recovery", "dtbo", "pvmfw"
        ]

    for partition in partition_order:
        if partition in avb_data:
            print_partition(partition, avb_data[partition])

    if partitions == ():
        for partition in avb_data:
            if partition not in partition_order:
                print_partition(partition, avb_data[partition])

    print("\n" + "=" * 80)
    my_ui_utils.press_enter_to_continue(t("display_avb.completed"))
