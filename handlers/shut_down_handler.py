from pyautogui import moveTo
from pydirectinput import click
from utils.ocr_utils import OCRUtils
from shared_state import shared_state
import os
from time import sleep
from utils.logger import logger

ocr_utils = OCRUtils()


class ShutDownHandler:
    def run(self):
        current_path = shared_state.current_path
        sd_image_paths = [
            os.path.join(current_path, "images", "sd-marker-up.png"),
            os.path.join(current_path, "images", "sd-marker-down.png"),
        ]
        shared_state.thread_barrier.wait()
        logger.debug("[SD] Received notification! Starting...")
        while shared_state.shut_down_handler_running:
            for path in sd_image_paths:
                sd_image = shared_state.load_image(path=path)
                point = ocr_utils.find(sd_image)
                if point is not None:
                    print(
                        f"[SD] Marker detected at {point[0]}, {point[1]}. Clicking target..."
                    )
                    with shared_state.moveTo_lock:
                        moveTo(x=point[0], y=point[1])
                        click()
                    sleep(0.2)
                    shared_state.moveto_center()
                    break
                sleep(1)
        print("[SD] Exiting...")
