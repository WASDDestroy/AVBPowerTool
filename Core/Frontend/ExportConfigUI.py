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
                                                                "ConfigManager")

    def call_backend(self, function_name: str):
        if function_name == self.customized_function["E"]:
            self.__handle_export_logic()

    def __handle_export_logic(self):
        file_can_be_selected = []
        for i in os.listdir(os.path.join(os.getcwd(), "Configs")):
            file_can_be_selected.append(i)
        my_file_selector = EnhancedFileSelectorUI("Select a Config", file_can_be_selected, True)
        config_list = my_file_selector.show()
        export_result = False
        if len(config_list) == 0:
            self.my_ui_utils.message_on_cancel()
            self.my_ui_utils.press_enter_to_continue()
            return
        elif len(config_list) > 1:
            if self.confirm_operation("Should export these configs as sparse archives?"):
                for i in config_list:
                    export_result = self.__call_export_backend(i, True)
            else:
                export_result = self.__call_export_backend(sparse=False, config_list=config_list)
        else:
            config_name = config_list[0]
            export_result = self.__call_export_backend(config_name, True)
        if export_result:
            print("Successfully exported selected config to root directory as an archive.")
            print("Config(s) exported:")
            for config_name in config_list:
                print(config_name)
        else:
            print("Failed to export config!")

        self.my_ui_utils.press_enter_to_continue()

    def __call_export_backend(self, config_name="", sparse=False, config_list=None):
        try:
            export_to_file_name = input("Enter the name of exported archive, keep it empty to use the name of config: ")
            if export_to_file_name == "":
                export_to_file_name = config_name
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
            return result
        except FileNotFoundError:
            self.my_logger.log("W",
                               "Config folder not found! Check system settings because config is already guaranteed exist in previous steps.",
                               self.TAG)
            return False