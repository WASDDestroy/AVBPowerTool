import os
import time

import BaseUI
from Core.Localization import t
from Frontend.UIUtils import EnhancedFileSelectorUI


class ExportConfigUI(BaseUI.BaseUI):

    def customized_init(self):
        self.TAG = "ExportConfigUI"
        # noinspection PyAttributeOutsideInit
        self.customized_function = {
            "E": {"id": "action:export_configs", "label": t("export.action.export_configs")},
        }
        # noinspection PyAttributeOutsideInit
        self.myConfigManager = self._my_importer.create_instance(self._my_importer.import_module("ConfigManager"),
                                                                "ConfigManager")

    def call_backend(self, function_name: str):
        if function_name == self.customized_function["E"]["id"]:
            self.__handle_export_logic()

    def __handle_export_logic(self):
        file_can_be_selected = []
        for i in os.listdir(os.path.join(os.getcwd(), "Configs")):
            file_can_be_selected.append(i)
        my_file_selector = EnhancedFileSelectorUI(t("export.selector_config"), file_can_be_selected, True)
        config_list = my_file_selector.show()
        export_result = False
        if len(config_list) == 0:
            self.my_ui_utils.message_on_cancel()
            self.my_ui_utils.press_enter_to_continue()
            return
        elif len(config_list) > 1:
            if self.confirm_operation(t("export.sparse_archives_confirm")):
                for i in config_list:
                    export_result = self.__call_export_backend(i, True)
            else:
                export_result = self.__call_export_backend(sparse=False, config_list=config_list)
        else:
            config_name = config_list[0]
            export_result = self.__call_export_backend(config_name, True)
        if export_result:
            print(t("export.success"))
            print(t("export.exported_configs"))
            for config_name in config_list:
                print(config_name)
        else:
            print(t("export.failed"))

        self.my_ui_utils.press_enter_to_continue()

    def __call_export_backend(self, config_name="", sparse=False, config_list=None):
        try:
            export_to_file_name = input(t("export.enter_archive_name"))
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
            self._my_logger.log("W",
                               "Config folder not found! Check system settings because config is already guaranteed exist in previous steps.",
                                self.TAG)
            return False
