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
        rolls_region_percent = (34, 91.77, 58, 94.3)
        last_known_rolls = 0
        last_known_roll_capacity = None
        # Capture rolls information
        while True:
            x_percent, y_percent, right_percent, bottom_percent = rolls_region_percent
            rolls_text = ocr_utils.ocr_to_str(
                x_percent,
                y_percent,
                right_percent,
                bottom_percent,
                output_image_path="rolls-proc.png",
            )
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
            sleep(1)

    def run_money(self):
        money_region_percent = (33, 7.25, 62, 11)
        last_known_money = 0
        # Capture money information
        while True:
            x_percent, y_percent, right_percent, bottom_percent = money_region_percent
            money_text = ocr_utils.ocr_to_str(
                x_percent,
                y_percent,
                right_percent,
                bottom_percent,
                output_image_path="proc-money.png",
            )
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
            sleep(1)
