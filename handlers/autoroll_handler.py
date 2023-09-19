"""
autoroll_handler.py

Autoroller handler. This handler is responsible for starting and stopping the autoroller and disable_autoroller threads.
"""

from threading import Thread
from handlers.autoroller import AutoRoller
from handlers.disable_autoroller import DisableAutoRoller
from shared_state import shared_state
from utils.logger import logger
from time import sleep


class AutoRollHandler:
    """
    Initialize the AutoRollHandler class.

    This class manages the autoroller and disable_autoroller threads.
    """

    def __init__(self):
        self.autoroller_running_condition = shared_state.autoroller_running_condition
        self.disable_autoroller_running_condition = (
            shared_state.disable_autoroller_running_condition
        )
        logger.debug("Autoroller handler initialized")

    def initialize(self):
        """
        Initialize the autoroller and disable_autoroller threads.
        """
        if (
            not shared_state.autoroller_running
            and not shared_state.disable_autoroller_running
        ):
            logger.debug("autoroller_running and disable_autoroller_running are False")
            self.set_autoroller_running(False)
            self.set_disable_autoroller_running(False)

    def set_autoroller_running(self, autoroller_running):
        """
        Set the autoroller_running flag.
        """
        with self.autoroller_running_condition:
            self.autoroller_running = autoroller_running
            shared_state.autoroller_running = autoroller_running
            logger.debug(
                f"Updated autoroller_running to {autoroller_running}. Notifying..."
            )
            self.autoroller_running_condition.notify_all()

    def set_disable_autoroller_running(self, running):
        """
        Set the disable_autoroller_running flag.
        """
        with self.disable_autoroller_running_condition:
            self.disable_autoroller_running = running
            shared_state.disable_autoroller_running = running
            logger.debug(
                f"Updated disable_autoroller_running to {running}. Notifying..."
            )
            self.disable_autoroller_running_condition.notify_all()

    # start the autoroll thread of autoroller.py
    def start_autoroller(self):
        """
        Start the autoroller thread of autoroller.py.
        """
        with shared_state.autoroller_running_condition:
            shared_state.autoroller_running_condition.wait_for(
                lambda: not shared_state.autoroller_running
            )
        if not shared_state.autoroller_running:
            self.autoroller_thread = Thread(
                target=AutoRoller.run, daemon=True, name="autoroller"
            )
            self.set_autoroller_running(True)
            self.autoroller_thread.start()
        with shared_state.autoroller_running_condition:
            shared_state.autoroller_running_condition.wait_for(
                lambda: shared_state.autoroller_running
            )
        logger.debug("Autoroller thread started in start_autoroller")

    # stop the autoroll thread of autoroller.py
    def stop_autoroller(self):
        """
        Stop the autoroller thread of autoroller.py.
        """
        if shared_state.autoroller_running:
            self.set_autoroller_running(False)
            self.autoroller_thread.join()
            logger.debug("Autoroller thread joined in stop_autoroller")
        logger.debug("Autoroller thread stopped in stop_autoroller")

    # start the disable_autoroll thread of disable_autoroller.py
    def start_disable_autoroller(self):
        """
        Start the disable_autoroller thread of disable_autoroller.py.
        """
        with shared_state.disable_autoroller_running_condition:
            shared_state.disable_autoroller_running_condition.wait_for(
                lambda: not shared_state.disable_autoroller_running
            )
        if not shared_state.disable_autoroller_running:
            self.disable_autoroller_thread = Thread(
                target=DisableAutoRoller.run, daemon=True, name="disable_autoroller"
            )
            self.set_disable_autoroller_running(True)
            self.disable_autoroller_thread.start()
        with shared_state.disable_autoroller_running_condition:
            shared_state.disable_autoroller_running_condition.wait_for(
                lambda: shared_state.disable_autoroller_running
            )
        logger.debug("Disable autoroller thread started in start_disable_autoroller")

    # stop the disable_autoroll thread of disable_autoroller.py
    def stop_disable_autoroller(self):
        """
        Stop the disable_autoroller thread of disable_autoroller.py.
        """
        if self.disable_autoroller_thread.is_alive():
            self.set_disable_autoroller_running(False)
            self.disable_autoroller_thread.join()
            logger.debug("Disable autoroller thread joined in stop_disable_autoroller")
        logger.debug("Disable autoroller thread stopped in stop_disable_autoroller")

    def update_running_status(self):
        """
        Update the autoroller_running and disable_autoroller_running flags.
        """
        while True:
            with shared_state.autoroller_running_condition:
                shared_state.autoroller_running = self.autoroller_running
                shared_state.autoroller_running_condition.notify_all()
            with shared_state.disable_autoroller_running_condition:
                shared_state.disable_autoroller_running = (
                    self.disable_autoroller_running
                )
                shared_state.disable_autoroller_running_condition.notify_all()
            break

    def run(self):
        """
        Main execution loop for the AutoRollHandler.
        """
        shared_state.thread_barrier.wait()
        logger.debug("[AR-H] Received notification! Starting...")
        self.initialize()
        while True:
            self.update_running_status()
            sleep(0.1)
