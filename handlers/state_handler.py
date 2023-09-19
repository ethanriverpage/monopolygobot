from threading import Thread
from shared_state import shared_state
from utils.player_info import PlayerInfo
from utils.set_console_title import SetConsoleTitle
from handlers import (
    autoroll_handler,
    bank_heist_handler,
    shut_down_handler,
    ui_handler,
    building_monitor,
    multiplier_monitor,
    autoroll_monitor,
    idle_handler,
)
from time import sleep
from utils.logger import logger

player_info = PlayerInfo()
set_console_title = SetConsoleTitle()


class StateHandler:
    def __init__(self):
        self.ar_handler_instance = autoroll_handler.AutoRollHandler()

    def start_player_info(self):
        threads = [
            Thread(target=player_info.run, daemon=True, name="player_info"),
        ]
        for thread in threads:
            thread.start()

    def start_set_console_title(self):
        threads = [
            Thread(target=set_console_title.run, daemon=True, name="set_console_title"),
        ]
        for thread in threads:
            thread.start()

    def start_autoroll_monitor(self):
        autoroll_monitor_instance = autoroll_monitor.AutorollMonitor()
        autoroll_monitor_thread = Thread(
            target=autoroll_monitor_instance.run,
            kwargs={"ar_handler_instance": self.ar_handler_instance},
            daemon=True,
            name="autoroll_monitor",
        )
        shared_state.autoroll_monitor_running = True
        autoroll_monitor_thread.start()
        while not autoroll_monitor_thread.is_alive():
            if autoroll_monitor_thread.is_alive():
                logger.debug(
                    "[STATE] Autoroll monitor thread initialized successfully."
                )
            else:
                logger.debug("[STATE] Waiting for autoroll monitor thread to start.")
                sleep(1)
        logger.debug("[STATE] Notifying autoroll monitor thread...")
        with shared_state.autoroll_monitor_condition:
            sleep(0.2)
            shared_state.autoroll_monitor_condition.notify_all()
            logger.debug("[STATE] Autoroll monitor thread notified.")
            shared_state.autoroll_monitor_running = True

    def start_autoroll_handler(self):
        autoroll_handler_thread = Thread(
            target=self.ar_handler_instance.run,
            daemon=True,
            name="autoroll_handler",
        )
        shared_state.autoroll_handler_running = True
        autoroll_handler_thread.start()
        while not autoroll_handler_thread.is_alive():
            if autoroll_handler_thread.is_alive():
                logger.debug(
                    "[STATE] Autoroll handler thread initialized successfully."
                )
            else:
                logger.debug("[STATE] Waiting for autoroll handler thread to start.")
                sleep(1)
        logger.debug("[STATE] Notifying autoroll handler thread...")
        with shared_state.autoroll_handler_condition:
            sleep(0.2)
            shared_state.autoroll_handler_condition.notify_all()
            logger.debug("[STATE] Autoroll handler thread notified.")
            shared_state.autoroll_handler_running = True

    def start_building_monitor(self):
        building_monitor_instance = building_monitor.BuildingMonitor()
        building_monitor_thread = Thread(
            target=building_monitor_instance.run,
            kwargs={
                "ar_handler_instance": self.ar_handler_instance
            },  # Pass the current state_handler
            daemon=True,
            name="building_monitor",
        )
        shared_state.building_monitor_running = True
        building_monitor_thread.start()
        while not building_monitor_thread.is_alive():
            if building_monitor_thread.is_alive():
                logger.debug(
                    "[STATE] Building monitor thread initialized successfully."
                )
            else:
                logger.debug("[STATE] Waiting for building monitor thread to start.")
                sleep(1)
        logger.debug("[STATE] Notifying building monitor thread...")
        with shared_state.building_monitor_condition:
            sleep(0.2)
            shared_state.building_monitor_condition.notify()
            logger.debug("[STATE] Building monitor thread notified.")
            shared_state.building_monitor_running = True

    def start_multiplier_monitor(self):
        multiplier_monitor_instance = multiplier_monitor.MultiplierMonitor()
        multiplier_monitor_thread = Thread(
            target=multiplier_monitor_instance.run,
            kwargs={
                "ar_handler_instance": self.ar_handler_instance
            },  # Pass the current ar_handler_instance
            daemon=True,
            name="multiplier_monitor",
        )
        shared_state.multiplier_monitor_running = True
        multiplier_monitor_thread.start()
        while not multiplier_monitor_thread.is_alive():
            if multiplier_monitor_thread.is_alive():
                logger.debug(
                    "[STATE] Multiplier monitor thread initialized successfully."
                )
            else:
                logger.debug("[STATE] Waiting for multiplier monitor thread to start.")
                sleep(1)
        logger.debug("[STATE] Notifying multiplier monitor thread...")
        with shared_state.multiplier_monitor_condition:
            sleep(0.2)
            shared_state.multiplier_monitor_condition.notify()
            logger.debug("[STATE] Multiplier monitor thread notified.")
            shared_state.multiplier_monitor_running = True

    def _toggle_handler(self, handler_name, is_running_key, thread_key, thread_target):
        if not getattr(shared_state, is_running_key):
            # Start the handler
            setattr(shared_state, is_running_key, True)
            thread = Thread(target=thread_target, daemon=True, name=thread_key)
            setattr(self, thread_key, thread)
            thread.start()
            logger.debug(f"[{handler_name}] {handler_name} started. Notifying...")
            while not thread.is_alive():
                if thread.is_alive():
                    logger.debug(f"[{handler_name}] {handler_name} thread started.")
                else:
                    logger.debug(
                        f"[{handler_name}] Waiting for {handler_name} thread to start."
                    )
                    sleep(1)
            # Notify the thread that it can start
            with getattr(shared_state, f"{handler_name.lower()}_condition"):
                sleep(0.2)
                getattr(shared_state, f"{handler_name.lower()}_condition").notify()
                logger.debug(f"[{handler_name}] {handler_name} notified.")
        else:
            # Stop the handler
            logger.debug(f"[{handler_name}] {handler_name} stopping...")
            setattr(shared_state, is_running_key, False)
            thread = getattr(self, thread_key, None)
            if thread and thread.is_alive():
                thread.join()
                logger.debug(
                    f"[{handler_name}] {handler_name} thread stopped successfully."
                )
            else:
                logger.debug(
                    f"[{handler_name}] Unable to stop {handler_name}. Is it running?"
                )

    def toggle_bank_heist_handler(self):
        self._toggle_handler(
            "bank_heist",
            "bank_heist_handler_running",
            "bank_heist_handler_thread",
            bank_heist_handler.BankHeistHandler().run,
        )

    def toggle_shut_down_handler(self):
        self._toggle_handler(
            "shut_down",
            "shut_down_handler_running",
            "shut_down_handler_thread",
            shut_down_handler.ShutDownHandler().run,
        )

    def toggle_ui_handler(self):
        self._toggle_handler(
            "ui",
            "ui_handler_running",
            "ui_handler_thread",
            ui_handler.UIHandler().run,
        )

    def toggle_idle_handler(self):
        self._toggle_handler(
            "idle",
            "idle_handler_running",
            "idle_handler_thread",
            idle_handler.IdleHandler().run,
        )

    def toggle_multiplier_monitor(self):
        self._toggle_handler(
            "multiplier_monitor",
            "multiplier_monitor_running",
            "multiplier_monitor_thread",
            self.start_multiplier_monitor,
        )

    def toggle_building_monitor(self):
        self._toggle_handler(
            "building_monitor",
            "building_monitor_running",
            "building_monitor_thread",
            self.start_building_monitor,
        )

    def toggle_autoroll_handler(self):
        self._toggle_handler(
            "autoroll_handler",
            "autoroll_handler_running",
            "autoroll_handler_thread",
            self.start_autoroll_handler,
        )

    def toggle_autoroll_monitor(self):
        self._toggle_handler(
            "autoroll_monitor",
            "autoroll_monitor_running",
            "autoroll_monitor_thread",
            self.start_autoroll_monitor,
        )
