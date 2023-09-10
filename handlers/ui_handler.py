from utils.image_cache import ImageCache
from utils.ocr_utils import OCRUtils
import glob
from pyautogui import locateOnScreen, center
from pydirectinput import click
from threading import Condition
from shared_state import shared_state
import os

image_cache = ImageCache()
ocr_utils = OCRUtils()

ui_handler_condition = Condition()


class UIHandler:
    def run(self):
        current_path = os.path.dirname(os.path.abspath(__file__))
        with ui_handler_condition:
            ui_handler_condition.wait()

        while True:
            for image_path in sorted(
                glob.glob(pathname=os.path.join(current_path, "images", "ui", "*.png"))
            ):
                target_image = image_cache.load_image(image_path)
                location = locateOnScreen(target_image)
                if location:
                    print(f"[UI] Detected {image_path}. Clicking...")
                    center_x, center_y = center(location)
                    click(center_x, center_y)
                    break
            if not shared_state.ui_handler_running:
                break
