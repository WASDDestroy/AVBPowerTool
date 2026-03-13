import os

import BaseUI
import Core.ConfigManager as ConfigManager
from Core.Frontend.UIUtils import EnhancedFileSelectorUI as EnhancedFileSelectorUI


class ImportConfigUI(BaseUI.BaseUI):

    def customized_init(self):
        self.TAG = "ImportConfigUI"
        self.customized_function = {"I" : "Import single config archive",
                                    "T" : "Batch import",}
        # noinspection PyAttributeOutsideInit
        self.myConfigManager = ConfigManager.ConfigManager(
            logger=self.my_logger)

    def call_backend(self, function_name: str):
        if function_name == self.customized_function["I"]:
            self.__handle_single_import_logic()

    def __handle_single_import_logic(self):
        file_can_be_selected = []
        for i in os.listdir(os.getcwd()):
            if i.endswith(".zip"):
                file_can_be_selected.append(i)
        my_file_selector = EnhancedFileSelectorUI(title="Select a Config", items=file_can_be_selected, multi_select=False, logger=self.my_logger)
        import_filename = my_file_selector.show()[0]
        if import_filename is None:
            print("Cancelled.")
            return
        archive_type = self.myConfigManager.check_config_type(
            file_name=import_filename)
        if archive_type == "SINGLE":
            try:
                self.myConfigManager.import_single_config(
                    import_from_file_name=import_filename)
                print("Successfully imported config.")
            except Exception as e:
                self.my_logger.log("W", e, self.TAG)
                print("Import failed!")
            self.my_ui_utils.press_enter_to_continue()
        elif archive_type == "BATCH":
            try:
                self.myConfigManager.batch_import_config(
                    import_from_file_name=import_filename)
                print("Successfully imported config.")
            except Exception as e:
                self.my_logger.log("W", e, self.TAG)
                print("Import failed!")
            self.my_ui_utils.press_enter_to_continue()
        else:
            print("Invalid archive file.")
            self.my_ui_utils.press_enter_to_continue()
