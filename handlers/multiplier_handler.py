from shared_state import shared_state
from pyautogui import moveTo
from pydirectinput import click
from utils.logger import logger
import time


class MultiplierHandler:
    """
    MultiplierHandler handles changing the multiplier.
    It is started by MultiplierMonitor when the multiplier is incorrect.
    """

    def __init__(self, correct_multiplier, timeout=30):
        self.correct_multiplier = correct_multiplier
        self.multiplier = shared_state.multiplier
        (
            self.window_x,
            self.window_y,
            self.window_width,
            self.window_height,
        ) = shared_state.window
        self.timeout = timeout
        mp_region_percent = (61, 70.5, 71, 73.3)
        left_percent, top_percent, right_percent, bottom_percent = mp_region_percent
        self.center_x = (
            self.window_x + self.window_width * (left_percent + right_percent) / 200
        )
        self.center_y = (
            self.window_y + self.window_height * (top_percent + bottom_percent) / 200
        )

    def run(self):
        with shared_state.in_home_condition:
            logger.debug("[MP-H] Not on home screen. Waiting...")
            shared_state.in_home_condition.wait_for(lambda: shared_state.in_home_status)
        logger.debug("[MP-H] On home screen. Starting...")
        start_time = time.time()
        while self.multiplier != self.correct_multiplier:
            shared_state.multiplier_handler_event.set()
            with shared_state.moveTo_lock:
                moveTo(self.center_x, self.center_y)
                click()
            with shared_state.multiplier_condition:
                shared_state.multiplier_condition.wait()
                self.multiplier = shared_state.multiplier
            elapsed_time = time.time() - start_time
            if self.multiplier == self.correct_multiplier:
                logger.debug("[MP-H] Multiplier correct. Exiting...")
                break
            if elapsed_time >= self.timeout:
                logger.debug("[MP-H] Timeout reached. Exiting...")
                break
            logger.debug("[MP-H] Multiplier updated. Checking...")
        shared_state.moveto_center()
        shared_state.multiplier_handler_event.clear()
        with shared_state.multiplier_handler_finished_condition:
            logger.debug("[MP-H] Exiting...")
            shared_state.multiplier_handler_running = False
            shared_state.multiplier_handler_finished_condition.notify_all()
