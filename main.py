from sys import exit
from handlers.state_handler import StateHandler
from shared_state import shared_state
import keyboard
import time
from utils import set_console_title
from utils.player_info import PlayerInfo
from pytesseract import pytesseract

pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
player_info = PlayerInfo()


def main():
    state_handler = StateHandler()
    state_handler.start_player_info()
    while True:
        set_console_title.set_console_title()

        # Start building handler if over 100m

        if keyboard.is_pressed("F1"):
            print("[AUTOROLL] Toggling autoroll...")
            state_handler.toggle_autoroller()
            time.sleep(0.2)

        if keyboard.is_pressed("F2"):
            if not shared_state.bank_heist_handler_running:
                state_handler.start_bank_heist_handler()
            else:
                state_handler.stop_bank_heist_handler()
            time.sleep(0.2)

        if keyboard.is_pressed("F3"):
            if not shared_state.shut_down_handler_running:
                state_handler.start_shut_down_handler()
            else:
                state_handler.stop_shut_down_handler()
            time.sleep(0.2)

        if keyboard.is_pressed("F4"):
            if not shared_state.ui_handler_running:
                state_handler.start_ui_handler()
            else:
                state_handler.stop_ui_handler()
            time.sleep(0.2)

        if keyboard.is_pressed("F5"):
            if (
                shared_state.money >= shared_state.BUILD_START_AMOUNT
                and not shared_state.builder_running
            ):
                print(
                    f"[STATUS] Money is over set {shared_state.BUILD_START_AMOUNT}. Starting builder..."
                )
                state_handler.start_building_handler()
                time.sleep(0.2)
                """ while (
                    not shared_state.builder_running
                    and shared_state.money >= shared_state.BUILD_START_AMOUNT
                ):
                    print(
                        f"[STATUS] Money is over set {shared_state.BUILD_START_AMOUNT}. Starting builder..."
                    )
                    state_handler.start_building_handler()
                    time.sleep(0.2)
                    break """
            elif shared_state.money < shared_state.BUILD_START_AMOUNT:
                print("[STATUS] Not enough money to start builder.")
                time.sleep(0.2)
            else:
                print("[STATUS] Builder is already running!")
                time.sleep(0.2)


if __name__ == "__main__":
    main()
