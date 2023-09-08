from handlers import (
    autoroller,
    bank_heist_handler,
    shut_down_handler,
    ui_handler,
    building_handler,
)
from threading import Thread
from shared_state import shared_state
from utils.player_info import PlayerInfo

player_info = PlayerInfo()


class StateHandler:
    def __init__(self):
        pass

    def start_player_info(self):
        threads = [
            Thread(target=player_info.run_money, daemon=True),
            Thread(target=player_info.run_rolls, daemon=True),
        ]

        for thread in threads:
            thread.start()

    def toggle_autoroller(self):
        if (
            not shared_state.autoroller_running
            and shared_state.rolls >= shared_state.AR_MINIMUM_ROLLS
        ):
            # Stop disable_autoroll
            if shared_state.disable_autoroller_running:
                shared_state.disable_autoroller_running = False
                self.disable_autoroller_thread.join()
                if not self.disable_autoroller_thread.is_alive():
                    print("[AUTOROLL] Disable_autoroll stopped successfully.")
                    shared_state.disable_autoroller_thread_is_alive = False
            # Start autoroll
            shared_state.autoroller_running = True
            self.autoroller_thread = Thread(
                target=autoroller.AutoRoller.run, daemon=True
            )
            self.autoroller_thread.start()
            print("[AUTOROLL] Autoroll started.")
            shared_state.autoroller_running = True
            shared_state.autoroller_thread_is_alive = True
            """lif shared_state.rolls < shared_state.AR_MINIMUM_ROLLS:
            print(
                f"[AUTOROLL] Cannot start autoroll. {shared_state.rolls} is < minimum {shared_state.AR_MINIMUM_ROLLS} to start rolling."
            )"""
        elif (
            shared_state.autoroller_running
            and not shared_state.disable_autoroller_running
        ):
            # Stop autoroll
            print("[AUTOROLL] Autoroll stopping...")
            shared_state.autoroller_running = False
            try:
                self.autoroller_thread.join()
                if not self.autoroller_thread.is_alive():
                    print("[AUTOROLL] Autoroll thread stopped successfully.")
                    shared_state.autoroller_thread_is_alive = False
            except Exception:
                print("[STATE] Unable to stop autoroll. Is it running?")
                pass

            # Start disable_autoroll
            shared_state.disable_autoroller_running = True
            self.disable_autoroller_thread = Thread(
                target=autoroller.DisableAutoRoller.run, daemon=True
            )
            self.disable_autoroller_thread.start()
            print("[AUTOROLL] Disable_autoroll started.")
            shared_state.disable_autoroller_running = True
            shared_state.disable_autoroller_thread_is_alive = True

    def start_bank_heist_handler(self):
        bank_heist_handler_thread = Thread(
            target=bank_heist_handler.BankHeistHandler().run, daemon=True
        )
        print("[HEIST] Starting thread...")
        shared_state.bank_heist_handler_running = True
        bank_heist_handler_thread.start()
        print("[HEIST] Notifying thread...")
        with bank_heist_handler.bank_heist_handler_condition:
            bank_heist_handler.bank_heist_handler_condition.notify()
            shared_state.bank_heist_handler_running = True

    def stop_bank_heist_handler(self):
        shared_state.bank_heist_handler_running = False
        print("[HEIST] Telling thread to wait...")

    def start_shut_down_handler(self):
        shut_down_handler_thread = Thread(
            target=shut_down_handler.ShutDownHandler().run, daemon=True
        )
        print("[SD] Starting thread...")
        shared_state.shut_down_handler_running = True
        shut_down_handler_thread.start()
        print("[SD] Notifying thread...")
        with shut_down_handler.shut_down_handler_condition:
            shut_down_handler.shut_down_handler_condition.notify()
            shared_state.shut_down_handler_running = True

    def stop_shut_down_handler(self):
        shared_state.shut_down_handler_running = False
        print("[SD] Telling thread to wait...")

    def start_ui_handler(self):
        ui_handler_thread = Thread(target=ui_handler.UIHandler().run, daemon=True)
        print("[UI] Starting thread...")
        shared_state.ui_handler_running = True
        ui_handler_thread.start()
        print("[UI] Notifying thread...")
        with ui_handler.ui_handler_condition:
            ui_handler.ui_handler_condition.notify()
            shared_state.ui_handler_running = True

    def stop_ui_handler(self):
        shared_state.ui_handler_running = False
        print("[UI] Telling thread to wait...")

    def start_building_handler(self):
        building_handler_instance = building_handler.BuildingHandler(self)
        building_handler_thread = Thread(
            target=building_handler_instance.run, daemon=True
        )
        print("[BUILDER] Starting thread...")
        shared_state.builder_running = True
        building_handler_thread.start()
