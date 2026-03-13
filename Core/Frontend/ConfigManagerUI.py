import BaseUI
from Core.Frontend.UIUtils import EnhancedFileSelectorUI


# noinspection PyAttributeOutsideInit
class ConfigManagerUI(BaseUI.BaseUI):

    def customized_init(self):
        self.TAG = "ConfigManagerUI"
        # noinspection PyAttributeOutsideInit
        self.configManagerModule = self.my_importer.import_module(
            "ConfigManager.py")
        # noinspection PyAttributeOutsideInit
        self.customized_function = {"S": "Set a config active",
                                   "P": "Save current config as a persistent one"}

    def call_backend(self, function_name: str):
        function_name_tuple = ("Set a config active",
                             "Save current config as a persistent one")
        self.myConfigManager = self.my_importer.create_instance(self.configManagerModule,
                                                              "ConfigManager",
                                                                self.my_logger)
        if function_name == function_name_tuple[0]:
            config_names = self.myConfigManager.get_all_configs()
            my_selector = EnhancedFileSelectorUI("Select a Config to Activate", config_names, False, self.my_logger)
            config_to_active = my_selector.show()[0]
            if config_to_active:
                if self.myConfigManager.set_config_active(config_to_active):
                    print("Successfully switched active config to", config_to_active)
                    print("Old \"active\" config has been removed.")
                else:
                    print("Failed to set active config to", config_to_active)
                    print("Please refer to log file for further information.")
                    print("Note: Exit tool first, then check log file, otherwise nothing will be shown in latest log.")
            else:
                print("User cancelled operation.")
            self.my_ui_utils.press_enter_to_continue()
        elif function_name == function_name_tuple[1]:
            config_name = input("Enter the name of your new config: ")
            result = self.myConfigManager.save_as_persistent_config(config_name)
            if result:
                print("Successfully saved \"current\" config to persistent file, name: %s." % config_name)
            else:
                print("Failed to save \"current\" config to persistent file.")
                print("Please refer to log file for further information.")
                print("Note: Exit tool, then check log file, otherwise nothing will be shown in latest log.")
            self.my_ui_utils.press_enter_to_continue()
