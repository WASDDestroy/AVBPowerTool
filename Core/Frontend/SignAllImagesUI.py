import BaseUI
import os
import time
import json


class SignAllImagesUI(BaseUI.BaseUI):

    def customized_init(self):
        self.TAG = "SignAllImagesUI"
        self.customized_function = {
            "Y": "Sign all images with current config file",
            "I": "Sign selected image file"
        }
        # print("Using navigation map: ", self.myNavigationEngine.currentFileDir)
        # print(self.myNavigationEngine.currentDic)
        # print(self.customizedFunction)
        # print(self.nodeFunction)
        # print(self.myNavigationEngine.getNextNodeNames())
        # noinspection PyAttributeOutsideInit
        self.SignImages = self.my_importer.import_module("SignImages.py")

    def call_backend(self, function_name: str):
        if function_name == "Sign all images with current config file":
            my_object = self.my_importer.create_instance(
                self.SignImages, "SignImages", self.my_logger)
            if os.name == "nt":
                print(
                    "WARNING: YOU CANNOT ADD HASHTREE FOOTER WITH FEC ROOTS WHEN RUNNING ON WINDOWS")
                print("AUTOMATICALLY SKIPPING FEC GENERATION")
                self.my_ui_utils.press_enter_to_continue()
            elif self.__is_wsl()[1] and "/mnt" in os.getcwd():
                print(
                    "NOT RECOMMENDED TO RUN THIS PROGRAM IN WSL WITH SCRIPTS STORED IN NTFS WORLD")
                print("MAY RESULT IN EACCES OF PEM FILES")
                self.my_ui_utils.press_enter_to_continue()
            print()
            print("It may take up to minutes depending on your hardware config.")
            print("The program is still running normally, DO NOT KILL IT!")
            for i in range(5):
                print("Start signing after %d secs." % (5 - i))
                time.sleep(1)
            print()
            my_object.sign_images_batch()
            self.my_ui_utils.press_enter_to_continue()
        elif function_name == "Sign selected image file":
            self._in_development_placeholder()

    def __choose_images_to_sign(self):
        image_to_display: set = self.__get_available_image_files()
        self.my_ui_utils.clear_screen()
        print("=" * 80)
        for i in image_to_display:
            print("%40s [ ]" % i)
        print("0 Selected.")

    @staticmethod
    def __get_available_image_files():
        with open(
            os.path.join(os.getcwd(), "Core",
                         "currentConfigs", "imageInfo.json"),
            "r",
                encoding="UTF-8") as myFile:
            image_config_dict: dict = json.load(myFile)
            image_available_in_config: list = list(image_config_dict.keys())
        image_dir = os.path.join(os.getcwd(), "Images")
        image_available_in_work_dir = []
        for i in os.listdir(image_dir):
            if "vbmeta" not in i:
                image_available_in_work_dir.append(i)
        set1 = set(image_available_in_config)
        set2 = set(image_available_in_work_dir)
        return set1 & set2

    @staticmethod
    def __is_wsl():
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
