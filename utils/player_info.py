from .ocr_utils import OCRUtils
from pytesseract import image_to_string
import re
import numpy as np
from pyautogui import screenshot
from threading import Thread
from shared_state import shared_state
from time import sleep

ocr_utils = OCRUtils()


class PlayerInfo:
    money = shared_state.money
    rolls = shared_state.rolls

    def run_rolls(self):
        rolls_region = (1169, 1274, 191, 38)
        last_known_rolls = 0
        last_known_roll_capacity = None
        # Capture rolls information
        while True:
            rolls_screenshot = screenshot(region=rolls_region)
            rolls_screenshot_np = np.array(rolls_screenshot)
            target_size = (573, 114)
            preprocessed_rolls = ocr_utils.preprocess_image(
                rolls_screenshot_np,
                contrast_reduction_percentage=-50,
                target_size=target_size,
            )
            rolls_text = image_to_string(preprocessed_rolls)
            rolls_text_e = re.sub(
                r"([^0-9/])", "", rolls_text
            )  # remove all characters except digits and /
            # Extract current rolls and roll capacity as integers
            rolls_parts = rolls_text_e.split("/")
            if len(rolls_parts) == 2:
                try:
                    rolls = int(rolls_parts[0].strip())
                    roll_capacity = int(rolls_parts[1].strip())
                    last_known_rolls = rolls
                    last_known_roll_capacity = roll_capacity
                    self.rolls = rolls
                except ValueError:
                    rolls = last_known_rolls
                    roll_capacity = last_known_roll_capacity
                    self.rolls = rolls
            else:
                rolls = last_known_rolls
                roll_capacity = last_known_roll_capacity
                self.rolls = rolls
            shared_state.rolls = self.rolls

    def run_money(self):
        money_region = (1148, 66, 226, 56)
        last_known_money = 0
        # Capture money information
        while True:
            money_screenshot = screenshot(region=money_region)
            money_text = image_to_string(money_screenshot)
            money_text = "".join(filter(str.isdigit, money_text))

            if money_text.isdigit():
                money = int(money_text)
                last_known_money = money
                self.money = money
                shared_state.money = self.money
            else:
                money = last_known_money
                self.money = money
                shared_state.money = self.money
