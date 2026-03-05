import BaseUI
import os, time, json

class SignAllImagesUI(BaseUI.BaseUI):

    def customizedInit(self):
        self.TAG = "SignAllImagesUI"
        self.customizedFunction = {
            "Y" : "Sign all images with current config file",
            "I" : "Sign selected image file"
        }
        # print("Using navigation map: ", self.myNavigationEngine.currentFileDir)
        # print(self.myNavigationEngine.currentDic)
        # print(self.customizedFunction)
        # print(self.nodeFunction)
        # print(self.myNavigationEngine.getNextNodeNames())
        self.SignImages = self._importModule("SignImages.py")
    
    def callBackEnd(self, functionName : str):
        if functionName == "Sign all images with current config file":
            myObject = self._createInstance(self.SignImages, "SignImages", self.myLogger)
            if os.name == "nt":
                print("WARNING: YOU CANNOT ADD HASHTREE FOOTER WITH FEC ROOTS WHEN RUNNING ON WINDOWS")
                print("AUTOMATICALLY SKIPPING FEC GENERATION")
                self._pressEnterToContinue()
            elif self.__isWSL()[1] and "/mnt" in os.getcwd():
                print("NOT RECOMMENDED TO RUN THIS PROGRAM IN WSL WITH SCRIPTS STORED IN NTFS WORLD")
                print("MAY RESULT IN EACCES OF PEM FILES")
                self._pressEnterToContinue()
            print()
            print("It may take up to minutes depending on your hardware config.")
            print("The program is still running normally, DO NOT KILL IT!")
            for i in range(5):
                print("Start signing after %d secs."%(5 - i))
                time.sleep(1)
            print()
            myObject.signImagesBatch()
            self._pressEnterToContinue()
        #elif functionName == "Sign selected image file":
            
    
    def __chooseImagesToSign(self):
        imageToDisplay : set = self.__getAvailableImageFiles()
        self.clearScreen()
        print("=" * 80)
        selectedImages = [False for i in range(len(imageToDisplay))]
        for i in imageToDisplay:
            print("%40s [ ]"%i)
        print("0 Selected.")
        
    
    def __getAvailableImageFiles(self):
        with open(
            os.path.join(os.getcwd(), "Core", "currentConfigs", "imageInfo.json"),
            "r",
            encoding = "UTF-8") as myFile:
            imageConfigDict : dict = json.load(myFile)
            imageAvailableInConfig : list = list(imageConfigDict.keys())
        imageDir = os.path.join(os.getcwd(), "Images")
        imageAvailableInWorkDir = []
        for i in os.listdir(imageDir):
            if "vbmeta" not in i:
                imageAvailableInWorkDir.append(i)
        set1 = set(imageAvailableInConfig)
        set2 = set(imageAvailableInWorkDir)
        return set1 & set2

    def __isWSL(self):
        wsl_env_vars = [
            'WSLENV',
            'WSL_DISTRO_NAME',
            'WSL_INTEROP',
            'WSL_UTF8'
        ]
        
        env_results = {}
        for var in wsl_env_vars:
            env_results[var] = os.environ.get(var, 'Not set')
        
        is_wsl = any(os.environ.get(var) for var in wsl_env_vars)
        return env_results, is_wsl