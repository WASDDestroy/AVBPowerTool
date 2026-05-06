import os

import BaseUI
import Core.Frontend.UIUtils as UIUtils
import Core.SignImages as SignImages
from Core import ConfigParser
from Core.ImageInfoUtils import ImageInfoUtils


class SignImagesUI(BaseUI.BaseUI):

    def customized_init(self):
        self.customized_function = {
            "S": "Sign selected image file",
        }

    def call_backend(self, function_name: str):
        if function_name == "Sign selected image file":
            self.handle_sign_selected_images()

        self.my_ui_utils.press_enter_to_continue()

    def handle_sign_selected_images(self):
        self.my_ui_utils.clear_screen()
        warn_words_before_signing =  ("Attention! Some images has their AVB info stored in vbmeta (vbmeta, vbmeta_system, vbmeta_vendor, etc.),"
                                      + "\n" + "Make sure you have clear understanding of what will happen after you signed images with this function."
                                      + "\n" + "Continue?")

        if self.my_ui_utils.confirm_operation(warn_words_before_signing):

            my_config_parser = ConfigParser.ConfigParser()

            # Get image with info stored in config file
            image_in_json = my_config_parser.get_image_in_json(
                os.path.join(os.getcwd(), "Core", "currentConfigs", "imageInfo.json"))
            if not image_in_json:
                self.my_ui_utils.message_on_cancel("Failed to fetch information about selected images! Cancelling.")
                return
            set_json = set(image_in_json)
            self.my_logger.log("I", "Image configured in JSON file: " + str(set_json), self.TAG)

            # Get image in work dir
            image_in_work_dir = []
            for image in os.listdir(os.path.join(os.getcwd(), "Images")):
                if image.endswith(".img"):
                    image_in_work_dir.append(image.rstrip(".img"))
            set_work_dir = set(image_in_work_dir)
            self.my_logger.log("I", "Images in work directory: " + str(set_work_dir), self.TAG)

            # Construct set of available images
            # Force to add vbmeta images to handle "other signing processes are successful, but vbmeta generation failed, and they are already removed by method for signing"
            set_available = set_json & set_work_dir
            for image_name in set_json:
                if "vbmeta" in image_name:
                    set_available.add(image_name)
            self.my_logger.log("I", "Available images: " + str(set_available), self.TAG)

            # Initialize selector and show it
            my_selector = UIUtils.EnhancedFileSelectorUI("Select image file(s) to sign", list(set_available), True,
                                                         True, True)
            images_to_sign = my_selector.show(allow_long_item=True)
            self.my_logger.log("I", "Sign selected images: " + str(images_to_sign), self.TAG)

            if len(images_to_sign) == 0:
                self.my_ui_utils.message_on_cancel("No option selected, cancelling.")
                self.my_ui_utils.press_enter_to_continue()
                return

            # Get vbmeta images
            vbmeta_images = []
            for image_name in images_to_sign:
                if "vbmeta" in image_name:
                    vbmeta_images.append(image_name)

            allow_continue_generation = True  # Handle vbmeta generation, set to false if images we have currently does not contain sufficient info to generate vbmeta images

            # If request generate vbmeta image, check is this operation performable
            if len(vbmeta_images) > 0:
                my_image_info_utils = ImageInfoUtils()
                for vbmeta_image in vbmeta_images:
                    config_check_result = my_image_info_utils.is_config_support_vbmeta_generation("current",
                                                                                                  vbmeta_image)
                    workdir_check_result = my_image_info_utils.is_work_dir_support_vbmeta_generation("current",
                                                                                                     vbmeta_image)

                    if not (config_check_result[0] and workdir_check_result[0]):
                        allow_continue_generation = False

                        # Show failure reasons

                        print("Unable to generate image \"%s\":" % vbmeta_image)

                        if not config_check_result[0]:
                            print("- Config does not satisfy requirements: missing AVB info of image ", end="")
                            for missing_config in config_check_result[1]:
                                print("\"%s\"" % missing_config, end=" ")
                        print()

                        if not workdir_check_result[0]:
                            print("- Workdir does not satisfy requirements: missing image file of ", end="")
                            for missing_image in workdir_check_result[1]:
                                print("\"%s\"" % missing_image, end=" ")
                        print("\n")

            if allow_continue_generation:

                if images_to_sign:
                    cherry_pick_result = my_config_parser.cherry_pick_from_config(images_to_sign)
                    if cherry_pick_result:
                        if self.__is_wsl()[1] and "/mnt" in os.getcwd():
                            print("NEVER RUN THIS PROGRAM IN WSL WITH SCRIPTS STORED IN NTFS WORLD")
                            print("MAY RESULT IN PERMISSION DENIAL OF PEM FILES")
                            self.my_ui_utils.message_on_fail("Improper directory, move complete project directory to Linux world and restart the program.")
                            self.my_ui_utils.press_enter_to_continue()
                            return
                        self.warn_before_signing()
                        my_signer = SignImages.SignImages()
                        batch_sign_result = my_signer.sign_images_batch(
                            os.path.join(os.getcwd(), "Core", "currentConfigs", "tempImageInfo.json"),
                            remove_vb=True if "vbmeta" in images_to_sign else False)
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
                self.my_ui_utils.message_on_fail()
        else:
            self.my_ui_utils.message_on_cancel()

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

    @staticmethod
    def warn_before_signing():
        if os.name == "nt":
            print(
                "WARNING: YOU CANNOT ADD HASHTREE FOOTER WITH FEC ROOTS WHEN RUNNING ON WINDOWS")
            print("AUTOMATICALLY SKIPPING FEC GENERATION")
        print()
        print("It may take up to minutes depending on your hardware config.")
        print("The program is still running normally, DO NOT KILL IT!")
        print()
