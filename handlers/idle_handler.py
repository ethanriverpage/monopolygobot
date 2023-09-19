from shared_state import shared_state
from utils.ocr_utils import OCRUtils
from pyautogui import moveTo
from utils.logger import logger
from pydirectinput import click
import re
from time import sleep
import os

ocr_utils = OCRUtils()


class IdleHandler:
    def __init__(self):
        self.window_width = shared_state.window_width
        self.window_height = shared_state.window_height
        self.window_center_x = shared_state.window_center_x
        self.window_center_y = shared_state.window_center_y
        self.friends_button_x = int(self.window_width * (83.8 / 100))
        self.friends_button_y = int(self.window_height * (90.7 / 100))
        self.exit_button_x = int(self.window_width * (47.4 / 100))
        self.exit_button_y = int(self.window_height * (96.8 / 100))
        self.invite_count_x_percent = 36.5
        self.invite_count_y_percent = 68.6
        self.invite_count_width_percent = 58.6
        self.invite_count_height_percent = 71.1
        self.share_button_path = os.path.join(
            shared_state.current_path, "images", "share_button.png"
        )
        self.invite_button_path = os.path.join(
            shared_state.current_path, "images", "invite-button.png"
        )
        self.share_button = shared_state.load_image(self.share_button_path)
        self.invite_button = shared_state.load_image(self.invite_button_path)
        self.in_friends_menu = False
        self.in_invite_menu = False
        # Calculate the coordinates of the button based on the above percentages relative to window size

    def gather_invite_count(self):
        process_settings = {
            "contrast_reduction_percentage": 0,
            "threshold_value": 75,
            "invert": False,
            "scale_factor": 4,
        }
        invite_count = ocr_utils.ocr_to_str(
            self.invite_count_x_percent,
            self.invite_count_y_percent,
            self.invite_count_width_percent,
            self.invite_count_height_percent,
            output_image_path="invite_count.png",
            ocr_settings="--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789/",
            process_settings=process_settings,
        )
        match = re.search(r"(\d+)/50", invite_count)
        if match:
            invite_count = int(match.group(1))
            return invite_count
        else:
            logger.debug("Failed to extract invite count")
            return -1

    def run(self):
        shared_state.thread_barrier.wait()
        logger.debug("[IDLE] Received notification! Starting...")

        while True:
            # Check conditions for idle actions
            rolls = shared_state.rolls
            money = shared_state.money
            builder_running = shared_state.builder_running
            autoroller_running = shared_state.autoroller_running
            multiplier_handler_running = shared_state.multiplier_handler_running
            if (
                rolls < shared_state.AR_RESUME_ROLLS
                and money < shared_state.BUILD_START_AMOUNT
                and not builder_running
                and not autoroller_running
                and not multiplier_handler_running
            ):
                logger.debug(
                    "[IDLE] Detected idle state. Checking for invite rewards..."
                )
                with shared_state.in_home_condition:
                    shared_state.in_home_condition.wait_for(
                        lambda: shared_state.in_home_status
                    )
                    in_home = shared_state.in_home_status
                with shared_state.rolling_condition:
                    shared_state.rolling_condition.wait_for(
                        lambda: not shared_state.rolling_status
                    )
                shared_state.idle_event.clear()
                sleep(5)
                # Stop UI Handler
                shared_state.idle_event.set()

                if in_home:  # If in home, move to friends button and click
                    with shared_state.moveTo_lock:
                        moveTo(self.friends_button_x, self.friends_button_y)
                        sleep(1)
                        click()
                    sleep(2)
                # Look for invite button
                invite_button = ocr_utils.find(self.invite_button)
                while (
                    not invite_button
                ):  # While the invite button isn't present, move to friends button and click
                    moveTo(self.friends_button_x, self.friends_button_y)
                    sleep(1)
                    click()
                    invite_button = ocr_utils.find(
                        self.invite_button
                    )  # Check again to see if invite button has been clicked
                sleep(2)
                if invite_button:  # If invite button is present, click it
                    # Move to invite button and click
                    with shared_state.moveTo_lock:
                        moveTo(invite_button)
                        sleep(1)
                        click()
                    sleep(2)
                in_menu = ocr_utils.find(self.share_button)  # Look for share button
                while (
                    not in_menu
                ):  # While the share button isn't present, move to invite button and click
                    invite_button = ocr_utils.find(self.invite_button)
                    if invite_button:
                        with shared_state.moveTo_lock:
                            moveTo(invite_button)
                            sleep(1)
                            click()
                    in_menu = ocr_utils.find(self.share_button)
                while in_menu:  # While the share button is present
                    invite_count = self.gather_invite_count()  # Gather the invite count
                    while (
                        invite_count == -1
                    ):  # If the invite count is -1, wait 3 seconds and check again
                        # Wait 5 seconds and check again
                        sleep(3)
                        invite_count = self.gather_invite_count()
                    if (
                        invite_count >= 0
                        and invite_count
                        not in [  # If the invite count is not in the following list, move to close button and click
                            5,
                            15,
                            30,
                            50,
                        ]
                    ):
                        sleep(2)
                        if invite_count not in [
                            5,
                            15,
                            30,
                            50,
                        ]:  # If the invite count is not in the following list, move to close button and click
                            # Move to close button and click
                            with shared_state.moveTo_lock:
                                moveTo(self.exit_button_x, self.exit_button_y)
                                click()
                                sleep(1)
                                click()
                                sleep(2)
                            shared_state.idle_event.clear()
                            break
                        shared_state.idle_event.clear()
                        break
                shared_state.moveto_center()
                # Start UI Handler again

            else:
                shared_state.idle_event.clear()
                with shared_state.rolls_condition:
                    shared_state.rolls_condition.wait()
                with shared_state.money_condition:
                    shared_state.money_condition.wait()
                sleep(1)
            sleep(45)
