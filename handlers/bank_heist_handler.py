from utils.ocr_utils import OCRUtils
from pyautogui import press
from time import sleep
from shared_state import shared_state
import os
from utils.logger import logger

ocr_utils = OCRUtils()


class BankHeistHandler:
    def __init__(self):
        self.current_path = shared_state.current_path
        self.bh_path = os.path.join(self.current_path, "images", "bank-heist-door.png")

    def run(self):
        shared_state.thread_barrier.wait()
        logger.debug("[HEIST] Received notification! Starting...")
        while shared_state.bank_heist_handler_running:
            if self.detect_and_execute(self.bh_path, "[HEIST] Bank heist detected."):
                sleep(5)
                with shared_state.press_lock:
                    press("num1")
                    sleep(5)

    def detect_and_execute(self, image_path, message):
        image = shared_state.load_image(image_path)
        point = ocr_utils.find(image)
        if point is not None:
            print(message)
            return True
        return False
