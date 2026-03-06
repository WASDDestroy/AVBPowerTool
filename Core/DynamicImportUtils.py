import os, sys
import LogUtils
import importlib.util

class DynamicImportUtils:

    def __init__(self, logger = None) -> None:
        self.TAG = "DynamicImportUtils"
        self.myLogger = logger or LogUtils.LogUtils(shouldAttachTime = True)

    def importFrontEndModule(self, moduleName : str) -> object:
        return self.importModule(moduleName, os.path.join(os.getcwd(), "Core", "Frontend"))
    
    def importModule(self, moduleName : str, moduleDir = None):
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
            self.myLogger.log("W", "Exception happened when importing module " + moduleName + ": " + repr(e), self.TAG)
            return None
    
    def createInstance(self, module, className, logger):
        try:
            ClassName = getattr(module, className)
            self.myLogger.log("I", "Successfully get attribute in module %s with class name %s"%(module, className), self.TAG)
        except AttributeError:
            self.myLogger.log("E", "Failed when creating instance for module with class name %s, no such attribution!"%(className), self.TAG)
            raise RuntimeError("Unable to create instance.")
        self.myLogger.log("I", "Successfully created instance for module with classname " + className, self.TAG)
        return ClassName(logger = logger)
    
    def createFrontendInstance(self, module, className, logger, gotoNode, navigationEngine):
        try:
            ClassName = getattr(module, className)
            self.myLogger.log("I", "Successfully get attribute in module %s with class name %s"%(module, className), self.TAG)
        except AttributeError:
            self.myLogger.log("E", "Failed when creating instance for module with class name %s, no such attribution!"%(className), self.TAG)
            raise RuntimeError("Unable to create instance.")
        self.myLogger.log("I", "Successfully created instance for module with classname " + className, self.TAG)
        return ClassName(logger = logger, gotoNode = gotoNode, navigationEngine = navigationEngine)