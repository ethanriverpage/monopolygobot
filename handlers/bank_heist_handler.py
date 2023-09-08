from utils.image_cache import ImageCache
from utils.ocr_utils import OCRUtils
from pyautogui import press
from time import sleep
from threading import Condition
from shared_state import shared_state

image_cache = ImageCache()
ocr_utils = OCRUtils()

bank_heist_handler_condition = Condition()


class BankHeistHandler:
    def run(self):
        with bank_heist_handler_condition:
            bank_heist_handler_condition.wait()
            print("[HEIST] Received notification! Starting...")
        while True:
            bh_image = image_cache.load_image(path="bank-heist-door.png")
            mh_image = image_cache.load_image(path="megaheist.png")
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
