import os

import BaseUI
from Frontend.UIUtils import EnhancedFileSelectorUI
import Core.ImageInfoUtils as ImageInfoUtils
import Core.ConfigParser as ConfigParser
from Core.Localization import t


class ReadImageInfoUI(BaseUI.BaseUI):

    def customized_init(self):
        self.TAG = "ReadImageInfoUI"
        self.customized_function = {
            "S": {"id": "action:read_selected_images", "label": t("read.action.selected_images")},
        }
        # noinspection PyAttributeOutsideInit
        self.my_image_info_utils = ImageInfoUtils.ImageInfoUtils()
        # noinspection PyAttributeOutsideInit
        self.m_config_parser = ConfigParser.ConfigParser()

    def call_backend(self, function_name: str):
        # if function_name == "Read info of all images":
        #     self.__handle_read_all_images_info()
        if function_name == self.customized_function["S"]["id"]:
            self.__handle_read_selected_images_info()
        self.my_ui_utils.press_enter_to_continue()

    def __handle_read_selected_images_info(self):
        if self.my_ui_utils.confirm_operation(t("read.signing_config_warning"),
                                              (t("read.understand_continue"), t("read.cancel_operation"))):
            available_images = os.listdir(os.path.join(os.getcwd(), "Images"))
            my_selector = EnhancedFileSelectorUI(t("read.selector_title"), available_images, True, True, True)
            images_to_read = my_selector.show()
            if images_to_read:
                print(t("read.reading_selected"))
                self._my_logger.log("I", "Read selected image(s).", self.TAG)
                for i in range(len(images_to_read)):
                    if images_to_read[i].endswith(".img"):
                        images_to_read[i] = images_to_read[i][:-4]
                self.my_image_info_utils.read_image_info_batch(images_to_read)
                print(t("read.selected_success"))
            else:
                self._my_logger.log("I", "No image selected.", self.TAG)
                print(t("read.no_image_selected"))
        else:
            self.my_ui_utils.message_on_cancel()

    # def __handle_read_all_images_info(self):
    #     if self.confirm_operation():
    #         check_result = self.my_image_info_utils.check_image_exists(
    #             image_info_list=self.m_config_parser.get_image_list())
    #         if not check_result[0]:
    #             print("WARNING: Image mismatch!")
    #             if check_result[1] == "MORE":
    #                 print("These images are unnecessary, consider remove them:")
    #                 for i in check_result[2]:
    #                     print(i)
    #             elif check_result[1] == "LESS":
    #                 print(
    #                     "These images are missing, you must have them to continue process:")
    #                 for i in check_result[2]:
    #                     print(i)
    #             elif check_result[1] == "DIFF":
    #                 print("Necessary image(s) not found!")
    #                 print("Config list:")
    #                 for i in self.m_config_parser.get_image_list():
    #                     print(i)
    #                 print("You have these images:")
    #                 for i in check_result[3]:
    #                     print(i)
    #             return
    #         else:
    #             try:
    #                 print("Reading AVB information of all images.")
    #                 self.my_image_info_utils.read_image_info_batch(
    #                     self.m_config_parser.get_image_list())
    #                 print("Successfully read info of all images.")
    #             except:
    #                 print("Operation failed.")
    #     else:
    #         self.my_ui_utils.message_on_cancel()
