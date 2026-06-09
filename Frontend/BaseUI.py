import Core.DynamicImportUtils as DynamicImportUtils
import Frontend.UIUtils as UIUtils
import Core.LogUtils as LogUtils
import Core.NavigationEngine as NavigationEngine
import Core.GlobalConfigUtils as GlobalConfigUtils
from Core.Localization import t
from Frontend.UIUtils import EnhancedFileSelectorUI

class BaseUI:

    def __init__(self, goto_node="") -> None:
        self.TAG = self.__class__.__name__
        self.node_function = {}
        self.customized_function = {}  # "Press Key" : {"id": "...", "label": "..."}
        self._my_logger = LogUtils.LogUtils()
        self._my_importer = DynamicImportUtils.DynamicImportUtils()
        __global_config_info = GlobalConfigUtils.GlobalConfigInfo()
        self._my_navigation_engine = NavigationEngine.NavigationEngine(__global_config_info.get_value("navigation_map_dir"))  # type: ignore
        self.my_ui_utils = UIUtils.UIUtils()
        self._my_logger.log("D", "Currently at: " +
                            self._my_navigation_engine.currentNodeName, self.TAG)
        self._my_logger.log("D", "Desired node: " + goto_node, self.TAG)
        if goto_node and goto_node != self._my_navigation_engine.currentFileName:
            self._my_navigation_engine.goto_node(goto_node)
        self.customized_init()
        self.get_node_functions()
        self._my_logger.log("I", "UI instance %s created." %
                            self.TAG, self.TAG)

    def customized_init(self):
        """
        Store customized initialization process of your UI class.
        """
        pass

    def get_node_functions(self):
        # Node function = Next nodes + Customized actions
        self.node_function = {}
        for i in self.customized_function:
            self.node_function[i] = self.customized_function[i]
        next_nodes_dict = self._my_navigation_engine.get_next_node_actions()
        for i in next_nodes_dict:
            self.node_function[i] = next_nodes_dict[i]
        if self._my_navigation_engine.currentDic["Previous"] == "END":
            self.node_function["E"] = {"id": "system:exit", "label": t("ui.exit")}
        else:
            self.node_function["B"] = {"id": "system:back", "label": t("ui.back")}

    def handle_back_and_exit(self, action_id):
        if action_id == "system:back":
            self._my_logger.log("I", "Back to upper level.", self.TAG)
            self._my_navigation_engine.go_to_upper_level()
            return True
        if action_id == "system:exit":
            print(t("ui.exiting"))
            self._my_logger.log("I", "Exit on UI request.", self.TAG)
            exit()
        return False

    def call_backend(self, action_id: str):
        self.handle_back_and_exit(action_id)
        raise NotImplementedError(
            "Unimplemented method callBackEnd." + self.TAG)

    def _in_development_placeholder(self):
        print(t("ui.in_development"))
        self.my_ui_utils.press_enter_to_continue()

    def confirm_operation(self, prompt=None) -> bool:
        return self.my_ui_utils.confirm_operation(prompt)

    def show_ui(self):
        self.my_ui_utils.clear_screen()
        available_entries = []
        for key in self.node_function:
            available_entries.append(self.node_function[key])
        available_labels = [entry["label"] if isinstance(entry, dict) else str(entry) for entry in available_entries]
        my_selector = EnhancedFileSelectorUI(self._my_navigation_engine.currentNodeName, available_labels, False,
                                             True, False)
        selected_label = my_selector.show(True if self._my_navigation_engine.currentNodeId == "home" else False,
                                          True)[0]
        selected_index = available_labels.index(selected_label)
        selected_entry = available_entries[selected_index]
        return selected_entry["id"] if isinstance(selected_entry, dict) else selected_label

    def handle_interaction_logic(self, action_id):
        self._my_logger.log("T", "Action id: " + action_id, self.TAG)
        if self.handle_back_and_exit(action_id):
            self._my_logger.log("T", "Back to upper level.", self.TAG)
            return True
        if action_id.startswith("node:"):
            target_node_id = action_id.split(":", 1)[1]
        else:
            target_node_id = None

        if self._my_navigation_engine.currentDic["Next"][0] != "END":
            self._my_logger.log(
                "T", "Current node has subnodes, traverse them.", self.TAG)
            for i in self._my_navigation_engine.currentDic["Next"]:
                self._my_logger.log(
                    "T", "Traversing, current: " + i, self.TAG)
                self._my_navigation_engine.goto_node(i)
                self._my_navigation_engine.refresh_node_info()
                if self._my_navigation_engine.currentNodeId == target_node_id:
                    # Found function in one of the next node, dynamically import it and execute entry
                    if self._my_navigation_engine.currentDic["Frontend"].endswith(".py"):
                        module_name = self._my_navigation_engine.currentDic["Frontend"][:-3]
                    else:
                        module_name = self._my_navigation_engine.currentDic["Frontend"]
                    self._my_logger.log(
                        "I", "Navigate to: " + module_name, self.TAG)
                    my_object = self._my_importer.create_frontend_instance(
                        self._my_importer.import_front_end_module(module_name), module_name, i)
                    self._my_logger.log("I", "Successfully created new UI instance from module %s" % module_name, self.TAG)
                    my_object.entry()
                    break
                else:
                    self._my_navigation_engine.go_to_upper_level()
            else:
                # If the loop ends normally, call functions in current node.
                self.call_backend(action_id)
                return None
        else:
            self._my_logger.log(
                "T", "Current node does not contain subnodes, directly call action: " + action_id, self.TAG)
            self.call_backend(action_id)
            return None

    def entry(self):
        while 1:
            self._my_logger.log("D", "Currently at: " +
                                self._my_navigation_engine.currentNodeName, self.TAG)
            function_name = self.show_ui()
            if self.handle_interaction_logic(function_name):
                break


if __name__ == "__main__":
    myBaseUI = BaseUI()
    myBaseUI.entry()
