from threading import Thread
from handlers import multiplier_handler
from shared_state import shared_state
from time import sleep
from utils.logger import logger
import os
from utils.ocr_utils import OCRUtils

ocr_utils = OCRUtils()


class MultiplierMonitor:
    def __init__(self):
        self.multiplier_handler_running_condition = (
            shared_state.multiplier_handler_running_condition
        )
        self.multiplier_handler_running = shared_state.multiplier_handler_running
        self.high_roller_event = False

    def update_multiplier_handler_running(self, value):
        with self.multiplier_handler_running_condition:
            self.multiplier_handler_running = value
            shared_state.multiplier_handler_running = value
            sleep(0.2)
            shared_state.multiplier_handler_running_condition.notify_all()

    def calculate_correct_multiplier(self, rolls, event):
        if event:
            if rolls < 50:
                return 3
            elif rolls < 100:
                return 5
            elif rolls < 300:
                return 10
            elif rolls < 1000:
                return 200
            elif rolls < 5000:
                return 500
            elif rolls >= 5000:
                return 1000
            else:
                return 1
        if not event:
            if rolls < 50:
                return 3
            elif rolls < 100:
                return 5
            elif rolls < 300:
                return 10
            elif rolls < 1000:
                return 20
            elif rolls < 2000:
                return 50
            elif rolls >= 2000:
                return 100
            else:
                return 1

    def run(self, ar_handler_instance):
        self.ar_handler_instance = ar_handler_instance
        shared_state.thread_barrier.wait()
        logger.debug("[MP-M] Received notification! Starting...")
        with shared_state.rolls_condition:
            shared_state.rolls_condition.wait()
            rolls = shared_state.rolls
        hr_image_path = os.path.join(
            shared_state.current_path, "images", "high-roller.png"
        )
        hr_image = shared_state.load_image(hr_image_path)
        while True:
            if shared_state.builder_event.is_set():
                logger.debug("[MP-M] Waiting for builder to finish...")
                shared_state.builder_event.wait()
                sleep(10)
            if not shared_state.builder_event.is_set():
                with shared_state.rolls_condition:
                    shared_state.rolls_condition.wait()
                    rolls = shared_state.rolls
                with shared_state.multiplier_condition:
                    shared_state.multiplier_condition.wait()
                    multiplier = shared_state.multiplier
                builder_running = shared_state.builder_running
                hr_event = ocr_utils.find(hr_image)
                if hr_event is not None:
                    self.high_roller_event = True
                else:
                    self.high_roller_event = False
                if not builder_running:
                    if self.high_roller_event:
                        correct_multiplier = self.calculate_correct_multiplier(
                            rolls, event=True
                        )
                    else:
                        correct_multiplier = self.calculate_correct_multiplier(
                            rolls, event=False
                        )
                    if (
                        not shared_state.multiplier_handler_running
                        and multiplier < correct_multiplier
                    ):
                        logger.debug(
                            f"[MP-M] Multiplier should be {correct_multiplier}. Starting multiplier handler..."
                        )
                        shared_state.multiplier_handler_event.set()
                        if shared_state.autoroller_running:
                            logger.debug("[MP-M] Stopping autoroller...")
                            with shared_state.stop_autoroller_lock:
                                self.ar_handler_instance.stop_autoroller()
                                with shared_state.autoroller_running_condition:
                                    shared_state.autoroller_running_condition.wait_for(
                                        lambda: not shared_state.autoroller_running
                                    )
                                logger.debug(
                                    "[MP-M] Autoroller stopped in MultiplierMonitor"
                                )
                        if not shared_state.disable_autoroller_running:
                            with shared_state.start_disable_autoroller_lock:
                                self.ar_handler_instance.start_disable_autoroller()
                                with shared_state.disable_autoroller_running_condition:
                                    shared_state.disable_autoroller_running_condition.wait_for(
                                        lambda: shared_state.disable_autoroller_running
                                    )
                        multiplier_handler_thread = Thread(
                            target=multiplier_handler.MultiplierHandler(
                                correct_multiplier
                            ).run,
                            daemon=True,
                            name="multiplier_handler",
                        )
                        multiplier_handler_thread.start()
                        self.update_multiplier_handler_running(True)
                        with shared_state.multiplier_handler_running_condition:
                            shared_state.multiplier_handler_running_condition.wait_for(
                                lambda: shared_state.multiplier_handler_running
                            )

                        logger.debug(
                            "[MP-M] Multiplier handler thread started in MultiplierMonitor"
                        )
                        with shared_state.multiplier_handler_finished_condition:
                            shared_state.multiplier_handler_finished_condition.wait_for(
                                lambda: not shared_state.multiplier_handler_running
                            )
                        logger.debug("[MP-M] Multiplier handler finished")
                        self.update_multiplier_handler_running(False)
                    elif (
                        shared_state.multiplier_handler_running
                        and shared_state.multiplier >= correct_multiplier
                    ):
                        logger.debug(
                            f"[MP-M] Multiplier is {correct_multiplier}. Stopping multiplier handler..."
                        )
                        multiplier_handler_thread.join()
                        with shared_state.multiplier_handler_running_condition:
                            shared_state.multiplier_handler_running_condition.wait_for(
                                lambda: not shared_state.multiplier_handler_running
                            )
                        logger.debug(
                            "[MP-M] Multiplier handler thread stopped in MultiplierMonitor"
                        )
                        if shared_state.disable_autoroller_running:
                            logger.debug("[MP-M] Stopping disable_autoroller...")
                            with shared_state.stop_disable_autoroller_lock:
                                self.ar_handler_instance.stop_disable_autoroller()
                                with shared_state.disable_autoroller_running_condition:
                                    shared_state.disable_autoroller_running_condition.wait_for(
                                        lambda: not shared_state.disable_autoroller_running
                                    )
                    elif (
                        not shared_state.multiplier_handler_running
                        and multiplier == correct_multiplier
                    ):
                        with shared_state.multiplier_handler_running_condition:
                            shared_state.multiplier_handler_running = False
                            shared_state.multiplier_handler_running_condition.notify_all()
                        sleep(5)
                else:
                    logger.debug(
                        "[MP-M] Builder running. Waiting for builder to finish before starting multiplier handler..."
                    )
                    sleep(5)
