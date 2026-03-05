import importlib.util
import os
import sys

class BaseUI:

    def __init__(self, logger = None, gotoNode = "", navigationEngine = None) -> None:
        self.TAG = "BaseUI"
        self.nodeFunction = {}
        self.customizedFunction = {} # "Press Key" : "Function Name"
        currentDir = os.path.join(os.getcwd(), "Core")

        # Import LogUtils dynamically
        try:
            spec : importlib.util.__spec__ = importlib.util.spec_from_file_location(name = "LogUtils", 
                                                                                location = os.path.join(currentDir, "LogUtils.py"))
            LogUtils = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(LogUtils)

            sys.modules["LogUtils"] = LogUtils
        except ImportError as e:
            print(e)

        # Import NavigationEngine
        try:
            spec1 : importlib.util.__spec__ = importlib.util.spec_from_file_location(name = "NavigationEngine",
                                                                                     location = os.path.join(currentDir, "NavigationEngine.py"))
            NavigationEngine = importlib.util.module_from_spec(spec1)
            spec1.loader.exec_module(NavigationEngine)

            sys.modules["NavigationEngine"] = NavigationEngine
        except ImportError as e:
            print(e)
        self.myLogger = logger or LogUtils.LogUtils() # type: ignore
        self.myNavigationEngine = navigationEngine or NavigationEngine.NavigationEngine(self.myLogger) # type: ignore
        if gotoNode:
            self.myNavigationEngine.gotoNode(gotoNode)
        self.customizedInit()
        self.getNodeFunctions()
        self.myLogger.log("I", "UI instance %s created."%(self.TAG), self.TAG)

    def customizedInit(self):
        '''
        Store customized initialization process of your UI class.
        '''
        pass

    def _pressEnterToContinue(self):
        input("Press Enter to continue.")

    def _importFrontEndModule(self, moduleName : str) -> object:
        return self._importModule(moduleName, os.path.join(os.getcwd(), "Core", "Frontend"))
    
    def _importModule(self, moduleName : str, moduleDir = None):
        if moduleDir is None:
            moduleDir = os.path.join(os.getcwd(), "Core")
        moduleName = moduleName.rstrip(".py")
        self.myLogger.log("D", "Importing module: " + moduleName, self.TAG)
        self.myLogger.log("D", "Complete path: " + os.path.join(moduleDir, moduleName + ".py"), self.TAG)
        try:
            if moduleName in sys.modules:
                self.myLogger.log("D", f"Module {moduleName} already imported, returning existing module", self.TAG)
                return sys.modules[moduleName]
            if moduleDir not in sys.path:
                sys.path.insert(0, moduleDir)
                self.myLogger.log("D", f"Added {moduleDir} to sys.path", self.TAG)
            try:
                ImportedModule = importlib.import_module(moduleName)
                self.myLogger.log("I", f"Successfully imported module {moduleName} using import_module", self.TAG)
            except ImportError:  
                spec : importlib.util.__spec__ = importlib.util.spec_from_file_location(moduleName,
                                                                                    location = os.path.join(moduleDir, moduleName + ".py"))
                ImportedModule = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(ImportedModule)
            sys.modules[moduleName] = ImportedModule
            self.myLogger.log("I", "Successfully imported module %s from %s"%(moduleName, moduleDir), self.TAG)
            return ImportedModule
        except Exception as e:
            self.myLogger.log("W", "Exception happened when importing module ", moduleName, ": " + repr(e), self.TAG)
            return None
    
    def _createInstance(self, module, className, logger):
        try:
            ClassName = getattr(module, className)
            self.myLogger.log("I", "Successfully get attribute in module %s with class name %s"%(module, className), self.TAG)
        except AttributeError:
            self.myLogger.log("E", "Failed when creating instance for module with class name %s, no such attribution!"%(className), self.TAG)
            raise RuntimeError("Unable to create instance.")
        self.myLogger.log("I", "Successfully created instance for module with classname " + className, self.TAG)
        return ClassName(logger = logger)
    
    def _createFrontendInstance(self, module, className, logger, gotoNode):
        try:
            ClassName = getattr(module, className)
            self.myLogger.log("I", "Successfully get attribute in module %s with class name %s"%(module, className), self.TAG)
        except AttributeError:
            self.myLogger.log("E", "Failed when creating instance for module with class name %s, no such attribution!"%(className), self.TAG)
            raise RuntimeError("Unable to create instance.")
        self.myLogger.log("I", "Successfully created instance for module with classname " + className, self.TAG)
        return ClassName(logger = logger, gotoNode = gotoNode)

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
            self.myNavigationEngine.refreshNodeInfo()
            self.myLogger.log("I", "Currently using file: " + self.myNavigationEngine.currentFileDir, self.TAG)
            return True
        if functionName == "Exit":
            print("Exiting.")
            self.myLogger.log("I", "Exit on UI request.", self.TAG)
            exit()
        return False

    def callBackEnd(self, functionName : str):
        self.handleBackAndExit(functionName)
        raise NotImplementedError("Unimplemented method callBackEnd." + self.TAG)

    def confirmOperation(self, prompt = "Confirm operation?") -> bool:
        try:
            if input(prompt + " [y/N]: ").lower() == "y":
                return True
            else:
                return False
        except:
            return False
    
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
            print("[%s] %s"%(i, self.nodeFunction[i]))
        print("=" * 80)
    
    def clearScreen(self):
        os.system("cls") if os.name == "nt" else os.system("clear")
    
    def handleInteractionLogic(self):
        mySelection = input("Your choice: ").upper()
        self.myLogger.log("T", "User input: " + mySelection, self.TAG)
        if not mySelection in self.nodeFunction.keys():
            print("No such choice.")
            self.myLogger.log("W", "Illegal choice: " + mySelection, self.TAG)
            self._pressEnterToContinue()
        else:
            functionName = self.nodeFunction[mySelection]
            self.myLogger.log("T", "Function name: " + functionName, self.TAG)
            if self.handleBackAndExit(functionName):
                return
            # Check whether function is in next node
            if self.myNavigationEngine.currentDic["Next"][0] != "END":
                self.myLogger.log("T", "Current node has subnodes, traverse them.", self.TAG)
                for i in self.myNavigationEngine.currentDic["Next"]:
                    self.myLogger.log("T", "Traversing, current: " + i, self.TAG)
                    self.myNavigationEngine.gotoNode(i)
                    self.myNavigationEngine.refreshNodeInfo()
                    self.myLogger.log("T", "Switched node and refreshed info.", self.TAG)
                    if self.myNavigationEngine.currentDic["Name"] == functionName:
                        # Found function in one of the next node, dynamically import it and execute entry
                        moduleName = self.myNavigationEngine.currentDic["Frontend"].rstrip(".py")
                        self.myLogger.log("T", "Found function! Corresponding module name: " + moduleName, self.TAG)
                        self.myLogger.log("T", "Navigate to: " + moduleName, self.TAG)
                        myObject = self._createFrontendInstance(self._importFrontEndModule(moduleName),
                                                        moduleName,
                                                        self.myLogger,
                                                        i)
                        myObject.entry(navigationEngine = self.myNavigationEngine)
                        break
                    else:
                        self.myLogger.log("T", "Function name mismatch, go to upper level.", self.TAG)
                        self.myNavigationEngine.goToUpperLevel()
                else:
                    # If the loop ends normally, call functions in current node.
                    self.myLogger.log("T", "Traverse end! Target function not found!", self.TAG)
                    self.myLogger.log("T", "Call current node's function by name: " + functionName, self.TAG)
                    self.callBackEnd(functionName)
            else:
                self.myLogger.log("T", "Current node does not contain subnodes, directly call function: " + functionName, self.TAG)
                self.callBackEnd(functionName)
        
    def entry(self, navigationEngine = None):
        if navigationEngine is not None:
            self.myLogger.log("D", "Use provided navigation engine.", self.TAG)
            self.myNavigationEngine = navigationEngine
        self.myLogger.log("D", self.myNavigationEngine.currentNodeName, self.TAG)
        self.myLogger.log("D", self.myNavigationEngine.currentNodeNext, self.TAG)
        self.showUI()
        self.handleInteractionLogic()

if __name__ == "__main__":
    myBaseUI = BaseUI()
    myBaseUI.entry()