import os

import BaseUI
from Core.Frontend.UIUtils import EnhancedFileSelectorUI
import Core.ImageInfoUtils as ImageInfoUtils
import Core.ConfigParser as ConfigParser


class ReadImageInfoUI(BaseUI.BaseUI):

    def customized_init(self):
        self.TAG = "ReadImageInfoUI"
        self.customized_function = {
            "S": "Read info of selected image(s)",
        }
        # noinspection PyAttributeOutsideInit
        self.my_image_info_utils = ImageInfoUtils.ImageInfoUtils()
        # noinspection PyAttributeOutsideInit
        self.m_config_parser = ConfigParser.ConfigParser()

    def call_backend(self, function_name: str):
        # if function_name == "Read info of all images":
        #     self.__handle_read_all_images_info()
        if function_name == "Read info of selected image(s)":
            self.__handle_read_selected_images_info()
        self.my_ui_utils.press_enter_to_continue()

    def __handle_read_selected_images_info(self):
        if self.my_ui_utils.confirm_operation("If you are going to create a signing config, this operation is strongly NOT recommended!",
                                              ("I understand, continue operation", "No, cancel operation")):
            available_images = os.listdir(os.path.join(os.getcwd(), "Images"))
            my_selector = EnhancedFileSelectorUI("Select Image(s) to Read", available_images, True, True, True)
            images_to_read = my_selector.show()
            if images_to_read:
                print("Reading selected images.")
                self.my_logger.log("I", "Read selected image(s).", self.TAG)
                for i in range(len(images_to_read)):
                    if images_to_read[i].endswith(".img"):
                        images_to_read[i] = images_to_read[i][:-4]
                self.my_image_info_utils.read_image_info_batch(images_to_read)
                print("Successfully read info of selected images.")
            else:
                self.my_logger.log("I", "No image selected.", self.TAG)
                print("No image selected! Tip: Use space to select file in multi-select mode and Enter to confirm your choice.")
                self.my_ui_utils.message_on_cancel()
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
