import BaseUI
import Core.ConfigManager as ConfigManager
from Core.Frontend.UIUtils import EnhancedFileSelectorUI as EnhancedFileSelectorUI


class ConfigLibManagerUI(BaseUI.BaseUI):

    def customized_init(self):
        self.TAG = "Config Manager"
        self.my_config_manager = ConfigManager.ConfigManager(self.my_logger)
        self.customized_function = {"M" : "Manage configs"}
        self.config_function = {"R" : "Rename",
                                "D" : "Delete",
                                "A" : "Activate",}

    def call_backend(self, function_name: str):
        self.my_logger.log("I", function_name + ", directly invoke selector.")
        config_list = self.my_config_manager.get_all_configs()
        my_selector = EnhancedFileSelectorUI("Select a config", config_list, False, self.my_logger, self.my_ui_utils)
        selected_config = my_selector.show()[0]
        available_functions = []
        for i in self.config_function:
            available_functions.append(self.config_function[i])
        my_selector = EnhancedFileSelectorUI("Options available for " + selected_config, available_functions, False, self.my_logger, self.my_ui_utils)
        selected_function = my_selector.show()[0]
        if selected_function == self.config_function["R"]:
            new_config_name = self.my_config_manager.get_new_config_name(selected_config, prompt="Config Rename")
            rename_result = self.my_config_manager.rename_config(selected_config, new_config_name)
            if rename_result:
                print("Successfully renamed " + selected_config + " to " + new_config_name)
            else:
                print("Failed to rename " + selected_config + " to " + new_config_name)
                self.my_ui_utils.message_on_fail()
            self.my_ui_utils.press_enter_to_continue()
        elif selected_function == self.config_function["D"]:
            if self.my_ui_utils.confirm_operation("DANGER: THIS OPERATION CANNOT BE UNDONE!"):
                remove_result = self.my_config_manager.remove_single_config(selected_config)
                if remove_result:
                    print("Successfully removed " + selected_config)
                else:
                    print("Failed to remove " + selected_config)
                    self.my_ui_utils.message_on_fail()
            else:
                self.my_ui_utils.message_on_cancel()
            self.my_ui_utils.press_enter_to_continue()
        elif selected_function == self.config_function["A"]:
            if self.my_ui_utils.confirm_operation("Sure to activate this config (%s)? If so, current config will be override." % selected_config):
                activate_result = self.my_config_manager.set_config_active(selected_config)
                if activate_result:
                    print("Successfully activated " + selected_config)
                else:
                    print("Failed to activate " + selected_config)
                    self.my_ui_utils.message_on_fail()
            else:
                self.my_ui_utils.message_on_cancel()
            self.my_ui_utils.press_enter_to_continue()
