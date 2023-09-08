import ctypes
from shared_state import shared_state


def set_console_title():
    ar_state = None
    if shared_state.autoroller_running:
        ar_state = "ON"
    else:
        ar_state = "OFF"

    status = f"[STATUS] AutoRoll: {ar_state} | Rolls: {shared_state.rolls} | Money: {shared_state.money}"
    ctypes.windll.kernel32.SetConsoleTitleW(status)
