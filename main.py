from sys import exit
from shared_state import shared_state
from handlers.state_handler import StateHandler
from utils.set_console_title import SetConsoleTitle
from utils.player_info import PlayerInfo
from pytesseract import pytesseract
from time import sleep
from pynput import keyboard
import os
from utils.logger import logger

# Set up tesseract
pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
# Initialize class instances
player_info = PlayerInfo()
set_console_title = SetConsoleTitle()
state_handler = StateHandler()


def on_key_press(key):
    if key == keyboard.Key.f1:
        print("[STATUS] Toggling autoroll...")
        logger.info("[STATUS] Toggling autoroll...")
        sleep(0.2)
        state_handler.toggle_autoroll_handler()
        sleep(0.2)

    elif key == keyboard.Key.f2:
        print("[STATUS] Toggling bank heist handler...")
        logger.info("[STATUS] Toggling bank heist handler...")
        sleep(0.2)
        state_handler.toggle_bank_heist_handler()
        sleep(0.2)

    elif key == keyboard.Key.f3:
        print("[STATUS] Toggling shut down handler...")
        logger.info("[STATUS] Toggling shut down handler...")
        sleep(0.2)
        state_handler.toggle_shut_down_handler()
        sleep(0.2)

    elif key == keyboard.Key.f4:
        print("[STATUS] Toggling UI handler...")
        logger.info("[STATUS] Toggling UI handler...")
        sleep(0.2)
        state_handler.toggle_ui_handler()
        sleep(0.2)

    elif key == keyboard.Key.f5:
        print("[STATUS] Toggling building monitor...")
        logger.info("[STATUS] Toggling building monitor...")
        sleep(0.2)
        state_handler.toggle_building_monitor()
        sleep(0.2)

    elif key == keyboard.Key.f6:
        print("[STATUS] Toggling multiplier monitor...")
        logger.info("[STATUS] Toggling multiplier monitor...")
        sleep(0.2)
        state_handler.toggle_multiplier_monitor()
        sleep(0.2)

    elif key == keyboard.Key.f7:
        print("[STATUS] Toggling autoroll monitor...")
        logger.info("[STATUS] Toggling autoroll monitor...")
        sleep(0.2)
        state_handler.toggle_autoroll_monitor()
        sleep(0.2)

    elif key == keyboard.Key.page_up:
        print("[STATUS] Starting all handlers...")
        logger.info("[STATUS] Starting all handlers...")
        sleep(0.2)
        try:
            state_handler.toggle_autoroll_handler()
            sleep(0.2)
            state_handler.toggle_building_monitor()
            sleep(0.2)
            state_handler.toggle_bank_heist_handler()
            sleep(0.2)
            state_handler.toggle_shut_down_handler()
            sleep(0.2)
            state_handler.toggle_ui_handler()
            sleep(0.2)
            state_handler.toggle_multiplier_monitor()
            sleep(0.2)
            state_handler.toggle_autoroll_monitor()
            sleep(0.2)
            state_handler.toggle_idle_handler()
            sleep(0.2)
        except Exception as e:
            print(e)
            logger.error(e)
            exit()
    elif key == keyboard.Key.f12:
        print("[STATUS] Exiting...")
        logger.info("[STATUS] Exiting...")
        shared_state.save_cache("image_cache.pkl")
        exit()


def init_cache():
    if os.path.exists("image_cache.pkl"):
        shared_state.load_cache("image_cache.pkl")
    else:
        shared_state.initialize_cache("images")
        shared_state.save_cache("image_cache.pkl")


init_cache()
logger.debug("Cache initialized.")


def main():
    state_handler.start_player_info()
    state_handler.start_set_console_title()

    with keyboard.Listener(on_press=on_key_press) as listener:
        listener.join()


if __name__ == "__main__":
    logger.info("Starting...")

    main()
