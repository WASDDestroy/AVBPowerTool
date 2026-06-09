import os

import BaseUI
import Frontend.UIUtils as UIUtils
import Core.SignImages as SignImages
from Core import ConfigParser
from Core.ImageInfoUtils import ImageInfoUtils
from Core.Localization import t


class SignImagesUI(BaseUI.BaseUI):

    def customized_init(self):
        self.customized_function = {
            "S": {"id": "action:sign_selected_images", "label": t("sign.action.selected_image")},
        }

    def call_backend(self, function_name: str):
        if function_name == self.customized_function["S"]["id"]:
            self.handle_sign_selected_images()

        self.my_ui_utils.press_enter_to_continue()

    def handle_sign_selected_images(self):
        self.my_ui_utils.clear_screen()
        warn_words_before_signing = t("sign.warning_before_select")

        if self.my_ui_utils.confirm_operation(warn_words_before_signing):

            my_config_parser = ConfigParser.ConfigParser()

            # Get image with info stored in config file
            image_in_json = my_config_parser.get_image_in_json(
                os.path.join(os.getcwd(), "Core", "currentConfigs", "imageInfo.json"))
            if not image_in_json:
                self.my_ui_utils.message_on_cancel(t("sign.fetch_info_failed_cancel"))
                return
            set_json = set(image_in_json)
            self._my_logger.log("I", "Image configured in JSON file: " + str(set_json), self.TAG)

            # Get image in work dir
            image_in_work_dir = []
            for image in os.listdir(os.path.join(os.getcwd(), "Images")):
                if image.endswith(".img"):
                    image_in_work_dir.append(image[:-4])
            set_work_dir = set(image_in_work_dir)
            self._my_logger.log("I", "Images in work directory: " + str(set_work_dir), self.TAG)

            # Construct set of available images
            # Force to add vbmeta images to handle "other signing processes are successful, but vbmeta generation failed, and they are already removed by method for signing"
            set_available = set_json & set_work_dir
            for image_name in set_json:
                if "vbmeta" in image_name:
                    set_available.add(image_name)
            self._my_logger.log("I", "Available images: " + str(set_available), self.TAG)

            # Initialize selector and show it
            my_selector = UIUtils.EnhancedFileSelectorUI(t("sign.selector_title"), list(set_available), True,
                                                         True, True)
            images_to_sign = my_selector.show(allow_long_item=True)
            self._my_logger.log("I", "Sign selected images: " + str(images_to_sign), self.TAG)

            if len(images_to_sign) == 0:
                self.my_ui_utils.message_on_cancel(t("ui.no_option_selected"))
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

                        print(t("sign.unable_generate", image=vbmeta_image))

                        if not config_check_result[0]:
                            print(t("sign.missing_config_info"), end=" ")
                            for missing_config in config_check_result[1]:
                                print("\"%s\"" % missing_config, end=" ")
                        print()

                        if not workdir_check_result[0]:
                            print(t("sign.missing_workdir_image"), end=" ")
                            for missing_image in workdir_check_result[1]:
                                print("\"%s\"" % missing_image, end=" ")
                        print("\n")

            if allow_continue_generation:

                if images_to_sign:
                    cherry_pick_result = my_config_parser.cherry_pick_from_config(images_to_sign)
                    if cherry_pick_result:
                        if self.__is_wsl()[1] and "/mnt" in os.getcwd():
                            print(t("main.wsl_ntfs_warning_1"))
                            print(t("sign.wsl_pem_warning_2"))
                            self.my_ui_utils.message_on_fail(t("sign.improper_directory"))
                            self.my_ui_utils.press_enter_to_continue()
                            return
                        self.warn_before_signing()
                        my_signer = SignImages.SignImages()
                        batch_sign_result = my_signer.sign_images_batch(
                            os.path.join(os.getcwd(), "Core", "currentConfigs", "tempImageInfo.json"),
                            remove_vb=True if "vbmeta" in images_to_sign else False)
                        if batch_sign_result[0]:
                            print(t("sign.success"))
                        else:
                            print(t("sign.failed", error=str(batch_sign_result[1])))
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
        print()
        print(t("sign.wait_minutes"))
        print(t("sign.do_not_kill"))
        print()
