import os
import time

import BaseUI
import Core.SignImages as SignImages

class SignAllImagesUI(BaseUI.BaseUI):

    def customized_init(self):
        self.customized_function = {
            "Y": "Sign all images with current config file",
            "I": "Sign selected image file"
        }

    def call_backend(self, function_name: str):
        if function_name == "Sign all images with current config file":
            my_signer = SignImages.SignImages(self.my_logger)
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
            batch_sign_result = my_signer.sign_images_batch()
            if batch_sign_result[0]:
                print("Successfully signed all images!")
            else:
                print("Failed to sign images:")
                print("Reason:", batch_sign_result[1])
                self.my_ui_utils.message_on_fail()
            self.my_ui_utils.press_enter_to_continue()
        elif function_name == "Sign selected image file":
            self._in_development_placeholder()

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
