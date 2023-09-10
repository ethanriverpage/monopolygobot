from utils.image_cache import ImageCache
from utils.ocr_utils import OCRUtils
from time import sleep
from pyautogui import press
from shared_state import shared_state
import cv2
import numpy as np
import os

image_cache = ImageCache()
ocr_utils = OCRUtils()


class AutoRoller:
    def run() -> bool:
        while shared_state.autoroller_running:
            current_path = os.path.dirname(os.path.abspath(__file__))
            go_path = os.path.join(current_path, "..", "images", "go.png")
            go_image = image_cache.load_image(go_path)
            while shared_state.rolls >= shared_state.AR_MINIMUM_ROLLS:
                point = ocr_utils.find(go_image)
                if point is not None:
                    print("[AUTOROLL] AutoRoll is not active. AutoRolling...")
                    press("insert")
                    sleep(15)
                elif point is None and shared_state.autoroller_running is False:
                    break
                sleep(1)
                break
            else:
                print(f"[AUTOROLL] Rolls is under set {shared_state.rolls}. Waiting...")
                sleep(30)

        print("[AUTOROLL] Exiting gracefully...")


class DisableAutoRoller:
    def run() -> bool:
        while shared_state.disable_autoroller_running:
            current_path = os.path.dirname(os.path.abspath(__file__))
            image_path = os.path.join(current_path, "..", "images", "autoroll.png")
            ar_image = cv2.imread(image_path)
            while True:
                point = ocr_utils.find(ar_image)
                if point is not None:
                    print("[AUTOROLL] Disabling autoroll...")
                    press("insert")
                    sleep(5)
                elif point is None and shared_state.disable_autoroller_running is True:
                    break
                break
        print("[AUTOROLL] Exiting disable_autoroll...")
