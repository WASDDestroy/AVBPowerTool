import os

import BaseUI
from Core.Frontend.UIUtils import EnhancedFileSelectorUI


class ExportConfigUI(BaseUI.BaseUI):

    def customized_init(self):
        self.TAG = "ExportConfigUI"
        # noinspection PyAttributeOutsideInit
        self.customized_function = {
            "E": "Export a selected config",
        }
        # noinspection PyAttributeOutsideInit
        self.myConfigManager = self.my_importer.create_instance(self.my_importer.import_module("ConfigManager"),
                                                              "ConfigManager",
                                                                self.my_logger)

    def call_backend(self, function_name: str):
        if function_name == self.customized_function["E"]:
            self.__handle_single_export_logic()

    def __handle_single_export_logic(self):
        file_can_be_selected = []
        for i in os.listdir(os.path.join(os.getcwd(), "Configs")):
            file_can_be_selected.append(i)
        my_file_selector = EnhancedFileSelectorUI(title="Select a Config", items=file_can_be_selected,
                                                  multi_select=False, logger=self.my_logger)
        config_name = my_file_selector.show()[0]
        if config_name is None:
            print("User cancelled operation.")
        else:
            try:
                result = self.myConfigManager.export_single_config(
                    export_config_folder_name=config_name)
                if result:
                    print("Successfully exported selected config %s to root directory as an archive." % (
                        config_name))
                else:
                    print("Failed to export config!")
            except FileNotFoundError:
                print("Config folder not found!")
                self.my_logger.log("W",
                                  "Config folder not found! Check system settings because config is already guaranteed exist in previous steps.",
                                  self.TAG)
        self.my_ui_utils.press_enter_to_continue()
