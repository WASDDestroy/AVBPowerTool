import os
import time

import BaseUI
import Core.SignImages as SignImages
import Core.Frontend.UIUtils as UIUtils
from Core import ConfigParser


class SignAllImagesUI(BaseUI.BaseUI):

    def customized_init(self):
        self.customized_function = {
            "Y": "Sign all images with current config file",
            "I": "Sign selected image file"
        }

    def call_backend(self, function_name: str):
        if function_name == "Sign all images with current config file":
            if self.my_ui_utils.confirm_operation():
                self.warn_before_signing()
                my_signer = SignImages.SignImages(self.my_logger)
                batch_sign_result = my_signer.sign_images_batch()
                if batch_sign_result[0]:
                    print("Successfully signed all images!")
                else:
                    print("Failed to sign images:")
                    print("Reason:", batch_sign_result[1])
                    self.my_ui_utils.message_on_fail()
            else:
                self.my_ui_utils.message_on_cancel()
        elif function_name == "Sign selected image file":
            self.warn_before_selective_signing()
            if self.my_ui_utils.confirm_operation("Continue?"):
                my_config_parser = ConfigParser.ConfigParser(self.my_logger)
                image_in_json = my_config_parser.get_image_in_json(
                    os.path.join(os.getcwd(), "Core", "currentConfigs", "imageInfo.json"))
                set_json = set(image_in_json)
                image_in_work_dir = []
                for image in os.listdir(os.path.join(os.getcwd(), "Images")):
                    if image.endswith(".img"):
                        image_in_work_dir.append(image.rstrip(".img"))
                set_work_dir = set(image_in_work_dir)
                set_available = set_json & set_work_dir
                for image_name in set_json:
                    if "vbmeta" in image_name:
                        set_available.add(image_name)
                my_selector = UIUtils.EnhancedFileSelectorUI("Select image file(s) to sign",
                                                             list(set_available),
                                                             True,
                                                             self.my_logger,
                                                             self.my_ui_utils,
                                                             True,
                                                             True)
                images_to_sign = my_selector.show(allow_long_item=True)
                self.my_logger.log("I", "Sign selected images: " + str(images_to_sign), self.TAG)
                if images_to_sign:
                    cherry_pick_result = my_config_parser.cherry_pick_from_config(images_to_sign)
                    if cherry_pick_result:
                        self.warn_before_signing()
                        my_signer = SignImages.SignImages(self.my_logger)
                        batch_sign_result = my_signer.sign_images_batch(
                            os.path.join(os.getcwd(), "Core", "currentConfigs", "tempImageInfo.json"), remove_vb= True if "vbmeta" in images_to_sign else False)
                        if batch_sign_result[0]:
                            print("Successfully signed selected images!")
                        else:
                            print("Failed to sign selected images! Error: ", batch_sign_result[1])
                            self.my_ui_utils.message_on_fail()
                    else:
                        self.my_ui_utils.message_on_fail()
                    my_config_parser.remove_cherry_pick_file()
                else:
                    self.my_ui_utils.message_on_cancel()
            else:
                self.my_ui_utils.message_on_cancel()

        self.my_ui_utils.press_enter_to_continue()


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

    def warn_before_signing(self):
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
        for i in range(3):
            print("Start signing after %d secs." % (3 - i))
            time.sleep(1)
        print()

    def warn_before_selective_signing(self):
        print("Attention! Some images has their AVB info stored in vbmeta (vbmeta, vbmeta_system, vbmeta_vendor, etc.),")
        print("Make sure you have clear understanding of what will happen after you signed images with this function.")
        self.my_ui_utils.press_enter_to_continue()