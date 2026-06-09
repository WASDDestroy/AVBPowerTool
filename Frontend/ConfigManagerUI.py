import BaseUI
from Frontend.UIUtils import EnhancedFileSelectorUI
from Core.Localization import t


# noinspection PyAttributeOutsideInit
class ConfigManagerUI(BaseUI.BaseUI):

    def customized_init(self):
        self.TAG = "ConfigManagerUI"
        # noinspection PyAttributeOutsideInit
        self.configManagerModule = self._my_importer.import_module(
            "ConfigManager.py")
        # noinspection PyAttributeOutsideInit
        self.customized_function = {"S": {"id": "action:activate_config", "label": t("config.action.activate")},
                                   "P": {"id": "action:save_config", "label": t("config.action.save_persistent")},
                                    "H": {"id": "action:config_help", "label": t("config.action.help")}}

    def call_backend(self, function_name: str):
        function_name_tuple = (self.customized_function["S"]["id"],
                             self.customized_function["P"]["id"],
                               self.customized_function["H"]["id"])
        self.myConfigManager = self._my_importer.create_instance(self.configManagerModule, "ConfigManager")
        if function_name == function_name_tuple[0]:
            config_names = self.myConfigManager.get_all_configs()
            my_selector = EnhancedFileSelectorUI(t("config.selector_activate"), config_names, False)
            config_to_active_list = my_selector.show()
            if len(config_to_active_list) > 0:
                config_to_active = config_to_active_list[0]
            else:
                self.my_ui_utils.message_on_cancel(t("ui.no_option_selected"))
                self.my_ui_utils.press_enter_to_continue()
                return
            if config_to_active:
                if self.myConfigManager.set_config_active(config_to_active):
                    print(t("config.activate_success", config=config_to_active))
                    print(t("config.active_removed"))
                else:
                    print(t("config.activate_failed", config=config_to_active))
                    self.my_ui_utils.message_on_fail()
            else:
                self.my_ui_utils.message_on_cancel()
        elif function_name == function_name_tuple[1]:
            config_name = input(t("config.enter_new_name"))
            result = self.myConfigManager.save_as_persistent_config(config_name)
            if result:
                print(t("config.save_success", config=config_name))
            else:
                print(t("config.save_failed"))
                self.my_ui_utils.message_on_fail()
        elif function_name == function_name_tuple[2]:
            self.get_help_message()
        self.my_ui_utils.press_enter_to_continue()

    @staticmethod
    def get_help_message():
        print(t("config.help_message"))
