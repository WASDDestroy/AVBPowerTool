import os, sys
import Core.LogUtils as LogUtils
import importlib.util

class DynamicImportUtils:

    def __init__(self, logger = None) -> None:
        self.TAG = "DynamicImportUtils"
        self.my_logger = logger or LogUtils.LogUtils(should_attach_time= True)

    def import_front_end_module(self, module_name : str) -> object:
        return self.import_module(module_name, os.path.join(os.getcwd(), "Core", "Frontend"))
    
    def import_module(self, module_name : str, module_dir = None):
        if module_dir is None:
            module_dir = os.path.join(os.getcwd(), "Core")
        module_name = module_name.rstrip(".py")
        self.my_logger.log("D", "Importing module: " + module_name, self.TAG)
        self.my_logger.log("D", "Complete path: " + os.path.join(module_dir, module_name + ".py"), self.TAG)
        try:
            if module_name in sys.modules:
                self.my_logger.log("D", f"Module {module_name} already imported, returning existing module", self.TAG)
                return sys.modules[module_name]
            if module_dir not in sys.path:
                sys.path.insert(0, module_dir)
                self.my_logger.log("D", f"Added {module_dir} to sys.path", self.TAG)
            try:
                imported_module = importlib.import_module(module_name)
                self.my_logger.log("I", f"Successfully imported module {module_name} using import_module", self.TAG)
            except ImportError:

                spec : importlib.util.__spec__ = importlib.util.spec_from_file_location(module_name,
                                                                                    location = os.path.join(module_dir, module_name + ".py"))
                imported_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(imported_module)
            sys.modules[module_name] = imported_module
            self.my_logger.log("I", "Successfully imported module %s from %s"%(module_name, module_dir), self.TAG)
            return imported_module
        except Exception as e:
            self.my_logger.log("W", "Exception happened when importing module " + module_name + ": " + repr(e), self.TAG)
            return None
    
    def create_instance(self, module, class_name, logger, goto_node = None, navigation_engine = None):
        try:
            class_name = getattr(module, class_name)
            self.my_logger.log("I", "Successfully get attribute in module %s with class name %s"%(module, class_name), self.TAG)
        except AttributeError:
            self.my_logger.log("E", "Failed when creating instance for module with class name %s, no such attribution!" % class_name, self.TAG)
            raise RuntimeError("Unable to create instance.")
        self.my_logger.log("I", "Successfully created instance for module with classname " + str(class_name), self.TAG)
        if goto_node and navigation_engine:
            return class_name(logger=logger, goto_node=goto_node, navigation_engine=navigation_engine)
        else:
            return class_name(logger = logger)
    
    def create_frontend_instance(self, module, class_name, logger, goto_node, navigation_engine):
        return self.create_instance(module, class_name, logger, goto_node, navigation_engine)