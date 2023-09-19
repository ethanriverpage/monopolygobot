import ctypes
from shared_state import shared_state
from time import sleep
from threading import Thread
from .logger import logger


class SetConsoleTitle:
    def __init__(self):
        """
        This class is used to update the console title with the current status of the bot.
        All the variables used to update the title are shared with the main thread.
        """
        # Conditions
        self.autoroller_running_condition = shared_state.autoroller_running_condition
        self.disable_autoroller_running_condition = (
            shared_state.disable_autoroller_running_condition
        )
        self.rolls_condition = shared_state.rolls_condition
        self.money_condition = shared_state.money_condition
        self.builder_running_condition = shared_state.builder_running_condition
        self.building_monitor_condition = shared_state.building_monitor_condition
        self.multiplier_condition = shared_state.multiplier_condition
        self.multiplier_handler_running_condition = (
            shared_state.multiplier_handler_running_condition
        )
        self.multiplier_monitor_condition = shared_state.multiplier_monitor_condition
        # Variables
        self.ar_state = "unknown"
        self.rolls_state = 0
        self.money_state = 0
        self.builder_state = "unknown"
        self.multiplier_state = 0
        self.multiplier_status_state = "unknown"
        self.status = ""

    def update_ar_state(self):
        """
        This method is used to update the autoroller state.
        """
        ar_running = shared_state.autoroller_running
        dar_running = shared_state.disable_autoroller_running
        while True:
            if shared_state.autoroller_running:
                self.ar_state = (
                    "WAITING"
                    if shared_state.rolls != shared_state.AR_MINIMUM_ROLLS
                    else "RUNNING"
                )
            if shared_state.disable_autoroller_running:
                self.ar_state = "DISABLED"
            else:
                self.ar_state = "OFF"
            with self.autoroller_running_condition:
                self.autoroller_running_condition.wait_for(
                    lambda: shared_state.autoroller_running != ar_running
                )
            ar_running = shared_state.autoroller_running
            with self.disable_autoroller_running_condition:
                self.disable_autoroller_running_condition.wait_for(
                    lambda: shared_state.disable_autoroller_running != dar_running
                )
            dar_running = shared_state.disable_autoroller_running

    def update_rolls_state(self):
        """
        This method is used to update the rolls state.
        """
        while True:
            with self.rolls_condition:
                self.rolls_condition.wait_for(
                    lambda: shared_state.rolls != self.rolls_state
                )
            self.rolls_state = shared_state.rolls

    def update_money_state(self):
        """
        This method is used to update the money state.
        """
        while True:
            with self.money_condition:
                self.money_condition.wait_for(
                    lambda: shared_state.money != self.money_state
                )
            self.money_state = shared_state.money

    def update_builder_state(self):
        """
        This method is used to update the builder state.
        """
        builder_running = shared_state.builder_running
        building_monitor_running = shared_state.building_monitor_running
        while True:
            self.builder_state = (
                "RUNNING"
                if builder_running
                else (
                    "WAITING"
                    if building_monitor_running and not builder_running
                    else "OFF"
                )
            )
            with self.builder_running_condition:
                self.builder_running_condition.wait_for(
                    lambda: shared_state.builder_running != builder_running
                )
            builder_running = shared_state.builder_running
            with self.building_monitor_condition:
                self.building_monitor_condition.wait_for(
                    lambda: shared_state.building_monitor_running
                    != building_monitor_running
                )
            building_monitor_running = shared_state.building_monitor_running

    def update_multiplier_status_state(self):
        multiplier_monitor_running = shared_state.multiplier_monitor_running
        multiplier_handler_running = shared_state.multiplier_handler_running
        self.multiplier_status_state = (
            "RUNNING"
            if multiplier_handler_running
            else (
                "WAITING"
                if multiplier_monitor_running and not multiplier_handler_running
                else "OFF"
            )
        )
        with self.multiplier_monitor_condition:
            self.multiplier_monitor_condition.wait_for(
                lambda: shared_state.multiplier_monitor_running
                != multiplier_monitor_running
            )
        multiplier_monitor_running = shared_state.multiplier_monitor_running
        with self.multiplier_handler_running_condition:
            self.multiplier_handler_running_condition.wait_for(
                lambda: shared_state.multiplier_handler_running
                != multiplier_handler_running
            )
        multiplier_handler_running = shared_state.multiplier_handler_running

    def update_multiplier_state(self):
        """
        This method is used to update the multiplier state.
        """
        while True:
            with self.multiplier_condition:
                self.multiplier_condition.wait_for(
                    lambda: shared_state.multiplier != self.multiplier_state
                )
            self.multiplier_state = shared_state.multiplier

    def run(self):
        """
        This method is used to update the console title with the current status of the bot.
        """
        threads = [
            Thread(
                target=self.update_rolls_state,
                daemon=True,
                name="set_console_title.rolls_state",
            ),
            Thread(
                target=self.update_money_state,
                daemon=True,
                name="set_console_title.money_state",
            ),
            Thread(
                target=self.update_ar_state,
                daemon=True,
                name="set_console_title.ar_state",
            ),
            Thread(
                target=self.update_builder_state,
                daemon=True,
                name="set_console_title.builder_state",
            ),
            Thread(
                target=self.update_multiplier_state,
                daemon=True,
                name="set_console_title.multiplier_state",
            ),
            Thread(
                target=self.update_multiplier_status_state,
                daemon=True,
                name="set_console_title.multiplier_status_state",
            ),
        ]
        for thread in threads:
            thread.start()

        while True:
            self.status = f"[STATUS] AutoRoll: {self.ar_state} | Rolls: {self.rolls_state} | Money: {self.money_state} | Multiplier: {self.multiplier_state} (Monitor: {self.multiplier_status_state}) | Builder: {self.builder_state}"
            ctypes.windll.kernel32.SetConsoleTitleW(self.status)
            sleep(0.2)
