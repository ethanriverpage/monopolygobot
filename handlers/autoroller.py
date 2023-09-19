from utils.ocr_utils import OCRUtils
from pyautogui import press
from shared_state import shared_state
import os
from utils.logger import logger
from time import sleep

ocr_utils = OCRUtils()


class AutoRoller:
    @staticmethod
    def run() -> bool:
        current_path = shared_state.current_path
        go_path = os.path.join(current_path, "images", "go.png")
        go_image = shared_state.load_image(go_path)
        autoroller_running = True
        while autoroller_running:  # While autoroller is running
            with shared_state.autoroller_running_condition:
                shared_state.autoroller_running_condition.wait()  # Update autoroller_running status
                autoroller_running = shared_state.autoroller_running
            if not autoroller_running:  # If autoroller_running is False,
                break  # break the loop
            with shared_state.in_home_condition:  # Wait for in_home_status to be updated
                shared_state.in_home_condition.wait_for(
                    lambda: shared_state.in_home_status
                )

            point = ocr_utils.find(go_image)
            if point is not None:
                logger.debug("[AUTOROLL] AutoRoll is not active. AutoRolling...")
                with shared_state.press_lock:
                    press("num0")
                    sleep(10)
            with shared_state.rolling_condition:
                shared_state.rolling_condition.wait_for(
                    lambda: not shared_state.rolling_status, timeout=5
                )
        logger.debug("[AUTOROLL] Exiting autoroll...")
