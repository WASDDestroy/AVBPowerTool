import BaseUI


class ConfigManagerUI(BaseUI.BaseUI):

    def __init__(self, logger=None, goto_node="", navigation_engine=None):
        super().__init__(logger, goto_node, navigation_engine)
        self.myConfigManager = None

    def customized_init(self):
        self.TAG = "ConfigManagerUI"
        # noinspection PyAttributeOutsideInit
        self.configManagerModule = self.my_importer.import_module(
            "ConfigManager.py")
        # noinspection PyAttributeOutsideInit
        self.customizedFunction = {"S": "Set a config active",
                                   "P": "Save current config as a persistent one"}

    def call_backend(self, function_name: str):
        function_name_tuple = ("Config Library Manager",
                             "Set a config active",
                             "Save current config as a persistent one")
        self.myConfigManager = self.my_importer.create_instance(self.configManagerModule,
                                                              "ConfigManager",
                                                                self.my_logger)
        if function_name == function_name_tuple[0]:  # Manage
            self._in_development_placeholder()
        elif function_name == function_name_tuple[1]:
            config_to_active = self. my_ui_utils.select_config_ui()
            if config_to_active:
                self.myConfigManager.set_config_active(config_to_active)
            else:
                print("User cancelled operation.")
        elif function_name == function_name_tuple[2]:
            config_name = input("Enter the name of your new config: ")
            result = self.myConfigManager.save_as_persistent_config(config_name)
            if result:
                print("Success.")
            else:
                print("Failed.")
            self.my_ui_utils.press_enter_to_continue()
