from dotenv import load_dotenv
from os import getenv as env
from threading import Condition, Lock, Barrier, Event, RLock
import pygetwindow as gw
from utils.image_cache import ImageCache
import os
from pyautogui import moveTo

load_dotenv()
image_cache = ImageCache()


class SharedState:
    AR_MINIMUM_ROLLS = int(env("AR_MINIMUM_ROLLS"))
    AR_RESUME_ROLLS = int(env("AR_RESUME_ROLLS"))
    # BUILD_START_AMOUNT = int(env("BUILD_START_AMOUNT"))
    BUILD_FINISH_AMOUNT = int(env("BUILD_FINISH_AMOUNT"))
    WINDOW_TITLE = env("WINDOW_TITLE")

    def __init__(self):
        self.window = gw.getWindowsWithTitle(self.WINDOW_TITLE)[0]
        self.window_x = self.window.left
        self.window_y = self.window.top
        self.window_width = self.window.width
        self.window_height = self.window.height
        self.window_center_x = int(self.window_width / 2)
        self.window_center_y = int(self.window_height / 2)
        self.window_right = self.window_x + self.window_width
        self.window_bottom = self.window_y + self.window_height
        self.window = (
            self.window_x,
            self.window_y,
            self.window_width,
            self.window_height,
        )
        self.window_coords = (
            self.window_x,
            self.window_y,
            self.window_right,
            self.window_bottom,
        )
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        # Variables
        self.autoroll_handler_running = False
        self.autoroller_running = False
        self.autoroller_thread_is_alive = False
        self.disable_autoroller_running = False
        self.disable_autoroller_thread_is_alive = False
        self.autoroll_monitor_running = False

        self.builder_running = False
        self.building_monitor_running = False
        self.building_handler_thread_is_alive = False
        self.builder_finished = False

        self.bank_heist_handler_running = False
        self.shut_down_handler_running = False
        self.ui_handler_running = False
        self.idle_handler_running = False

        self.multiplier_handler_running = False
        self.multiplier_monitor_running = False

        self.money = 0
        self.rolls = 0
        self.multiplier = 1
        self.BUILD_START_AMOUNT = 1
        self.rolling_status = False
        self.in_home_status = True
        # Conditions
        self.autoroll_handler_condition = Condition()
        self.autoroll_handler_running_condition = Condition()
        self.autoroller_running_condition = Condition()
        self.disable_autoroller_running_condition = Condition()
        self.autoroll_monitor_condition = Condition()

        self.building_monitor_condition = Condition()
        self.builder_running_condition = Condition()
        self.builder_finished_condition = Condition()

        self.bank_heist_condition = Condition()
        self.shut_down_condition = Condition()
        self.ui_condition = Condition()
        self.idle_condition = Condition()

        self.multiplier_condition = Condition()
        self.multiplier_monitor_condition = Condition()
        self.multiplier_handler_running_condition = Condition()
        self.multiplier_handler_finished_condition = Condition()

        self.rolls_condition = Condition()
        self.money_condition = Condition()
        self.rolling_condition = Condition()
        self.in_home_condition = Condition()
        # Locks
        self.multiplier_monitor_lock = Lock()
        self.autoroller_lock = Lock()
        self.moveTo_lock = Lock()
        self.press_lock = Lock()
        self.start_autoroller_lock = RLock()
        self.stop_autoroller_lock = RLock()
        self.start_disable_autoroller_lock = RLock()
        self.stop_disable_autoroller_lock = RLock()
        # Thread barrier
        self.thread_barrier = Barrier(8)
        # Events
        self.multiplier_handler_event = Event()
        self.builder_event = Event()
        self.idle_event = Event()

    def load_image(self, path: str):
        return image_cache.load_image(path)

    def save_cache(self, path: str):
        image_cache.save_cache(path)

    def load_cache(self, path: str):
        image_cache.load_cache(path)

    def initialize_cache(self, directory: str, recursive=True):
        image_cache.initialize_cache(directory, recursive)

    def moveto_center(self):
        with self.moveTo_lock:
            moveTo(self.window_center_x, self.window_center_y, duration=0.2)


shared_state = SharedState()
