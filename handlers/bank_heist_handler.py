from utils.image_cache import ImageCache
from utils.ocr_utils import OCRUtils
from pyautogui import press
from time import sleep
from threading import Condition
from shared_state import shared_state
import os

image_cache = ImageCache()
ocr_utils = OCRUtils()

bank_heist_handler_condition = Condition()


class BankHeistHandler:
    def run(self):
        current_path = os.path.dirname(os.path.abspath(__file__))
        with bank_heist_handler_condition:
            bank_heist_handler_condition.wait()
            print("[HEIST] Received notification! Starting...")
        while True:
            bh_path = os.path.join(current_path, "..", "images", "bank-heist-door.png")
            mh_path = os.path.join(current_path, "..", "images", "megaheist.png")
            bh_image = image_cache.load_image(bh_path)
            mh_image = image_cache.load_image(mh_path)
            point = ocr_utils.find(bh_image)
            mh_point = ocr_utils.find(mh_image)
            if point is not None:
                print("[HEIST] Bank heist detected. Executing macro...")
                sleep(2)
                press("num1")
                sleep(5)
            elif mh_point is not None:
                print("[HEIST] Mega heist detected. Executing macro...")
                sleep(2)
                press("num1")
                sleep(5)
            if not shared_state.bank_heist_handler_running:
                print("[HEIST] I've been told to stop!")
                break
            sleep(1)
