import os
import time

import BaseUI
from Core.GlobalConfigUtils import GlobalConfigInfo, GlobalConfigUtils
from Core.Localization import Localization, StringResourceChecker, t
from Frontend.UIUtils import EnhancedFileSelectorUI


class SettingsUI(BaseUI.BaseUI):

    BOOLEAN_VALUES = ("1", "0")
    LOG_LEVELS = ("T", "D", "I", "W", "E", "F", "O")
    LIMITED_CHOICE_LABEL_KEYS = {
        "language": {
            "en": "settings.option.language.en",
            "zh": "settings.option.language.zh",
            "me": "settings.option.language.me",
        },
        "log_level": {
            "T": "settings.option.log_level.T",
            "D": "settings.option.log_level.D",
            "I": "settings.option.log_level.I",
            "W": "settings.option.log_level.W",
            "E": "settings.option.log_level.E",
            "F": "settings.option.log_level.F",
            "O": "settings.option.log_level.O",
        },
    }
    READ_ONLY_KEYS = ("tool_version", "navigation_map_dir", "frontend_dir", "logo_path", "resource_dir")
    PATH_KEYS = (
        "navigation_map_dir",
        "frontend_dir",
        "logo_path",
        "log_destination",
        "bin_dir",
        "resource_dir",
    )

    def customized_init(self):
        self.TAG = "SettingsUI"
        self.config_path = os.path.join(os.getcwd(), "GlobalConfig.cfg")
        self.config_utils = GlobalConfigUtils()
        self.global_config = GlobalConfigInfo()
        self.customized_function = {
            "E": {"id": "action:settings_edit", "label": t("settings.action.edit")},
            "V": {"id": "action:settings_view", "label": t("settings.action.view")},
            "L": {"id": "action:settings_check_l10n", "label": t("settings.action.check_l10n")},
        }

    def call_backend(self, action_id: str):
        if action_id == self.customized_function["E"]["id"]:
            self.__edit_setting()
        elif action_id == self.customized_function["V"]["id"]:
            self.__show_settings()
        elif action_id == self.customized_function["L"]["id"]:
            self.__show_missing_l10n()
        self.my_ui_utils.press_enter_to_continue()

    def __load_config(self):
        return self.config_utils.parse_key_value_file(self.config_path)

    def __save_config(self, config_dict):
        self.config_utils.save_config_to_file(self.config_path, config_dict)
        self.global_config.clear_values()
        self.global_config.set_values_by_dict(config_dict)
        Localization().initialize(
            resources_dir=self.global_config.get_value("resource_dir") or "./Resources",
            language=self.global_config.get_value("language") or "en")

    def __show_settings(self):
        config_dict = self.__load_config()
        print("=" * 80)
        print(t("settings.current_settings"))
        print("=" * 80)
        for key, value in config_dict.items():
            print(f"{key}={value}")

    def __edit_setting(self):
        config_dict = self.__load_config()
        selectable_keys = list(config_dict.keys())
        selector_items = []
        for key in selectable_keys:
            value = config_dict[key]
            readonly = " " + t("settings.read_only_suffix") if key in self.READ_ONLY_KEYS else ""
            selector_items.append(f"{key} = {value}{readonly}")

        selector = EnhancedFileSelectorUI(t("settings.select_setting"), selector_items, False, True, True)
        selected = selector.show(allow_long_item=True)
        if not selected:
            self.my_ui_utils.message_on_cancel(t("ui.no_option_selected"))
            return

        selected_index = selector_items.index(selected[0])
        selected_key = selectable_keys[selected_index]
        if selected_key in self.READ_ONLY_KEYS:
            print(t("settings.read_only_message", config_key=selected_key))
            return

        old_value = config_dict[selected_key]
        new_value = self.__get_new_value(selected_key, old_value)
        if new_value is None:
            self.my_ui_utils.message_on_cancel()
            return

        config_dict[selected_key] = new_value
        self.__save_config(config_dict)
        print(t("settings.saved", config_key=selected_key, old=old_value, new=new_value))
        if selected_key in ("language", "resource_dir", "allow_clear_screen"):
            print(t("settings.restart_notice"))

    def __get_new_value(self, key, old_value):
        if old_value in self.BOOLEAN_VALUES and key not in ("log_flush_threshold",):
            return self.__select_from_options(
                t("settings.select_boolean", config_key=key),
                (("1", t("settings.enabled")), ("0", t("settings.disabled"))),
                old_value)

        if key == "log_level":
            return self.__select_from_options(
                t("settings.select_log_level"),
                self.__build_limited_choice_options(key, self.LOG_LEVELS),
                old_value)

        if key == "language":
            languages = self.__get_available_languages()
            return self.__select_from_options(
                t("settings.select_language"),
                self.__build_limited_choice_options(key, languages),
                old_value)

        if key == "log_flush_threshold":
            return self.__input_validated_value(key, old_value, str.isdecimal)

        return input(t("settings.enter_value", config_key=key, old=old_value))

    @classmethod
    def __build_limited_choice_options(cls, key, values):
        return tuple((value, cls.__get_limited_choice_label(key, value)) for value in values)

    @classmethod
    def __get_limited_choice_label(cls, key, value):
        resource_key = cls.LIMITED_CHOICE_LABEL_KEYS.get(key, {}).get(value)
        if not resource_key:
            return value
        label = t(resource_key)
        return label if label != resource_key else value

    @staticmethod
    def __select_from_options(title, options, old_value):
        labels = []
        values = []
        for value, label in options:
            current_suffix = " " + t("settings.current_suffix") if value == old_value else ""
            labels.append(f"{label} ({value}){current_suffix}")
            values.append(value)
        selector = EnhancedFileSelectorUI(title, labels, False, True, True)
        selected = selector.show(allow_long_item=True)
        if not selected:
            return None
        return values[labels.index(selected[0])]

    def __input_validated_value(self, key, old_value, validator):
        while True:
            new_value = input(t("settings.enter_value", config_key=key, old=old_value))
            if new_value == "":
                return None
            if validator(new_value):
                return new_value
            print(t("settings.invalid_value"))

    def __get_available_languages(self):
        resource_dir = self.global_config.get_value("resource_dir") or "./Resources"
        languages = ["en"]
        if os.path.isdir(resource_dir):
            for item in os.listdir(resource_dir):
                if item.startswith("values-") and os.path.isdir(os.path.join(resource_dir, item)):
                    languages.append(item[len("values-"):])
        return sorted(set(languages))

    def __show_missing_l10n(self):
        missing_strings = StringResourceChecker.get_missing_strings()
        language = self.global_config.get_value("language") or "en"
        if not missing_strings:
            print(t("cli.check_l10n.no_missing", language=language))
            return
        print(t("cli.check_l10n.missing_header", language=language, count=len(missing_strings)))
        for key in sorted(missing_strings.keys()):
            print(StringResourceChecker.build_xml_string_entry(key, missing_strings[key]))
