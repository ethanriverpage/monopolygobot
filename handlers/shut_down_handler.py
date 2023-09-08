from pyautogui import moveTo
from pydirectinput import click
from utils.image_cache import ImageCache
from utils.ocr_utils import OCRUtils
from shared_state import shared_state
from threading import Condition

image_cache = ImageCache()
ocr_utils = OCRUtils()

shut_down_handler_condition = Condition()


class ShutDownHandler:
    def run(self):
        with shut_down_handler_condition:
            shut_down_handler_condition.wait()
        while True:
            sd_image_paths = ["sd-marker-down.png", "sd-marker-up.png"]
            for path in sd_image_paths:
                sd_image = image_cache.load_image(path=path)
                point = ocr_utils.find(sd_image)
                if point is not None:
                    print(
                        f"[SD] Marker detected at {point.x}, {point.y}. Clicking target..."
                    )
                    moveTo(x=point.x, y=point.y, duration=0.2)
                    click()
                    break
            if not shared_state.shut_down_handler_running:
                break
