from dotenv import load_dotenv
from os import getenv as env
from threading import Thread

load_dotenv()


class SharedState:
    AR_MINIMUM_ROLLS = int(env("AR_MINIMUM_ROLLS"))
    BUILD_START_AMOUNT = int(env("BUILD_START_AMOUNT"))
    BUILD_FINISH_AMOUNT = int(env("BUILD_FINISH_AMOUNT"))
    WINDOW_TITLE = str(env("WINDOW_TITLE"))

    def __init__(self):
        self.bank_heist_handler_running = False
        self.builder_running = False
        self.autoroller_running = False
        self.autoroller_thread_is_alive = False
        self.disable_autoroller_running = False
        self.disable_autoroller_thread_is_alive = False
        self.shut_down_handler_running = False
        self.ui_handler_running = False
        self.money = 0
        self.rolls = 0


shared_state = SharedState()
