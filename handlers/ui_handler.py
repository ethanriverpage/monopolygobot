from utils.ocr_utils import OCRUtils
from pyautogui import moveTo
from pydirectinput import click
from shared_state import shared_state
import os
from utils.logger import logger
from time import sleep

ocr_utils = OCRUtils()


class UIHandler:
    def __init__(self):
        self.last_clicked_image = None

    def run(self):
        current_path = shared_state.current_path
        ui_images_path = os.path.join(current_path, "images", "ui")

        shared_state.thread_barrier.wait()
        logger.debug("[UI] Received notification! Starting...")

        image_files = [
            os.path.join(ui_images_path, file)
            for file in os.listdir(ui_images_path)
            if os.path.isfile(os.path.join(ui_images_path, file))
        ]

        while True:
            if shared_state.idle_event.is_set():
                shared_state.idle_event.wait()
            if not shared_state.idle_event.is_set():
                for image_path in image_files:
                    if shared_state.idle_event.is_set():
                        shared_state.idle_event.wait()
                    target_image = shared_state.load_image(image_path)
                    location = ocr_utils.find(target_image)
                    if location:
                        print(f"[UI] Detected {image_path}. Clicking...")
                        with shared_state.moveTo_lock:
                            moveTo(location[0], location[1])
                            click()
                        self.last_clicked_image = image_path
                        shared_state.moveto_center()
                        break
            sleep(0.5)
