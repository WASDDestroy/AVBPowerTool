import os

import BaseUI
import Core.ConfigManager as ConfigManager
from Core.Localization import t
from Frontend.UIUtils import EnhancedFileSelectorUI as EnhancedFileSelectorUI


class ImportConfigUI(BaseUI.BaseUI):

    def customized_init(self):
        self.TAG = "ImportConfigUI"
        self.customized_function = {"I" : {"id": "action:import_configs", "label": t("import.action.import_configs")}}
        # noinspection PyAttributeOutsideInit
        self.myConfigManager = ConfigManager.ConfigManager()

    def call_backend(self, function_name: str):
        if function_name == self.customized_function["I"]["id"]:
            self.__handle_import_logic()

    def __handle_import_logic(self):
        file_can_be_selected = []
        for i in os.listdir(os.getcwd()):
            if i.endswith(".zip"):
                file_can_be_selected.append(i)
        my_file_selector = EnhancedFileSelectorUI(t("import.selector_title"), file_can_be_selected, True)
        import_files = my_file_selector.show()
        self._my_logger.log("I", "Import files: %s" % str(import_files), self.TAG)
        if len(import_files) == 0:
            self.my_ui_utils.message_on_cancel(t("ui.no_option_selected"))
            self.my_ui_utils.press_enter_to_continue()
            return
        for file_name in import_files:
            archive_type = self.myConfigManager.check_config_type(
                file_name=file_name)
            self._my_logger.log("I", "Archive type is %s" % archive_type, self.TAG)
            if archive_type == "SINGLE":
                try:
                    self.myConfigManager.import_single_config(
                        import_from_file_name=file_name)
                    print(t("import.single_success", file=file_name))
                except Exception as e:
                    self._my_logger.log("W", e, self.TAG)
                    print(t("import.failed"))
                    self.my_ui_utils.press_enter_to_continue()
            elif archive_type == "BATCH":
                try:
                    self.myConfigManager.batch_import_config(
                        import_from_file_name=file_name)
                    print(t("import.batch_success"))
                except Exception as e:
                    self._my_logger.log("W", e, self.TAG)
                    print(t("import.failed"))
                    self.my_ui_utils.press_enter_to_continue()
            else:
                print(t("import.invalid_archive_press_enter"))
                self.my_ui_utils.press_enter_to_continue()
        print(t("import.completed"))
        self.my_ui_utils.press_enter_to_continue()
