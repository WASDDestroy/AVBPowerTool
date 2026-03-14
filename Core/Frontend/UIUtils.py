import os
import sys
from typing import List, Set, Optional
import subprocess

import Core.ConfigManager as ConfigManager
import Core.LogUtils as LogUtils


class UIUtils:

    def __init__(self, logger=None) -> None:
        self.TAG = "UIUtils"
        if logger is None:
            self.my_logger = LogUtils.LogUtils(should_attach_time=True)
        else:
            self.my_logger = logger
        self.myConfigManager = ConfigManager.ConfigManager(
            logger=self.my_logger)
        self.my_logger.log(
            "I", "Successfully created UIUtils instance.", self.TAG)

    def clear_screen(self):

        def is_in_ide():
            if os.getenv('PYCHARM_HOSTED') == '1':
                return True
            if os.getenv('VSCODE_PID') is not None:
                return True
            return False

        try:
            self.my_logger.log("D", "Clear screen.", self.TAG)
            result = subprocess.run(["cls"], shell=True) if os.name == "nt" else subprocess.run(["clear"], shell=True)
            if result.returncode != 0 or is_in_ide():
                self.my_logger.log("W", "Unable to run command %s on platform %s, try alternate method to clear screen." % ("cls" if os.name == "nt" else "clear", os.name), self.TAG)
                supports_ansi = sys.stdout.isatty() and not (os.name == 'nt' and not os.getenv('ANSICON'))
                self.my_logger.log("D", "ANSI sequence support: %d" % supports_ansi, self.TAG)
                if supports_ansi:
                    sys.stdout.write("\033[2J\033[H")
                    sys.stdout.flush()
                else:
                    print("\n" * 100)
        except FileNotFoundError:
            self.my_logger.log("W", "Unable to run clear screen command on platform %s due to FileNotFoundError" % os.name, self.TAG)

    @staticmethod
    def press_enter_to_continue():
        input("Press Enter to continue.")

    def confirm_operation(self, prompt="Confirm operation?") -> bool:
        my_selector = EnhancedFileSelectorUI(prompt, ["Yes", "No"], False, self.my_logger, True, True)
        if my_selector.show(show_instructions=False)[0] == "Yes":
            return True
        else:
            return False
    @staticmethod
    def message_on_fail():
        print("Please refer to log file for further information.")
        print("Note: Exit tool, then check log file, otherwise nothing will be shown in latest log.")

class EnhancedFileSelectorUI:
    """
    An enhanced "file" selector.

    Supports keyboard navigation, multi-select and infinite roll.
    """

    def __init__(self, title: str = "Select Files", items: List[str] = None,
                 multi_select: bool = False, logger = None, infinite_roll = True, cancelable = True):  # type: ignore
        """
        Initialize a selector.

        :param title: Title of your selector interface
        :param items: Items shown in selector interface
        :param multi_select: Is multi-select supported
        :param logger: logger instance
        :param infinite_roll: Is infinite roll supported
        :param cancelable: Is cancelable (Use ESC to cancel)
        """
        self.title = title
        self.items = items or []
        self.multi_select = multi_select
        self.selected_indices: Set[int] = set()
        self.current_index = 0
        self.finished = False
        self.cancelled = False
        self.infinite_roll = infinite_roll
        self.cancelable = cancelable
        if logger is None:
            self.my_logger = LogUtils.LogUtils()
        else:
            self.my_logger = logger

    def show(self, show_instructions = True, allow_long_item = False) -> Optional[List[str]]:
        """
        Display selector and return selected item(s).
        :param show_instructions: Display instructions
        :param allow_long_item: Allow long item(more than 35 letters)
        :return: list: item(s) selected; None: On user cancellation
        """
        if not self.items:
            print("No items to select.")
            return None if not self.multi_select else []

        # Reset state
        self.selected_indices.clear()
        self.current_index = 0
        self.finished = False
        self.cancelled = False

        # Main loop
        while not self.finished:
            self._draw_ui(show_instructions, allow_long_item)
            self._process_input()

        # Return result when user cancels
        if self.cancelled:
            return None

        selected_items = [self.items[i] for i in sorted(self.selected_indices)]

        # Return only one item when in single-selection mode
        if not self.multi_select and selected_items:
            return [selected_items[0]]

        return selected_items

    def _draw_ui(self, show_instructions = True, allow_long_item = False) -> None:
        """
        Draw UI interface
        """
        my_ui_utils = UIUtils(logger=self.my_logger)
        my_ui_utils.clear_screen()

        # Show title
        print("=" * 80)
        title_line = f"  {self.title:^80}  "
        print(title_line)
        print("=" * 80)

        # Show instructions
        if show_instructions:
            print("  Instructions:")
            print("    ↑/↓ : Navigate items")
            if self.multi_select:
                print("    Space : Select/Deselect current item")
                print("    A     : Select All / Deselect All")
            print("    Enter : Confirm selection")
            if self.cancelable:
                print("    ESC   : Cancel")
            print("=" * 80)

        # Show selectable items
        if not self.items:
            print("  No items available.                          ")
        else:
            for i, item in enumerate(self.items):
                # Handle long names
                display_item = item
                if len(display_item) > 35 and not allow_long_item:
                    display_item = display_item[:32] + "..."

                # Prefix
                if i == self.current_index:
                    prefix = "→ "
                else:
                    prefix = "  "

                # Show checkbox
                if self.multi_select:
                    checkbox = "[✓]" if i in self.selected_indices else "[ ]"
                else:
                    checkbox = "[●]" if i in self.selected_indices else "[○]"

                # Finally construct the whole line
                line = f"{prefix}{checkbox} {display_item}"
                line = line.ljust(80)
                print(f"  {line}  ")

        print("=" * 80)

        # Show current state
        if self.multi_select:
            selected_count = len(self.selected_indices)
            status = f"Selected: {selected_count}/{len(self.items)}"
            print(f"  {status:^80}  ")
            print("=" * 80)

        # Show buttons
        if self.cancelable:
            print("  [Enter: Confirm]        [ESC: Cancel]")
        else:
            print("  [Enter: Confirm]")
        print("=" * 80)

    def _process_input(self) -> None:
        """
        Process user input
        """
        try:
            if os.name == 'nt':
                import msvcrt
                key = msvcrt.getch().decode('utf-8', errors='ignore')
            else:
                import tty
                import termios
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(sys.stdin.fileno())
                    key = sys.stdin.read(1)
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except (ImportError, Exception):
            # Fall back to standard input
            key = input("").lower()
            if len(key) > 0:
                key = key[0]
            else:
                key = ''

        # Handle special keys
        if key == '\x1b' and self.cancelable:  # ESC
            self.cancelled = True
            self.finished = True
            return

        elif key == '\r' or key == '\n':  # Enter
            # Select current item when in single-select mode
            if not self.multi_select and not self.selected_indices:
                self.selected_indices.add(self.current_index)
            self.finished = True
            return

        elif key in ['w', 'W', '\x48']:  # Up arrow or W
            if self.current_index > 0:
                self.current_index -= 1
            elif self.infinite_roll:
                self.current_index = len(self.items) - 1

        elif key in ['s', 'S', '\x50']:  # Down arrow or S
            if self.current_index < len(self.items) - 1:
                self.current_index += 1
            elif self.infinite_roll:
                self.current_index = 0

        elif key == ' ':  # Space
            if self.multi_select:
                # Multi-select mode
                if self.current_index in self.selected_indices:
                    self.selected_indices.remove(self.current_index)
                else:
                    self.selected_indices.add(self.current_index)
            else:
                # Single-select mode
                self.selected_indices.clear()
                self.selected_indices.add(self.current_index)

        elif key in ['a', 'A'] and self.multi_select:  # Select all
            if len(self.selected_indices) == len(self.items):
                # Cancel "select all"
                self.selected_indices.clear()
            else:
                # Select all
                self.selected_indices = set(range(len(self.items)))

    @staticmethod
    def _get_key() -> str:
        """
        Get keyboard input when arrow key navigation is unavailable.
        """
        try:
            import msvcrt
            return msvcrt.getch().decode('utf-8', errors='ignore')
        except (ImportError, Exception):
            return input("")[0] if input("") else ''