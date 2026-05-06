import Core.Frontend.BaseUI as BaseUI
import Core.Frontend.DisplayAVBInfo as DisplayAVBInfo

class HomePageUI(BaseUI.BaseUI):

    def customized_init(self):
        self.TAG = "HomePageUI"
        self.customized_function = {
            "V": "View current config info"
        }
        # noinspection PyAttributeOutsideInit

    def call_backend(self, function_name: str):
        if function_name == "View current config info":
            DisplayAVBInfo.entry()  # type: ignore


if __name__ == "__main__":
    myHomePage = HomePageUI()
    while 1:
        myHomePage.entry()
