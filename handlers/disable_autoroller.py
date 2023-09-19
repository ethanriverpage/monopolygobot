from shared_state import shared_state
import os
from time import sleep
from pyautogui import moveTo
from pydirectinput import click
from utils.ocr_utils import OCRUtils
from utils.logger import logger

ocr_utils = OCRUtils()


class DisableAutoRoller:
    @staticmethod
    def run() -> bool:
        current_path = shared_state.current_path
        image_path = os.path.join(current_path, "images", "autoroll.png")
        ar_image = shared_state.load_image(image_path)
        disable_autoroller_running = True
        while disable_autoroller_running:
            with shared_state.disable_autoroller_running_condition:
                shared_state.disable_autoroller_running_condition.wait()
                disable_autoroller_running = shared_state.disable_autoroller_running
            if not disable_autoroller_running:
                break
            with shared_state.in_home_condition:
                shared_state.in_home_condition.wait_for(
                    lambda: shared_state.in_home_status
                )

            point = ocr_utils.find(ar_image)
            if point is not None:
                logger.debug("[AUTOROLL] AutoRoll is active. Disabling autoroll...")
                with shared_state.moveTo_lock:
                    moveTo(point[0], point[1])
                    sleep(0.2)
                    click()
            with shared_state.rolling_condition:
                shared_state.rolling_condition.wait_for(
                    lambda: shared_state.rolling_status, timeout=5
                )
        logger.debug("[AUTOROLL] Exiting disable_autoroll...")
