import os
import time

import BaseUI
from Core.Frontend.UIUtils import EnhancedFileSelectorUI


class ExportConfigUI(BaseUI.BaseUI):

    def customized_init(self):
        self.TAG = "ExportConfigUI"
        # noinspection PyAttributeOutsideInit
        self.customized_function = {
            "E": "Export selected config(s)",
        }
        # noinspection PyAttributeOutsideInit
        self.myConfigManager = self.my_importer.create_instance(self.my_importer.import_module("ConfigManager"),
                                                              "ConfigManager",
                                                                self.my_logger)

    def call_backend(self, function_name: str):
        if function_name == self.customized_function["E"]:
            self.__handle_export_logic()

    def __handle_export_logic(self):
        file_can_be_selected = []
        for i in os.listdir(os.path.join(os.getcwd(), "Configs")):
            file_can_be_selected.append(i)
        my_file_selector = EnhancedFileSelectorUI(title="Select a Config", items=file_can_be_selected,
                                                  multi_select=True, logger=self.my_logger)
        config_list = my_file_selector.show()
        if len(config_list) == 0:
            print("User cancelled operation.")
            return
        elif len(config_list) > 1:
            if self.confirm_operation("Should export these configs as sparse archives?"):
                for i in config_list:
                    self.__call_export_backend(i, True)
            else:
                self.__call_export_backend(sparse=False, config_list=config_list)
        else:
            config_name = config_list[0]
            self.__call_export_backend(config_name, True)


        self.my_ui_utils.press_enter_to_continue()

    def __call_export_backend(self, config_name="", sparse=False, config_list=None):
        try:
            export_to_file_name = input("Enter the name of exported archive, keep it empty to use the name of config: ")
            if not export_to_file_name.endswith(".zip"):
                export_to_file_name += ".zip"
            if sparse:
                result = self.myConfigManager.export_single_config(
                    export_config_folder_name=config_name, export_to_file_name=export_to_file_name or config_name + ".zip")
            else:
                result = self.myConfigManager.batch_export_config(export_to_file_name=export_to_file_name or
                                                                                      "AVBPowerTool_Batch_Export_"
                                                                                      + time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
                                                                                      + ".zip",
                                                                  selected_configs=config_list)
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
