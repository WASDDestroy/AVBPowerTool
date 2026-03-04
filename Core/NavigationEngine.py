import os, json, time, copy
import LogUtils

class NavigationEngine:
    def __init__(self, logger = None) -> None:
        self.myLogger = logger or LogUtils.LogUtils()
        self.ROOT_NODE = "main_navigation.json"
        self.TAG = "NavigationEngine"
        self.myLogger.log("I", "Navigation engine started.", self.TAG)
        self.navigatorDir = os.path.join(os.getcwd(), "Core", "Navigator")
        self.myLogger.log("I", "Navigation map root dir: " + self.navigatorDir, self.TAG)
        self.currentFileDir = os.path.join(self.navigatorDir, self.ROOT_NODE)
        self.currentDic = self.__parseNavigationJSON(self.currentFileDir)
        self.getCurrentNodeInfo()
        self.previousNodes = []
        self.nextNodes = []

    def __parseNavigationJSON(self, mapDir : str) -> dict:
        with open(mapDir, "r", encoding = "UTF-8") as myJSONFile:
            return json.load(myJSONFile)
    
    def refreshNodeInfo(self):
        self.currentDic = self.__parseNavigationJSON(self.currentFileDir)
        self.getCurrentNodeInfo()
    
    def getCurrentNodeInfo(self):
        self.currentNodeName = self.currentDic.get("Name", "Unknown")
        self.currentNodeDesc = self.currentDic.get("Description", "Unknown")
        self.currentNodePrev = self.currentDic.get("Previous", "Unknown")
        self.currentNodeNext = self.currentDic.get("Next", ["Unknown"])
        self.currentNodeSelections = self.currentDic.get("Selection", ["Unknown"])
        self.currentNodeFrontEnd = self.currentDic.get("Frontend", "Unknown")
    
    def getNextNodeNames(self) -> dict:
        if self.currentDic["Next"][0] == "END":
            return {}
        else:
            selectionList = self.currentDic["Selection"]
            resultDict = {}
            tmpNextList = copy.deepcopy(self.currentDic["Next"])
            for i in range(len(tmpNextList)):
                navigationFileDir = os.path.join(self.navigatorDir, tmpNextList[i])
                with open(navigationFileDir, "r", encoding = "UTF-8") as myJSON:
                    nextNodeName = json.load(myJSON)["Name"]
                resultDict[selectionList[i]] = nextNodeName
            return resultDict
    
    def gotoNode(self, nodeIdentifier) -> None:
        if isinstance(nodeIdentifier, int) and 0 <= nodeIdentifier < len(self.currentDic["Next"]):
            nodeName = self.currentDic["Next"][nodeIdentifier]
        else:
            nodeName = str(nodeIdentifier)
        if not nodeName.endswith(".json"):
            nodeName += ".json"
        if nodeName in self.currentDic["Next"]:
            self.previousNodes.append(self.currentFileDir)
            self.currentFileDir = os.path.join(self.navigatorDir, nodeName)
            self.refreshNodeInfo()
        elif nodeName == self.currentDic["Previous"]:
            self.previousNodes.append(self.currentFileDir)
            self.currentFileDir = os.path.join(self.navigatorDir, nodeName)
            self.refreshNodeInfo()
        else:
            raise FileNotFoundError("Unknown navigation destination when attempting to go to node \"" + nodeName + "\"")
    
    # Argument "nodeName" is reserved for situations with multiple upper-level nodes.
    def goToUpperLevel(self) -> None:
        if self.currentDic["Previous"] == "END":
            raise RuntimeError("Attempting to navigate to an unexisting upper level node.")
        nodeName = self.currentDic["Previous"]
        self.previousNodes.append(self.currentFileDir)
        self.currentFileDir = os.path.join(self.navigatorDir, nodeName)
        self.refreshNodeInfo()


    def goToPrevious(self) -> None:
        if self.previousNodes:
            self.nextNodes.append(self.currentFileDir)
            self.currentFileDir = os.path.join(self.navigatorDir, self.previousNodes.pop(-1))
            self.refreshNodeInfo()
        else:
            raise RuntimeError("Attempting to navigate to an unexisting previous node.")
    
    def goToNext(self) -> None:
        if self.nextNodes:
            self.previousNodes.append(self.currentFileDir)
            self.currentFileDir = os.path.join(self.navigatorDir, self.nextNodes.pop(-1))
            self.refreshNodeInfo()
        else:
            raise RuntimeError("Attempting to navigate to an unexisting next node.")
    
    def __traverseNodesRecursively(self, rootMapName="main_navigation.json"):
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
                self.gotoNode(next_node)
                
                # Traverse recursively
                child_results = self.__traverseNodesRecursively()
                result.extend(child_results)
                
                self.currentFileDir = prev_file_dir
                self.currentDic = prev_dic
                self.getCurrentNodeInfo()
        
        return result

    def traverseAllNodes(self):
        os.system("cls") if os.name == "nt" else os.system("clear")
        start_file_dir = self.currentFileDir
        start_dic = self.currentDic
        self.currentNodeName = self.ROOT_NODE
        self.currentFileDir = os.path.join(self.navigatorDir, self.currentNodeName)
        self.refreshNodeInfo()
        traverse_result = self.__traverseNodesRecursively()
        self.currentFileDir = start_file_dir
        self.currentDic = start_dic
        self.getCurrentNodeInfo()
        
        # Display result
        result_list_length = len(traverse_result)
        print("=" * 80)
        print("Traverse Result")
        print("=" * 80)
        INDENT = " " * 4
        
        for i in range(result_list_length):
            print("Page %d/%d, %s" % (i + 1, result_list_length, traverse_result[i][0]))
            print(INDENT + "Description: ", traverse_result[i][1])
            print(INDENT + "UI File: ", traverse_result[i][2])
            print(INDENT + "Navigation Map Directory: ", traverse_result[i][3])
            if traverse_result[i][4][0] != "END":
                print(INDENT + "Can Navigate To:")
                for j in traverse_result[i][4]:
                    print(INDENT * 2 + j)
            if traverse_result[i][5] != "END":
                print(INDENT + "Upper Page: ", traverse_result[i][5])
            print()

class NavigationMapGenerator:

    LEGAL_PROPS = ["Name", "Description", "Previous", "Next", "Frontend", "Selection"]
    
    def __init__(self, logger = None) -> None:
        self.myLogger = logger or LogUtils.LogUtils()
        self.myNavigationEngine = NavigationEngine()
        self.TAG = "NavigationMapGenerator"
        self.currentFileName = os.path.join(os.getcwd(), "Core", "Navigator", "main_navigation.json")
        with open(self.currentFileName, "r", encoding = "UTF-8") as myFile:
            self.currentDic : dict = json.load(myFile)
        self.getMapProps()

    def listFile(self, dir = ""):
        pathToMaps = dir or os.path.join(os.getcwd(), "Core", "Navigator")
        return os.listdir(pathToMaps)
    
    def switchFile(self):
        tmpList = self.listFile()
        for i in range(len(tmpList)):
            print(i + 1, tmpList[i])
        self.saveFile()
        print("Previous mods have been saved.")
        mySelection = int(input("Type -1 to create a new map file."))
        if mySelection == -1:
            mapName = input("Enter new map name: ")
            self.currentFileName = os.path.join(os.getcwd(), "Core", "Navigator", mapName)
            with open(self.currentFileName, "w+", encoding = "UTF-8") as myFile:
                json.dump({}, myFile)
            self.currentDic = {}
        else:
            try: 
                mapName = tmpList[mySelection - 1]
            except IndexError:
                print("Index over range, automatically switch to the last file.")
                time.sleep(1)
                mapName = tmpList[-1]
            try:
                self.currentFileName = os.path.join(os.getcwd(), "Core", "Navigator", mapName)
                with open(self.currentFileName, "r", encoding = "UTF-8") as myFile:
                    self.currentDic = json.load(myFile)
            except:
                with open(self.currentFileName, "w+", encoding = "UTF-8") as myFile:
                    json.dump({}, myFile)
                self.currentDic = {}
        self.getMapProps()

    def saveFile(self):
        with open(self.currentFileName, "w", encoding = "UTF-8") as myFile:
            json.dump(self.currentDic, myFile, indent = 4, sort_keys = True)
    
    def getMapProps(self):
        self.currentMapName = self.currentDic.get("Name", "Unknown")
        self.currentMapDesc = self.currentDic.get("Description", "Unknown")
        self.currentMapPrev = self.currentDic.get("Previous", "Unknown")
        self.currentMapNext = self.currentDic.get("Next", ["Unknown"])
        self.currentMapFrontEnd = self.currentDic.get("Frontend", "Unknown")
        self.currentMapSelection = self.currentDic.get("Selection", ["Unknown"])
    
    def printMapInfo(self):
        name = self.currentMapName
        desc = self.currentMapDesc
        prev = self.currentMapPrev
        next = self.currentMapNext
        fe = self.currentMapFrontEnd
        sel = self.currentMapSelection
        print("Name: ", name, "\n",
              "Description: ", desc, "\n",
              "Previous map file: ", prev, "\n",
              "Next map file(s):", next, "\n",
              "Corresponding selection(s):", sel, "\n",
              "Frontend File: ", fe)

    def editCurrentMap(self, value = "", targetProp : str = "", mode = "add") -> bool:
        if not targetProp in self.LEGAL_PROPS:
            return False
        if mode == "add":
            if targetProp == "Next" or "Selection":
                try:
                    tmpList : list = self.currentDic[targetProp]
                    tmpList.append(value)
                    self.currentDic[targetProp] = tmpList
                except KeyError:
                    self.currentDic[targetProp] = [value]
            else:
                self.currentDic[targetProp] = value
        else:
            if targetProp == "Next" or "Selection":
                for i in range(len(self.currentDic[targetProp])):
                    print(i + 1, self.currentDic[targetProp][i])
                pos = int(input("Enter an index: "))
                self.currentDic[targetProp].pop(pos - 1)
            else:
                self.currentDic[targetProp] = ""
        return True

    def __chooseKey(self) -> str:
        def confirmDecimal(numberStr : str) -> bool:
            for i in numberStr:
                if not '0' <= i <= '9':
                    return False
            return True
        while 1:
            print("Select a key:")
            for i in range(len(self.LEGAL_PROPS)):
                print(i + 1, self.LEGAL_PROPS[i])
            print("Enter a number or full prop name, case sensitive. Enter \"XXX\" to exit.")
            tmpStr = input()
            if tmpStr == "XXX":
                return ""
            if tmpStr in self.LEGAL_PROPS:
                return tmpStr
            elif confirmDecimal(tmpStr):
                return self.LEGAL_PROPS[int(tmpStr) - 1]
            else:
                print("Illegal option.")
        return ""


    def refreshCLI(self):

        try:
            os.system("cls") if os.name == "nt" else os.system("clear")
            print("=" * 80)
            print("Current File: " + self.currentFileName)
            self.getMapProps()
            self.printMapInfo()
            print("=" * 80)
            print("Please save your mods in time!")
            print("=" * 80)
            print()
            PROMPT_LIST = ["[W] Switch a map;",
                           "[E] Edit current map;",
                           "[R] Remove a value in current map config;",
                           "[S] Save;",
                           "[T] Traverse navigation map;",
                           "[X] Exit.",]
            for i in PROMPT_LIST:
                print(i)
            print()
            print("=" * 80)
            mySelection = input("Your choice: ").upper()
            if mySelection == "W":
                self.switchFile()
            elif mySelection == "E":
                self.editCurrentMap(targetProp = self.__chooseKey(),
                                    value = input("The value you want to add to the map: "))
            elif mySelection == "S":
                self.saveFile()
            elif mySelection == "R":
                self.editCurrentMap(targetProp = self.__chooseKey(), mode = "remove")
            elif mySelection == "X":
                self.saveFile()
                exit()
            elif mySelection == "T":
                myNavigationEngine.traverseAllNodes()
                input("Press Enter to continue.")
            else:
                print("Illegal input.")
        except KeyboardInterrupt:
            print("Exit at KeyboardInterrupt.")
            self.saveFile()
            exit()

if __name__ == "__main__":
    myNavigationEngine = NavigationEngine()
    if input("1: Edit navigator map; 2: Run single traverse test. Your choice: ") == "1":
        myNavigationGen = NavigationMapGenerator()
        while 1:
            myNavigationGen.refreshCLI()
    else:
        myNavigationEngine.traverseAllNodes()