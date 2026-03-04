import BaseUI
class ReadImageInfoUI(BaseUI.BaseUI):

    def customizedInit(self):
        self.TAG = "ReadImageInfoUI"
        self.customizedFunction = {
            "A" : "Read info of all images",
            "S" : "Read info of selected image(s) (NOT RECOMMENDED)",
        }
        self.mImageInfoUtils = self._createInstance(self._importModule("ImageInfoUtils"),
                                                    "ImageInfoUtils",
                                                    self.myLogger)
        self.mConfigParser = self._createInstance(self._importModule("ConfigParser"),
                                                  "ConfigParser",
                                                  self.myLogger)
    
    def callBackEnd(self, functionName: str):
        self.handleBackAndExit(functionName)
        if functionName == "Read info of all images":
            if self.confirmOperation():
                checkResult = self.mImageInfoUtils.checkImageExists(imageInfoList = self.mConfigParser.getImageList())
                if not checkResult[0]:
                    print("WARNING: Image mismatch!")
                    if checkResult[1] == "MORE":
                        print("These images are unnecessary, consider remove them:")
                        for i in checkResult[2]:
                            print(i)
                    elif checkResult[1] == "LESS":
                        print("These images are missing, you must have them to continue process:")
                        for i in checkResult[2]:
                            print(i)
                    elif checkResult[1] == "DIFF":
                        print("Necessary image(s) not found!")
                        print("Config list:")
                        for i in self.mConfigParser.getImageList():
                            print(i)
                        print("You have these images:")
                        for i in checkResult[3]:
                            print(i)
                    self._pressEnterToContinue()
                    return
                else:
                    try:
                        self.mImageInfoUtils.readImageInfoBatch(self.mConfigParser.getImageList())
                        print("Successfully read info of all images.")
                    except:
                        print("Operation failed.")
            else:
                print("Operation cancelled.")
            self._pressEnterToContinue()
        #elif functionName == "Read info of selected image(s) (NOT RECOMMENDED)":