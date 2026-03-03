import LogUtils
import os, subprocess, json, importlib.util, sys

class SignImages:

    TAG = "ImageSigner"
    __IMAGE_DIR = os.path.join(os.getcwd(), "Images")

    def __init__(self, logger = None) -> None:
        if not logger:
            self.myLogger = LogUtils.LogUtils()
            self.myLogger.log("W", "Logger not given, created an instance just now.", "SignImages")
        else:
            self.myLogger = logger
        self.myConfigParser = self._createInstance(self._importModule("ConfigParser"),
                                                   "ConfigParser",
                                                   self.myLogger)
        self.myLogger.log("I", "Instance of SignImages successfully created.", "SignImages")
    
    def _importModule(self, moduleName : str, moduleDir = os.path.join(os.getcwd(), "Core")):
        moduleName = moduleName.rstrip(".py")
        try:
            spec : importlib.util.__spec__ = importlib.util.spec_from_file_location(moduleName,
                                                                                    location = os.path.join(moduleDir, moduleName + ".py"))
            ImportedModule = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(ImportedModule)
            sys.modules[moduleName] = ImportedModule
            return ImportedModule
        except Exception as e:
            self.myLogger.log("W", "Exception happened when importing module: " + repr(e), self.TAG)
    
    def _createInstance(self, module, className, logger):
        ClassName = getattr(module, className)
        return ClassName(logger = logger)
    
    def signSingleImage(self, signingCommand : list) -> tuple:
        """
        Receive a command list and run it via subcommand.
        
        :param signingCommand: The list of signing command.
        :return: A tuple contains three items:
        1. bool, indicates whether the signing process successes
        2. string, standard error of avbtool.py
        3. string, standard output of avbtool.py
        
        :rtype: tuple(bool, str, str)
        """
        result = subprocess.run(signingCommand, capture_output = True, text = True)
        signResult = (result.returncode == 0,
                result.stderr if result.stderr else "Empty",
                result.stdout if result.stdout else "Empty")
        return signResult
    
    def signImagesWithOutput(self, singleConfigArg, imageName):
        """
        Logic extracted from signImagesBatch
        """
        self.myLogger.log("I", "=" * 80, self.TAG)
        if "vbmeta" in imageName.lower():
            print("Generating vbmeta image, name: " + imageName)
        else:
            print("Signing image: " + imageName)
        self.myLogger.log("I", "Processing image: " + imageName, self.TAG)
        singleCommand : list = self.myConfigParser.buildSingleAvbtoolCommand(singleConfigArg)
        self.myLogger.log("D", "================================AVB COMMAND================================", "signImagesBatch")
        commandForOutput : str = ""
        for j in singleCommand:
            commandForOutput += j + " "
        self.myLogger.log("D", commandForOutput, "signImagesBatch")
        self.myLogger.log("D", "===========================================================================", "signImagesBatch")
        avbToolResult : tuple = self.signSingleImage(singleCommand)
        if avbToolResult[0]:
            if "vbmeta" in imageName.lower():
                print("Successfully generated vbmeta image: " + imageName)
            else:
                print("Successfully signed " + imageName)
            self.myLogger.log("D", "Successfully processed image: " + imageName)
        else:
            if "vbmeta" in imageName.lower():
                print("Failed to generate vbmeta image: " + imageName)
                print("Check your images manually, make sure that all images are signed properly.")
            else:
                print("Failed to sign " + imageName)
            self.myLogger.log("W", "Failed to process image: " + imageName, self.TAG)
        self.myLogger.log("D", "stderr from avbtool.py: " + avbToolResult[1], self.TAG)
        self.myLogger.log("D", "stdout from avbtool.py: " + avbToolResult[2], self.TAG)
        print()

    def signImagesBatch(self,
                        imageConfigFileDir = os.path.join(os.getcwd(),
                                                          "Core",
                                                          "currentConfigs",
                                                          "imageInfo.json"),
                        removeFootersFirst = False,
                        removeVB = True):
        """
        Sign images in <ProjectDir>/images dir.

        :param imageConfigFileDir: The directory of config file. Config file name is optional.
        :param removeFootersFirst: Choose whether the program removes footers before signing process.
        :param removeVB: Whether the program removes vbmeta images before signing. (Will generate new vbmeta images.)
        """
        if not imageConfigFileDir.endswith(".json"):
            imageConfigFileDir += "imageInfo.json"
        if removeFootersFirst:
            self.removeAllFooters()
        if removeVB:
            for i in os.listdir(self.__IMAGE_DIR):
                if "vbmeta" in i.lower():
                    try:
                        os.remove(os.path.join(self.__IMAGE_DIR, i))
                        self.myLogger.log("I", "Removed vbmeta image: " + i, self.TAG)
                    except Exception as e:
                        self.myLogger.log("W", "Exception happened when removing vbmeta images: " + repr(e), self.TAG)
        configDic = self.myConfigParser.json2Dic(imageConfigFileDir)
        self.myLogger.log("D", str(configDic), self.TAG)
        vbmetaList = []
        self.myLogger.log("I", "First, sign non-vbmeta images.")
        for i in configDic:
            if "vbmeta" in i.lower():
                vbmetaList.append(i)
                continue
            self.signImagesWithOutput(configDic[i], i)
        
        self.myLogger.log("I", "Then generate vbmeta images.")
        for i in vbmetaList:
            self.signImagesWithOutput(configDic[i], i)
    
    def removeAllFooters(self):
        command_list = ["python3",
                        os.path.join(os.getcwd(), "Core", "avbtool.py"),
                        "erase_footer",
                        "--image",
                        "<image_file>"]
        if os.name == "nt":
            command_list[0] = "py"
        imageList = self.myConfigParser.getImageList()
        for i in imageList:
            command_list[-1] = os.path.join(self.__IMAGE_DIR, i + ".img")
            result = subprocess.run(command_list, capture_output = True, text = True)
            self.myLogger.log("I", "avbtool.py returns with return code: " + str(result.returncode) + "when processing image" + command_list[-1], "removeAllFooters")

if __name__ == "__main__":
    myImageSigner = SignImages()
    myImageSigner.signImagesBatch()