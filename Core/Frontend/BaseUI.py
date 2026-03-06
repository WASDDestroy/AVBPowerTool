import importlib.util
import os
import sys


class BaseUI:

    def __init__(self, logger=None, gotoNode="", navigationEngine=None) -> None:
        self.TAG = self.__class__.__name__
        self.nodeFunction = {}
        self.customizedFunction = {}  # "Press Key" : "Function Name"
        currentDir = os.path.join(os.getcwd(), "Core")
        # Import LogUtils dynamically
        try:
            spec: importlib.util.__spec__ = importlib.util.spec_from_file_location(name="LogUtils",
                                                                                   location=os.path.join(currentDir, "LogUtils.py"))
            LogUtils = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(LogUtils)

            sys.modules["LogUtils"] = LogUtils
        except ImportError as e:
            print(e)

        self.myLogger = logger or LogUtils.LogUtils()  # type: ignore

        # Import DynamicImportUtils dynamically
        try:
            spec: importlib.util.__spec__ = importlib.util.spec_from_file_location(name="DynamicImportUtils",
                                                                                   location=os.path.join(currentDir, "DynamicImportUtils.py"))
            DynamicImportUtils = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(DynamicImportUtils)

            sys.modules["DynamicImportUtils"] = DynamicImportUtils
        except ImportError as e:
            print(e)
        self.myImporter = DynamicImportUtils.DynamicImportUtils(
            logger=self.myLogger)
        UIUtils = self.myImporter.importModule(moduleName="UIUtils")
        NavigationEngine = self.myImporter.importModule(
            moduleName="NavigationEngine")
        self.myNavigationEngine = navigationEngine or NavigationEngine.NavigationEngine(
            self.myLogger)  # type: ignore
        self.myUIUtils = UIUtils.UIUtils(logger)
        self.myLogger.log("D", "Currently at: " +
                          self.myNavigationEngine.currentNodeName, self.TAG)
        self.myLogger.log("D", "Desired node: " + gotoNode, self.TAG)
        if gotoNode and gotoNode != self.myNavigationEngine.currentFileName:
            self.myNavigationEngine.gotoNode(gotoNode)
        self.customizedInit()
        self.getNodeFunctions()
        self.myLogger.log("I", "UI instance %s created." %
                          (self.TAG), self.TAG)

    def customizedInit(self):
        '''
        Store customized initialization process of your UI class.
        '''
        pass

    def getNodeFunctions(self):
        # Node function = Next nodes + Customized actions
        self.nodeFunction = {}
        for i in self.customizedFunction:
            self.nodeFunction[i] = self.customizedFunction[i]
        nextNodesDict = self.myNavigationEngine.getNextNodeNames()
        for i in nextNodesDict:
            self.nodeFunction[i] = nextNodesDict[i]
        if self.myNavigationEngine.currentDic["Previous"] == "END":
            self.nodeFunction["E"] = "Exit"
        else:
            self.nodeFunction["B"] = "Back to upper level"

    def handleBackAndExit(self, functionName):
        if "back" in functionName.lower():
            self.myLogger.log("I", "Back to upper level.", self.TAG)
            self.myNavigationEngine.goToUpperLevel()
            return True
        if functionName == "Exit":
            print("Exiting.")
            self.myLogger.log("I", "Exit on UI request.", self.TAG)
            exit()
        return False

    def callBackEnd(self, functionName: str):
        self.handleBackAndExit(functionName)
        raise NotImplementedError(
            "Unimplemented method callBackEnd." + self.TAG)

    def _inDevelopmentPlaceHolder(self):
        print("Function in development.")
        self.myUIUtils.pressEnterToContinue()

    def confirmOperation(self, prompt="Confirm operation?") -> bool:
        return self.myUIUtils.confirmOperation(prompt)

    def showTitle(self):
        tmpLen = (80 - len(self.myNavigationEngine.currentNodeName)) // 2
        if tmpLen >= 0:
            print("=" * tmpLen
                  + self.myNavigationEngine.currentNodeName
                  + "=" * tmpLen)
        else:
            print(self.myNavigationEngine.currentNodeName)
            print("=" * 80)

    def showUI(self):
        self.clearScreen()
        self.showTitle()
        for i in self.nodeFunction:
            print("[%s] %s" % (i, self.nodeFunction[i]))
        print("=" * 80)

    def clearScreen(self):
        os.system("cls") if os.name == "nt" else os.system("clear")

    def handleInteractionLogic(self):
        mySelection = input("Your choice: ").upper()
        self.myLogger.log("T", "User input: " + mySelection, self.TAG)
        if not mySelection in self.nodeFunction.keys():
            print("No such choice.")
            self.myLogger.log("W", "Illegal choice: " + mySelection, self.TAG)
            self.myUIUtils.pressEnterToContinue()
        else:
            functionName = self.nodeFunction[mySelection]
            self.myLogger.log("T", "Function name: " + functionName, self.TAG)
            if self.handleBackAndExit(functionName):
                self.myLogger.log
                return True
            # Check whether function is in next node
            if self.myNavigationEngine.currentDic["Next"][0] != "END":
                self.myLogger.log(
                    "T", "Current node has subnodes, traverse them.", self.TAG)
                for i in self.myNavigationEngine.currentDic["Next"]:
                    self.myLogger.log(
                        "T", "Traversing, current: " + i, self.TAG)
                    self.myNavigationEngine.gotoNode(i)
                    self.myNavigationEngine.refreshNodeInfo()
                    self.myLogger.log(
                        "T", "Switched node and refreshed info.", self.TAG)
                    if self.myNavigationEngine.currentDic["Name"] == functionName:
                        # Found function in one of the next node, dynamically import it and execute entry
                        moduleName = self.myNavigationEngine.currentDic["Frontend"].rstrip(
                            ".py")
                        self.myLogger.log(
                            "T", "Found function! Corresponding module name: " + moduleName, self.TAG)
                        self.myLogger.log(
                            "I", "Navigate to: " + moduleName, self.TAG)
                        myObject = self.myImporter.createFrontendInstance(self.myImporter.importFrontEndModule(moduleName),
                                                                          moduleName,
                                                                          self.myLogger,
                                                                          i,
                                                                          self.myNavigationEngine)
                        myObject.entry(
                            navigationEngine=self.myNavigationEngine)
                        break
                    else:
                        self.myLogger.log(
                            "T", "Function name mismatch, go to upper level.", self.TAG)
                        self.myNavigationEngine.goToUpperLevel()
                else:
                    # If the loop ends normally, call functions in current node.
                    self.myLogger.log(
                        "T", "Traverse end! Target function not found!", self.TAG)
                    self.myLogger.log(
                        "T", "Call current node's function by name: " + functionName, self.TAG)
                    self.callBackEnd(functionName)
            else:
                self.myLogger.log(
                    "T", "Current node does not contain subnodes, directly call function: " + functionName, self.TAG)
                self.callBackEnd(functionName)

    def entry(self, navigationEngine=None):
        if navigationEngine is not None:
            self.myLogger.log("D", "Use provided navigation engine.", self.TAG)
            self.myNavigationEngine = navigationEngine
        while 1:
            self.myLogger.log("D", "Currently at: " +
                              self.myNavigationEngine.currentNodeName, self.TAG)
            self.myLogger.log(
                "D", "Subnodes: " + str(self.myNavigationEngine.currentNodeNext), self.TAG)
            self.myLogger.log(
                "D", "Previous node: " + str(self.myNavigationEngine.currentNodePrev), self.TAG)
            self.showUI()
            if self.handleInteractionLogic():
                break


if __name__ == "__main__":
    myBaseUI = BaseUI()
    myBaseUI.entry()
