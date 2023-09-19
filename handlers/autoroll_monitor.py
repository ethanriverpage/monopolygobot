from shared_state import shared_state
from utils.logger import logger
from time import sleep


class AutorollMonitor:
    def __init__(self):
        """
        Initalize the AutorollMonitor class.

        This class monitors various conditions and manages the autoroller thread.
        """
        self.ar_handler_instance = None
        self.current_rolls = shared_state.rolls
        self.minimum_rolls = shared_state.AR_MINIMUM_ROLLS
        self.resume_rolls = shared_state.AR_RESUME_ROLLS

    def run(self, ar_handler_instance):
        """
        Start the AutorollMonitor.
        Monitors roll count and starts/stops the autoroller thread as needed.
        """
        self.ar_handler_instance = ar_handler_instance
        shared_state.thread_barrier.wait()
        logger.debug("[AR-M] Received notification! Starting...")
        while True:
            if shared_state.builder_event.is_set():
                logger.debug("[AR-M] Waiting for builder to finish...")
                shared_state.builder_event.wait()
                sleep(10)
            if shared_state.multiplier_handler_event.is_set():
                logger.debug("[AR-M] Waiting for multiplier handler to finish...")
                shared_state.multiplier_handler_event.wait()
                sleep(10)

            if (
                not shared_state.builder_event.is_set()
                and not shared_state.multiplier_handler_event.is_set()
            ):
                with shared_state.builder_running_condition:
                    shared_state.builder_running_condition.wait(timeout=5)
                builder_running = shared_state.builder_running
                with shared_state.multiplier_handler_running_condition:
                    shared_state.multiplier_handler_running_condition.wait(timeout=5)
                multiplier_handler_running = shared_state.multiplier_handler_running

                if not multiplier_handler_running and not builder_running:
                    with shared_state.autoroller_running_condition:
                        shared_state.autoroller_running_condition.wait()
                        autoroller_running = shared_state.autoroller_running
                    with shared_state.disable_autoroller_running_condition:
                        shared_state.disable_autoroller_running_condition.wait()
                        disable_autoroller_running = (
                            shared_state.disable_autoroller_running
                        )
                    with shared_state.rolls_condition:
                        shared_state.rolls_condition.wait()
                        self.current_rolls = shared_state.rolls
                    if self.current_rolls < self.minimum_rolls and autoroller_running:
                        logger.debug(
                            "[AR-M] Rolls are less than minimum rolls. Stopping autoroller..."
                        )
                        if autoroller_running:
                            with shared_state.stop_autoroller_lock:
                                ar_handler_instance.stop_autoroller()
                                with shared_state.autoroller_running_condition:
                                    shared_state.autoroller_running_condition.wait_for(
                                        lambda: not shared_state.autoroller_running
                                    )
                        if not disable_autoroller_running:
                            with shared_state.start_disable_autoroller_lock:
                                ar_handler_instance.start_disable_autoroller()
                                with shared_state.disable_autoroller_running_condition:
                                    shared_state.disable_autoroller_running_condition.wait_for(
                                        lambda: shared_state.disable_autoroller_running
                                    )
                    if (
                        self.current_rolls >= self.resume_rolls
                        and not autoroller_running
                    ):
                        logger.debug(
                            "[AR-M] Rolls are greater than resume rolls. Starting autoroller..."
                        )
                        if disable_autoroller_running:
                            with shared_state.stop_disable_autoroller_lock:
                                ar_handler_instance.stop_disable_autoroller()
                                with shared_state.disable_autoroller_running_condition:
                                    shared_state.disable_autoroller_running_condition.wait_for(
                                        lambda: not shared_state.disable_autoroller_running
                                    )
                        if not autoroller_running:
                            with shared_state.start_autoroller_lock:
                                ar_handler_instance.start_autoroller()
                                with shared_state.autoroller_running_condition:
                                    shared_state.autoroller_running_condition.wait_for(
                                        lambda: shared_state.autoroller_running
                                    )

                    with shared_state.rolls_condition:
                        shared_state.rolls_condition.wait_for(
                            lambda: shared_state.rolls != self.current_rolls
                        )
                        self.current_rolls = shared_state.rolls
                else:
                    if shared_state.idle_event.is_set():
                        logger.debug("[AR-M] Paused. Waiting to resume...")
                        shared_state.idle_event.wait()
                    if not shared_state.idle_event.is_set():
                        continue
                    with shared_state.builder_running_condition:
                        shared_state.builder_running_condition.wait_for(
                            lambda: not shared_state.builder_running
                        )
                    with shared_state.multiplier_handler_running_condition:
                        shared_state.multiplier_handler_running_condition.wait_for(
                            lambda: not shared_state.multiplier_handler_running
                        )
