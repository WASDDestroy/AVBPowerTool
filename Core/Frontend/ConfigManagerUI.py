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
                                   "P": "Save current config as a persistent one",
                                    "H": "Help"}

    def call_backend(self, function_name: str):
        function_name_tuple = ("Set a config active",
                             "Save current config as a persistent one",
                               "Help")
        self.myConfigManager = self.my_importer.create_instance(self.configManagerModule, "ConfigManager")
        if function_name == function_name_tuple[0]:
            config_names = self.myConfigManager.get_all_configs()
            my_selector = EnhancedFileSelectorUI("Select a Config to Activate", config_names, False)
            config_to_active_list = my_selector.show()
            if len(config_to_active_list) > 0:
                config_to_active = config_to_active_list[0]
            else:
                self.my_ui_utils.message_on_cancel("No option selected, cancelling.")
                self.my_ui_utils.press_enter_to_continue()
                return
            if config_to_active:
                if self.myConfigManager.set_config_active(config_to_active):
                    print("Successfully switched active config to", config_to_active)
                    print("Old \"active\" config has been removed.")
                else:
                    print("Failed to set active config to", config_to_active)
                    self.my_ui_utils.message_on_fail()
            else:
                self.my_ui_utils.message_on_cancel()
        elif function_name == function_name_tuple[1]:
            config_name = input("Enter the name of your new config: ")
            result = self.myConfigManager.save_as_persistent_config(config_name)
            if result:
                print("Successfully saved \"current\" config to persistent file, name: %s." % config_name)
            else:
                print("Failed to save \"current\" config to persistent file.")
                self.my_ui_utils.message_on_fail()
        elif function_name == function_name_tuple[2]:
            self.get_help_message()
        self.my_ui_utils.press_enter_to_continue()

    @staticmethod
    def get_help_message():
        help_message = """
        Configs are stored under folder \"Configs\" with corresponding key files under directory \"Key\".
        To create a config, create two folders named with your config under Config and Key folder respectively.
        Then, write a file named imageList.txt under folder in Config directory, one partition name for a line.
        As for Key folder, place your .pem file under it and program will do the rest.
        
        Also, you can open folder ./Core/currentConfigs and ./Core/currentKeySet to do the same thing with interactive
        guide. However, directly access to core folders may result in unexpected behavior.
        """
        print(help_message)