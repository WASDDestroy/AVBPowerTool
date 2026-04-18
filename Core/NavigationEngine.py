import os, json, time, copy, threading
import Core.LogUtils as LogUtils


class NavigationEngine:
    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if NavigationEngine._initialized:
            return
        with NavigationEngine._lock:
            if NavigationEngine._initialized:
                return
        self.currentNodeFrontEnd = None
        self.currentNodeSelections = None
        self.currentNodeNext = None
        self.currentNodePrev = None
        self.currentNodeDesc = None
        self.currentNodeName = None
        self.myLogger = LogUtils.LogUtils()
        self.ROOT_NODE = "main_navigation.json"
        self.TAG = "NavigationEngine"
        self.myLogger.log("I", "Navigation engine started.", self.TAG)
        self.navigatorDir = os.path.join(os.getcwd(), "Core", "Navigator")
        self.myLogger.log("I", "Navigation map root dir: " + self.navigatorDir, self.TAG)
        self.currentFileDir = os.path.join(self.navigatorDir, self.ROOT_NODE)
        self.currentFileName = os.path.basename(self.currentFileDir)
        self.currentDic = self.__parse_navigation_json(self.currentFileDir)
        self.get_current_node_info()
        self.previousNodes = []
        self.nextNodes = []
        NavigationEngine._initialized = True

    def __parse_navigation_json(self, map_dir: str) -> dict:
        with open(map_dir, "r", encoding="UTF-8") as myJSONFile:
            self.myLogger.log("D", "Successfully opened file: " + map_dir, self.TAG)
            return json.load(myJSONFile)

    def refresh_node_info(self):
        self.currentDic = self.__parse_navigation_json(self.currentFileDir)
        self.get_current_node_info()

    def get_current_node_info(self):
        self.currentNodeName = self.currentDic.get("Name", "Unknown")
        self.currentNodeDesc = self.currentDic.get("Description", "Unknown")
        self.currentNodePrev = self.currentDic.get("Previous", "Unknown")
        self.currentNodeNext = self.currentDic.get("Next", ["Unknown"])
        self.currentNodeSelections = self.currentDic.get("Selection", ["Unknown"])
        self.currentNodeFrontEnd = self.currentDic.get("Frontend", "Unknown")
        # self.myLogger.log("T", "Successfully refreshed node info:", self.TAG)
        # self.myLogger.log("T", "Node name: " + self.currentNodeName, self.TAG)
        # self.myLogger.log("T", "Node description: " + self.currentNodeDesc, self.TAG)
        # self.myLogger.log("T", "Previous node(s): " + str(self.currentNodePrev), self.TAG)
        # self.myLogger.log("T", "Next node(s): " + str(self.currentNodeNext), self.TAG)
        # self.myLogger.log("T", "Use frontend: " +self.currentNodeFrontEnd, self.TAG)

    def get_next_node_names(self) -> dict:
        if self.currentDic["Next"][0] == "END":
            return {}
        else:
            selection_list = self.currentDic["Selection"]
            result_dict = {}
            tmp_next_list = copy.deepcopy(self.currentDic["Next"])
            for i in range(len(tmp_next_list)):
                navigation_file_dir = os.path.join(self.navigatorDir, tmp_next_list[i])
                with open(navigation_file_dir, "r", encoding="UTF-8") as myJSON:
                    next_node_name = json.load(myJSON)["Name"]
                result_dict[selection_list[i]] = next_node_name
            return result_dict

    def goto_node(self, node_identifier) -> None:
        if isinstance(node_identifier, int) and 0 <= node_identifier < len(self.currentDic["Next"]):
            node_name = self.currentDic["Next"][node_identifier]
        else:
            node_name = str(node_identifier)
        if not node_name.endswith(".json"):
            node_name += ".json"
        if node_name in self.currentDic["Next"]:
            self.previousNodes.append(self.currentFileDir)
            self.currentFileDir = os.path.join(self.navigatorDir, node_name)
            self.currentFileName = os.path.basename(self.currentFileDir)
            self.refresh_node_info()
        elif node_name == self.currentDic["Previous"]:
            self.previousNodes.append(self.currentFileDir)
            self.currentFileDir = os.path.join(self.navigatorDir, node_name)
            self.currentFileName = os.path.basename(self.currentFileDir)
            self.refresh_node_info()
        else:
            raise FileNotFoundError(
                "Unknown navigation destination when attempting to go to node \"" + node_name + "\"")

    # Argument "nodeName" is reserved for situations with multiple upper-level nodes.
    def go_to_upper_level(self) -> None:
        if self.currentDic["Previous"] == "END":
            self.myLogger.log("E", "Attempting to navigate to an unexisting upper level node.", self.TAG)
            self.myLogger.log("E", "Currently at: " + self.currentNodeName, self.TAG)
            self.myLogger.log("E", "Complete previous stack: " + str(self.currentDic["Previous"]), self.TAG)
            raise RuntimeError("Attempting to navigate to an unexisting upper level node.")
        node_name = self.currentDic["Previous"]
        self.myLogger.log("D", "Go to upper level, node name: " + node_name, self.TAG)
        self.previousNodes.append(self.currentFileDir)
        self.currentFileDir = os.path.join(self.navigatorDir, node_name)
        self.currentFileName = os.path.basename(self.currentFileDir)
        self.myLogger.log("D", "Using file from " + self.currentFileDir, self.TAG)
        self.refresh_node_info()

    def go_to_previous(self) -> None:
        if self.previousNodes:
            self.nextNodes.append(self.currentFileDir)
            self.currentFileDir = os.path.join(self.navigatorDir, self.previousNodes.pop(-1))
            self.currentFileName = os.path.basename(self.currentFileDir)
            self.refresh_node_info()
        else:
            raise RuntimeError("Attempting to navigate to an unexisting previous node.")

    def go_to_next(self) -> None:
        if self.nextNodes:
            self.previousNodes.append(self.currentFileDir)
            self.currentFileDir = os.path.join(self.navigatorDir, self.nextNodes.pop(-1))
            self.currentFileName = os.path.basename(self.currentFileDir)
            self.refresh_node_info()
        else:
            raise RuntimeError("Attempting to navigate to an unexisting next node.")

    def __traverse_nodes_recursively(self):
        result = []

        current_result = [
            self.currentDic["Name"],
            self.currentDic["Description"],
            self.currentDic["Frontend"],
            self.currentFileDir,
            self.currentDic["Next"].copy() if isinstance(self.currentDic["Next"], list) else ["Unknown"],
            self.currentDic["Previous"]
        ]
        result.append(current_result)

        if self.currentDic["Next"][0] != "END":
            for next_node in self.currentDic["Next"]:
                prev_file_dir = self.currentFileDir
                prev_dic = self.currentDic
                self.goto_node(next_node)

                # Traverse recursively
                child_results = self.__traverse_nodes_recursively()
                result.extend(child_results)

                self.currentFileDir = prev_file_dir
                self.currentFileName = os.path.basename(self.currentFileDir)
                self.currentDic = prev_dic
                self.get_current_node_info()

        return result

    def traverse_all_nodes(self):
        os.system("cls") if os.name == "nt" else os.system("clear")
        start_file_dir = self.currentFileDir
        start_dic = self.currentDic
        self.currentNodeName = self.ROOT_NODE
        self.currentFileDir = os.path.join(self.navigatorDir, self.currentNodeName)
        self.currentFileName = os.path.basename(self.currentFileDir)
        self.refresh_node_info()
        traverse_result = self.__traverse_nodes_recursively()
        self.currentFileDir = start_file_dir
        self.currentFileName = os.path.basename(self.currentFileDir)
        self.currentDic = start_dic
        self.get_current_node_info()

        # Display result
        result_list_length = len(traverse_result)
        print("=" * 80)
        print("Traverse Result")
        print("=" * 80)
        indent = " " * 4

        for i in range(result_list_length):
            print("Page %d/%d, %s" % (i + 1, result_list_length, traverse_result[i][0]))
            print(indent + "Description: ", traverse_result[i][1])
            print(indent + "UI File: ", traverse_result[i][2])
            print(indent + "Navigation Map Directory: ", traverse_result[i][3])
            if traverse_result[i][4][0] != "END":
                print(indent + "Can Navigate To:")
                for j in traverse_result[i][4]:
                    print(indent * 2 + j)
            if traverse_result[i][5] != "END":
                print(indent + "Upper Page: ", traverse_result[i][5])
            print()


class NavigationMapGenerator:
    LEGAL_PROPS = ["Name", "Description", "Previous", "Next", "Frontend", "Selection"]

    def __init__(self) -> None:
        self.currentMapSelection = None
        self.currentMapFrontEnd = None
        self.currentMapNext = None
        self.currentMapPrev = None
        self.currentMapDesc = None
        self.currentMapName = None
        self.myLogger = LogUtils.LogUtils()
        self.myNavigationEngine = NavigationEngine()
        self.TAG = "NavigationMapGenerator"
        self.currentFileName = os.path.join(os.getcwd(), "Core", "Navigator", "main_navigation.json")
        with open(self.currentFileName, "r", encoding="UTF-8") as myFile:
            self.currentDic: dict = json.load(myFile)
        self.get_map_props()

    @staticmethod
    def list_file(file_dir=""):
        path_to_maps = file_dir or os.path.join(os.getcwd(), "Core", "Navigator")
        return os.listdir(path_to_maps)

    def switch_file(self):
        tmp_list = self.list_file()
        for i in range(len(tmp_list)):
            print(i + 1, tmp_list[i])
        self.save_file()
        print("Previous mods have been saved.")
        my_selection = int(input("Type -1 to create a new map file."))
        if my_selection == -1:
            map_name = input("Enter new map name: ")
            self.currentFileName = os.path.join(os.getcwd(), "Core", "Navigator", map_name)
            with open(self.currentFileName, "w+", encoding="UTF-8") as myFile:
                json.dump({}, myFile)
            self.currentDic = {}
        else:
            try:
                map_name = tmp_list[my_selection - 1]
            except IndexError:
                print("Index over range, automatically switch to the last file.")
                time.sleep(1)
                map_name = tmp_list[-1]
            try:
                self.currentFileName = os.path.join(os.getcwd(), "Core", "Navigator", map_name)
                with open(self.currentFileName, "r", encoding="UTF-8") as myFile:
                    self.currentDic = json.load(myFile)
            except FileNotFoundError:
                with open(self.currentFileName, "w+", encoding="UTF-8") as myFile:
                    json.dump({}, myFile)
                self.currentDic = {}
        self.get_map_props()

    def save_file(self):
        with open(self.currentFileName, "w", encoding="UTF-8") as myFile:
            json.dump(self.currentDic, myFile, indent=4, sort_keys=True)

    def get_map_props(self):
        self.currentMapName = self.currentDic.get("Name", "Unknown")
        self.currentMapDesc = self.currentDic.get("Description", "Unknown")
        self.currentMapPrev = self.currentDic.get("Previous", "Unknown")
        self.currentMapNext = self.currentDic.get("Next", ["Unknown"])
        self.currentMapFrontEnd = self.currentDic.get("Frontend", "Unknown")
        self.currentMapSelection = self.currentDic.get("Selection", ["Unknown"])

    def print_map_info(self):
        name = self.currentMapName
        desc = self.currentMapDesc
        prev = self.currentMapPrev
        next_nodes = self.currentMapNext
        fe = self.currentMapFrontEnd
        sel = self.currentMapSelection
        print("Name: ", name, "\n",
              "Description: ", desc, "\n",
              "Previous map file: ", prev, "\n",
              "Next map file(s):", next_nodes, "\n",
              "Corresponding selection(s):", sel, "\n",
              "Frontend File: ", fe)

    def edit_current_map(self, value="", target_prop: str = "", mode="add") -> bool:
        if not target_prop in self.LEGAL_PROPS:
            return False
        if mode == "add":
            if target_prop in ["Next", "Selection"]:
                try:
                    tmp_list: list = self.currentDic[target_prop]
                    tmp_list.append(value)
                    self.currentDic[target_prop] = tmp_list
                except KeyError:
                    self.currentDic[target_prop] = [value]
            else:
                self.currentDic[target_prop] = value
        else:
            if target_prop == "Next" or "Selection":
                for i in range(len(self.currentDic[target_prop])):
                    print(i + 1, self.currentDic[target_prop][i])
                pos = int(input("Enter an index: "))
                self.currentDic[target_prop].pop(pos - 1)
            else:
                self.currentDic[target_prop] = ""
        return True

    def __choose_key(self) -> str:
        def confirm_decimal(number_str: str) -> bool:
            for number in number_str:
                if not '0' <= number <= '9':
                    return False
            return True

        while 1:
            print("Select a key:")
            for i in range(len(self.LEGAL_PROPS)):
                print(i + 1, self.LEGAL_PROPS[i])
            print("Enter a number or full prop name, case sensitive. Enter \"XXX\" to exit.")
            tmp_str = input()
            if tmp_str == "XXX":
                return ""
            if tmp_str in self.LEGAL_PROPS:
                return tmp_str
            elif confirm_decimal(tmp_str):
                return self.LEGAL_PROPS[int(tmp_str) - 1]
            else:
                print("Illegal option.")

    def refresh_cli(self):

        try:
            os.system("cls") if os.name == "nt" else os.system("clear")
            print("=" * 80)
            print("Current File: " + self.currentFileName)
            self.get_map_props()
            self.print_map_info()
            print("=" * 80)
            print("Please save your mods in time!")
            print("=" * 80)
            print()
            prompt_list = ["[W] Switch a map;",
                           "[E] Edit current map;",
                           "[R] Remove a value in current map config;",
                           "[S] Save;",
                           "[T] Traverse navigation map;",
                           "[X] Exit.", ]
            for i in prompt_list:
                print(i)
            print()
            print("=" * 80)
            my_selection = input("Your choice: ").upper()
            if my_selection == "W":
                self.switch_file()
            elif my_selection == "E":
                self.edit_current_map(target_prop=self.__choose_key(),
                                      value=input("The value you want to add to the map: "))
            elif my_selection == "S":
                self.save_file()
            elif my_selection == "R":
                self.edit_current_map(target_prop=self.__choose_key(), mode="remove")
            elif my_selection == "X":
                self.save_file()
                exit()
            elif my_selection == "T":
                myNavigationEngine.traverse_all_nodes()
                input("Press Enter to continue.")
            else:
                print("Illegal input.")
        except KeyboardInterrupt:
            print("Exit at KeyboardInterrupt.")
            self.save_file()
            exit()


if __name__ == "__main__":
    myNavigationEngine = NavigationEngine()
    if input("1: Edit navigator map; 2: Run single traverse test. Your choice: ") == "1":
        myNavigationGen = NavigationMapGenerator()
        while 1:
            myNavigationGen.refresh_cli()
    else:
        myNavigationEngine.traverse_all_nodes()
