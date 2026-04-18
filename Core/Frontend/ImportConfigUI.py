import os

import BaseUI
import Core.ConfigManager as ConfigManager
from Core.Frontend.UIUtils import EnhancedFileSelectorUI as EnhancedFileSelectorUI


class ImportConfigUI(BaseUI.BaseUI):

    def customized_init(self):
        self.TAG = "ImportConfigUI"
        self.customized_function = {"I" : "Import config(s)"}
        # noinspection PyAttributeOutsideInit
        self.myConfigManager = ConfigManager.ConfigManager()

    def call_backend(self, function_name: str):
        if function_name == self.customized_function["I"]:
            self.__handle_import_logic()

    def __handle_import_logic(self):
        file_can_be_selected = []
        for i in os.listdir(os.getcwd()):
            if i.endswith(".zip"):
                file_can_be_selected.append(i)
        my_file_selector = EnhancedFileSelectorUI("Select a Config Archive to Import", file_can_be_selected, True)
        import_files = my_file_selector.show()
        self.my_logger.log("I", "Import files: %s" % str(import_files), self.TAG)
        if len(import_files) == 0:
            self.my_ui_utils.message_on_cancel()
            return
        for file_name in import_files:
            archive_type = self.myConfigManager.check_config_type(
                file_name=file_name)
            self.my_logger.log("I", "Archive type is %s" % archive_type, self.TAG)
            if archive_type == "SINGLE":
                try:
                    self.myConfigManager.import_single_config(
                        import_from_file_name=file_name)
                    print("Successfully imported single config archive %s." % file_name)
                except Exception as e:
                    self.my_logger.log("W", e, self.TAG)
                    print("Import failed!")
                    self.my_ui_utils.press_enter_to_continue()
            elif archive_type == "BATCH":
                try:
                    self.myConfigManager.batch_import_config(
                        import_from_file_name=file_name)
                    print("Successfully imported config.")
                except Exception as e:
                    self.my_logger.log("W", e, self.TAG)
                    print("Import failed!")
                    self.my_ui_utils.press_enter_to_continue()
            else:
                print("Invalid archive file. Press Enter to continue.")
                self.my_ui_utils.press_enter_to_continue()
        print("Import process completed.")
        self.my_ui_utils.press_enter_to_continue()