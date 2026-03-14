import Core.DynamicImportUtils as DynamicImportUtils
import Core.Frontend.UIUtils as UIUtils
import Core.LogUtils as LogUtils
import Core.NavigationEngine as NavigationEngine
from Core.Frontend.UIUtils import EnhancedFileSelectorUI

class BaseUI:

    def __init__(self, logger=None, goto_node="", navigation_engine=None, ui_utils = None) -> None:
        self.TAG = self.__class__.__name__
        self.node_function = {}
        self.customized_function = {}  # "Press Key" : "Function Name"
        self.my_logger = logger or LogUtils.LogUtils(should_attach_time=True)
        self.my_importer = DynamicImportUtils.DynamicImportUtils(logger=self.my_logger)
        self.my_navigation_engine = navigation_engine or NavigationEngine.NavigationEngine(
            self.my_logger)  # type: ignore
        self.my_ui_utils = ui_utils or UIUtils.UIUtils(logger)
        self.my_logger.log("D", "Currently at: " +
                          self.my_navigation_engine.currentNodeName, self.TAG)
        self.my_logger.log("D", "Desired node: " + goto_node, self.TAG)
        if goto_node and goto_node != self.my_navigation_engine.currentFileName:
            self.my_navigation_engine.goto_node(goto_node)
        self.customized_init()
        self.get_node_functions()
        self.my_logger.log("I", "UI instance %s created." %
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
        next_nodes_dict = self.my_navigation_engine.get_next_node_names()
        for i in next_nodes_dict:
            self.node_function[i] = next_nodes_dict[i]
        if self.my_navigation_engine.currentDic["Previous"] == "END":
            self.node_function["E"] = "Exit"
        else:
            self.node_function["B"] = "Back to upper level"

    def handle_back_and_exit(self, function_name):
        if "back" in function_name.lower():
            self.my_logger.log("I", "Back to upper level.", self.TAG)
            self.my_navigation_engine.go_to_upper_level()
            return True
        if function_name == "Exit":
            print("Exiting.")
            self.my_logger.log("I", "Exit on UI request.", self.TAG)
            exit()
        return False

    def call_backend(self, function_name: str):
        self.handle_back_and_exit(function_name)
        raise NotImplementedError(
            "Unimplemented method callBackEnd." + self.TAG)

    def _in_development_placeholder(self):
        print("Function in development.")
        self.my_ui_utils.press_enter_to_continue()

    def confirm_operation(self, prompt="Confirm operation?") -> bool:
        return self.my_ui_utils.confirm_operation(prompt)

    def show_ui(self):
        self.my_ui_utils.clear_screen()
        available_functions = []
        for i in self.node_function:
            available_functions.append(self.node_function[i])
        my_selector = EnhancedFileSelectorUI(self.my_navigation_engine.currentNodeName,
                                             available_functions,
                                             False,
                                             self.my_logger,
                                             self.my_ui_utils,
                                             True,
                                             False)
        return my_selector.show(True if self.my_navigation_engine.currentNodeName == "AVBPowerTool Home Page" else False,
                                True)[0]

    def handle_interaction_logic(self, function_name):
        self.my_logger.log("T", "Function name: " + function_name, self.TAG)
        if self.handle_back_and_exit(function_name):
            self.my_logger.log("T", "Back to upper level.", self.TAG)
            return True
        # Check whether function is in next node
        if self.my_navigation_engine.currentDic["Next"][0] != "END":
            self.my_logger.log(
                "T", "Current node has subnodes, traverse them.", self.TAG)
            for i in self.my_navigation_engine.currentDic["Next"]:
                self.my_logger.log(
                    "T", "Traversing, current: " + i, self.TAG)
                self.my_navigation_engine.goto_node(i)
                self.my_navigation_engine.refresh_node_info()
                if self.my_navigation_engine.currentDic["Name"] == function_name:
                    # Found function in one of the next node, dynamically import it and execute entry
                    module_name = self.my_navigation_engine.currentDic["Frontend"].rstrip(
                        ".py")
                    self.my_logger.log(
                        "I", "Navigate to: " + module_name, self.TAG)
                    my_object = self.my_importer.create_frontend_instance(self.my_importer.import_front_end_module(module_name),
                                                                          module_name,
                                                                          self.my_logger,
                                                                          i,
                                                                          self.my_navigation_engine,
                                                                          self.my_ui_utils)
                    self.my_logger.log("I", "Successfully created new UI instance from module %s" % module_name, self.TAG)
                    my_object.entry(
                        navigation_engine=self.my_navigation_engine)
                    break
                else:
                    self.my_navigation_engine.go_to_upper_level()
            else:
                # If the loop ends normally, call functions in current node.
                self.call_backend(function_name)
                return None
        else:
            self.my_logger.log(
                "T", "Current node does not contain subnodes, directly call function: " + function_name, self.TAG)
            self.call_backend(function_name)
            return None

    def entry(self, navigation_engine=None):
        if navigation_engine is not None:
            self.my_logger.log("D", "Use provided navigation engine.", self.TAG)
            self.my_navigation_engine = navigation_engine
        else:
            self.my_logger.log("D", "Use navigation engine created by the instance.", self.TAG)
        while 1:
            self.my_logger.log("D", "Currently at: " +
                              self.my_navigation_engine.currentNodeName, self.TAG)
            function_name = self.show_ui()
            if self.handle_interaction_logic(function_name):
                break


if __name__ == "__main__":
    myBaseUI = BaseUI()
    myBaseUI.entry()
