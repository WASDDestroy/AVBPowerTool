import BaseUI
import Core.ConfigManager as ConfigManager
from Core.Localization import t
from Frontend.UIUtils import EnhancedFileSelectorUI as EnhancedFileSelectorUI


class ConfigLibManagerUI(BaseUI.BaseUI):

    def customized_init(self):
        self.TAG = "Config Manager"
        self.my_config_manager = ConfigManager.ConfigManager()
        self.customized_function = {"M" : {"id": "action:manage_configs", "label": t("config_lib.action.manage")}}
        self.config_function = {"R" : {"id": "action:rename_config", "label": t("config_lib.action.rename")},
                                "D" : {"id": "action:delete_config", "label": t("config_lib.action.delete")},
                                "A" : {"id": "action:activate_library_config", "label": t("config_lib.action.activate")},}

    def call_backend(self, function_name: str):
        self._my_logger.log("I", function_name + ", directly invoke selector.")
        config_list = self.my_config_manager.get_all_configs()
        my_selector = EnhancedFileSelectorUI(t("config_lib.selector_config"), config_list, False)
        selected_config_list = my_selector.show()
        if len(selected_config_list) > 0:
            selected_config = selected_config_list[0]
        else:
            self.my_ui_utils.message_on_cancel(t("ui.no_option_selected"))
            self.my_ui_utils.press_enter_to_continue()
            return
        available_functions = []
        for i in self.config_function:
            available_functions.append(self.config_function[i]["label"])
        my_selector = EnhancedFileSelectorUI(t("config_lib.options_for", config=selected_config), available_functions, False)
        selected_function_list = my_selector.show()
        if len(selected_function_list) > 0:
            selected_function_label = selected_function_list[0]
            selected_function = None
            for key in self.config_function:
                if self.config_function[key]["label"] == selected_function_label:
                    selected_function = self.config_function[key]["id"]
                    break
        else:
            self.my_ui_utils.message_on_cancel(t("ui.no_option_selected"))
            self.my_ui_utils.press_enter_to_continue()
            return
        if selected_function == self.config_function["R"]["id"]:
            new_config_name = self.my_config_manager.get_new_config_name(selected_config, prompt=t("config_lib.rename_prompt"))
            rename_result = self.my_config_manager.rename_config(selected_config, new_config_name)
            if rename_result:
                print(t("config_lib.rename_success", old=selected_config, new=new_config_name))
            else:
                print(t("config_lib.rename_failed", old=selected_config, new=new_config_name))
                self.my_ui_utils.message_on_fail()
            self.my_ui_utils.press_enter_to_continue()
        elif selected_function == self.config_function["D"]["id"]:
            if self.my_ui_utils.confirm_operation(t("config_lib.delete_danger")):
                remove_result = self.my_config_manager.remove_single_config(selected_config)
                if remove_result:
                    print(t("config_lib.remove_success", config=selected_config))
                else:
                    print(t("config_lib.remove_failed", config=selected_config))
                    self.my_ui_utils.message_on_fail()
            else:
                self.my_ui_utils.message_on_cancel()
            self.my_ui_utils.press_enter_to_continue()
        elif selected_function == self.config_function["A"]["id"]:
            if self.my_ui_utils.confirm_operation(t("config_lib.activate_confirm", config=selected_config)):
                activate_result = self.my_config_manager.set_config_active(selected_config)
                if activate_result:
                    print(t("config_lib.activate_success", config=selected_config))
                else:
                    print(t("config_lib.activate_failed", config=selected_config))
                    self.my_ui_utils.message_on_fail()
            else:
                self.my_ui_utils.message_on_cancel()
            self.my_ui_utils.press_enter_to_continue()
