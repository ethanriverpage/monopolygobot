from utils.image_cache import ImageCache
from utils.ocr_utils import OCRUtils
from time import sleep
from pyautogui import press
from shared_state import shared_state

image_cache = ImageCache()
ocr_utils = OCRUtils()


class AutoRoller:
    def run() -> bool:
        while shared_state.autoroller_running:
            go_image = image_cache.load_image(path="go.png")
            while shared_state.rolls >= shared_state.AR_MINIMUM_ROLLS:
                point = ocr_utils.find(go_image)
                if point is not None:
                    print("[AUTOROLL] AutoRoll is not active. AutoRolling...")
                    press("num0")
                    sleep(15)
                elif point is None and shared_state.autoroller_running is False:
                    break
                break
            else:
                print(f"[AUTOROLL] Rolls is under set {shared_state.rolls}. Waiting...")
                sleep(30)

        print("[AUTOROLL] Exiting gracefully...")


class DisableAutoRoller:
    def run() -> bool:
        while shared_state.disable_autoroller_running:
            ar_image = image_cache.load_image(path="autoroll.png")
            while True:
                point = ocr_utils.find(ar_image)
                if point is not None:
                    print("[AUTOROLL] Disabling autoroll...")
                    press("num0")
                    sleep(5)
                elif point is None and shared_state.disable_autoroller_running is True:
                    break
                break
        print("[AUTOROLL] Exiting disable_autoroll...")
