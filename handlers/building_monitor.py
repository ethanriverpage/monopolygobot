"""
building_monitor.py

This module contains the BuildingMonitor class, which is responsible for starting the building handler when the money reaches the target amount.
Runs as a loop in a separate thread.
"""

from threading import Thread
from handlers import building_handler
from shared_state import shared_state
from time import sleep
from utils.logger import logger
import json


class BuildingMonitor:
    def __init__(self):
        self.builder_running_condition = shared_state.builder_running_condition
        self.builder_running = shared_state.builder_running
        self.game_data_file = str(shared_state.WINDOW_TITLE.strip()) + "_game_data.json"
        self.update_build_start_amount()

    def set_builder_running(self, value):
        """
        Set the builder_running state and notify other threads.
        Args:
            value (bool): The value to set the builder_running state to.
        """
        with self.builder_running_condition:
            self.builder_running = value
            shared_state.builder_running = value
            sleep(0.2)
            self.builder_running_condition.notify_all()
        if value is True:
            shared_state.builder_event.set()
            shared_state.start_autoroller_lock.acquire(blocking=True)
            shared_state.start_disable_autoroller_lock.acquire(blocking=True)
            shared_state.stop_autoroller_lock.acquire(blocking=True)
            shared_state.stop_disable_autoroller_lock.acquire(blocking=True)
        if value is False:
            shared_state.builder_event.clear()
            shared_state.start_autoroller_lock.release()
            shared_state.start_disable_autoroller_lock.release()
            shared_state.stop_autoroller_lock.release()
            shared_state.stop_disable_autoroller_lock.release()

    def load_data(self):
        """
        Loads game data from the game_data_file.

        Returns:
            list: A list containing game data.
        """
        try:
            with open(self.game_data_file, "r") as f:
                logger.debug(f"[BUILD-M] Loaded data from {self.game_data_file}.")
                return json.load(f)

        except FileNotFoundError:
            logger.error("[BUILD-M] game_data.json not found.")
            return []

    def update_build_start_amount(self):
        """
        Update BUILD_START_AMOUNT based on the total cost of the most recent board.
        """
        data = self.load_data()
        most_recent_board = max(data, key=lambda x: x.get("board_number", 0))
        if "total_cost" in most_recent_board:
            total_cost = most_recent_board["total_cost"]
            shared_state.BUILD_START_AMOUNT = total_cost * 2
            logger.debug(
                f"[BUILD-M] Updated BUILD_START_AMOUNT to {shared_state.BUILD_START_AMOUNT}."
            )
        else:
            logger.debug("[BUILD-M] Failed to update BUILD_START_AMOUNT.")

    def run(self, ar_handler_instance):
        """
        Start the building handler when the money reaches the target amount.
        Handles starting and stopping the autoroller & disable_ autoroller.
        Args:
            ar_handler_instance (AutorollerHandler): The AutorollerHandler instance.
        """
        self.ar_handler_instance = ar_handler_instance
        shared_state.thread_barrier.wait()
        logger.debug("[BUILD-M] Received notification! Starting...")
        while True:
            with shared_state.money_condition:  # Wait for money to be updated
                shared_state.money_condition.wait()
                money = shared_state.money
            if shared_state.multiplier_handler_event.is_set():
                logger.debug("[BUILD-M] Waiting for multiplier handler to finish...")
                shared_state.multiplier_handler_event.wait()
                sleep(10)
            if not shared_state.multiplier_handler_event.is_set():
                if (  # Start building handler if money is more than set amount and building handler is not already running
                    not shared_state.builder_running
                    and money >= shared_state.BUILD_START_AMOUNT
                ):
                    logger.debug(
                        f"[BUILD-M] Money is more than set {shared_state.BUILD_START_AMOUNT}. Starting builder..."
                    )
                    self.set_builder_running(True)
                    if shared_state.autoroller_running:
                        logger.debug("[BUILD-M] Stopping autoroller...")
                        with shared_state.stop_autoroller_lock:
                            ar_handler_instance.stop_autoroller()
                            while (
                                shared_state.autoroller_running
                            ):  # Wait for autoroller to stop
                                with shared_state.autoroller_running_condition:
                                    shared_state.autoroller_running_condition.wait_for(
                                        lambda: not shared_state.autoroller_running
                                    )
                            logger.debug(
                                "[BUILD-M] Autoroller stopped in BuildingMonitor"
                            )
                        if not shared_state.disable_autoroller_running:
                            with shared_state.start_disable_autoroller_lock:
                                ar_handler_instance.start_disable_autoroller()
                                while (
                                    not shared_state.disable_autoroller_running
                                ):  # Wait for disable_autoroller to start
                                    with shared_state.disable_autoroller_running_condition:
                                        shared_state.disable_autoroller_running_condition.wait_for(
                                            lambda: shared_state.disable_autoroller_running
                                        )
                    while (
                        not shared_state.in_home_status
                    ):  # Wait for in_home_status to be updated
                        with shared_state.in_home_condition:
                            shared_state.in_home_condition.wait()
                    building_handler_instance = (
                        building_handler.BuildingHandler()
                    )  # Start building handler
                    if not hasattr(self, "building_handler_thread"):
                        self.building_handler_thread = Thread(
                            target=building_handler_instance.run,
                            daemon=False,
                            name="building_handler",
                        )
                        self.building_handler_thread.start()

                        logger.debug(
                            "[BUILD-M] Builder handler thread started in BuildingMonitor"
                        )
                    elif not self.building_handler_thread.is_alive():
                        self.building_handler_thread = Thread(
                            target=building_handler_instance.run,
                            daemon=False,
                            name="building_handler",
                        )
                        self.building_handler_thread.start()

                    with shared_state.builder_running_condition:
                        shared_state.builder_running = self.builder_running
                        shared_state.builder_running_condition.notify_all()

                    with shared_state.builder_finished_condition:  # Wait for building handler to finish
                        shared_state.builder_finished_condition.wait_for(
                            lambda: shared_state.builder_finished
                        )
                        logger.debug("[BUILD-M] Builder handler finished")

                    if (
                        shared_state.disable_autoroller_running
                    ):  # Start autoroller if disable_autoroller is running
                        logger.debug("[BUILD-M] Stopping disable_autoroller...")
                        with shared_state.stop_disable_autoroller_lock:
                            ar_handler_instance.stop_disable_autoroller()
                            with shared_state.disable_autoroller_running_condition:
                                shared_state.disable_autoroller_running_condition.wait_for(
                                    lambda: not shared_state.disable_autoroller_running
                                )
                    self.set_builder_running(False)  # Set builder_running to False
                elif (
                    not shared_state.builder_running
                    and money < shared_state.BUILD_START_AMOUNT
                ):  # Wait for money to be more than set amount
                    with shared_state.money_condition:
                        shared_state.money_condition.wait()
                        money = shared_state.money
                    self.update_build_start_amount()
                    with shared_state.builder_running_condition:
                        shared_state.builder_running_condition.wait_for(
                            lambda: money >= shared_state.BUILD_START_AMOUNT
                        )
                else:  # Wait for builder_running to be False
                    with shared_state.builder_running_condition:
                        shared_state.builder_running_condition.wait()
