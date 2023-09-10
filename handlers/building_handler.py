from shared_state import shared_state
from utils.image_cache import ImageCache
from pyautogui import locateOnScreen, center, screenshot, moveTo
from pydirectinput import click
from time import sleep
import re
from utils.ocr_utils import OCRUtils
from pytesseract import image_to_string
import numpy as np
import pygetwindow as gw

image_cache = ImageCache()
ocr_utils = OCRUtils()


class BuildingHandler:
    def __init__(self, state_handler):
        self.state_handler = state_handler
        shared_state.builder_running = True
        # Disable autoroller
        self.stop_autoroller()
        # Initialize variables
        self.current_money = shared_state.money
        self.image_cache = image_cache
        self.start_building = False
        self.unsuccessful_purchases = 0
        self.finished = False
        self.in_menu = False
        self.building_costs_gathered = False
        window_title = shared_state.WINDOW_TITLE
        windows = gw.getWindowsWithTitle(window_title)
        if windows:
            window = windows[0]
            self.window_x, self.window_y, self.window_width, self.window_height = (
                window.left,
                window.top,
                window.width,
                window.height,
            )
        print("[BUILDER] Initialized successfully.")

    def stop_autoroller(self):
        if shared_state.autoroller_running:
            print("[BUILDER] Toggling autoroll...")
            self.state_handler.toggle_autoroller()
            while shared_state.autoroller_thread_is_alive:
                sleep(1)
            sleep(5)
        else:
            print("[BUILDER] Toggling autoroll...")
            self.state_handler.toggle_autoroller()

    # Enter the build menu (menu state 1)
    def check_menu_status(self):
        build_exit = image_cache.load_image("build-exit.png")
        location = locateOnScreen(build_exit)
        if location:
            self.in_menu = True
        else:
            self.in_menu = False

    def enter_build_menu(self):
        self.check_menu_status()
        if not self.in_menu:
            build_icon = image_cache.load_image("build.png")
            while True:
                location = locateOnScreen(build_icon)
                if location:
                    center_x, center_y = center(location)
                    click(center_x, center_y)
                    sleep(2)
                self.check_menu_status()
                if self.in_menu:
                    print("[BUILDER] Menu entered successfully.")
                    self.in_menu = True
                    break
                break

    # Gather the costs of each building, loop until all 5 costs are acquired

    def extract_and_convert_cost(self, cost_text):
        # Define a regular expression pattern to match numbers with optional decimal points and 'M' or 'K' indicators
        pattern = r"(\d+(\.\d+)?)([MK]?)"

        # Search for matches in the cost_text
        match = re.search(pattern, cost_text)
        if match:
            # Extract the numeric part and unit part
            numeric_part, _, unit_part = match.groups()

            # Convert the numeric part to a float (to handle decimal points) and multiply by 1 million or 1 thousand based on the unit
            if unit_part == "M":
                self.cost_value = int(float(numeric_part) * 1_000_000)
            elif unit_part == "K":
                self.cost_value = int(float(numeric_part) * 1_000)
            else:
                self.cost_value = int(float(numeric_part))

            return self.cost_value
        else:
            # If no match found, return 0 or raise an exception based on your requirements
            return 0  # You can modify this to handle errors differently if needed

    def gather_building_costs(self):
        self.y = 1202
        width = 91
        height = 42
        buildings = [
            {
                "name": "building1",
                "x_percent": 7.024,
                "y_percent": 86.905,
                "right_percent": 19.316,
                "bottom_percent": 89.583,
                "cost": "",
            },
            {
                "name": "building2",
                "x_percent": 26.710,
                "y_percent": 86.905,
                "right_percent": 39.002,
                "bottom_percent": 89.583,
                "cost": "",
            },
            {
                "name": "building3",
                "x_percent": 47,
                "y_percent": 86.905,
                "right_percent": 58.3,
                "bottom_percent": 89.583,
                "cost": "",
            },
            {
                "name": "building4",
                "x_percent": 67,
                "y_percent": 86.905,
                "right_percent": 77.6,
                "bottom_percent": 89.583,
                "cost": "",
            },
            {
                "name": "building5",
                "x_percent": 86.75,
                "y_percent": 86.905,
                "right_percent": 97,
                "bottom_percent": 89.583,
                "cost": "",
            },
        ]
        cost_text = None
        building_finished = self.image_cache.load_image("building-complete.png")
        self.check_menu_status()
        if not self.in_menu:
            self.enter_build_menu()
        else:
            if self.in_menu:
                for building_info in buildings:
                    building_name = building_info["name"]
                    x_percent = building_info["x_percent"]
                    y_percent = building_info["y_percent"]
                    right_percent = building_info["right_percent"]
                    bottom_percent = building_info["bottom_percent"]
                    x = int(self.window_x + (self.window_width * (x_percent / 100)))
                    y = int(self.window_y + (self.window_height * (y_percent / 100)))
                    width = int(self.window_width * (right_percent - x_percent) / 100)
                    height = int(
                        self.window_height * (bottom_percent - y_percent) / 100
                    )

                    print(f"[BUILDER] Getting cost of {building_name}...")
                    finished = locateOnScreen(
                        building_finished, region=(x, y, width, height)
                    )
                    if not finished:
                        cost_text = ocr_utils.ocr_to_str(
                            x_percent,
                            y_percent,
                            right_percent,
                            bottom_percent,
                        )

                        sleep(0.1)

                        cost = self.extract_and_convert_cost(cost_text)
                        buildings[cost] = cost
                        print(f"[BUILDER] {building_name} costs {cost}")
                    else:
                        print("[BUILDER] Building finished. Moving on...")
                        cost = -1
                        buildings[cost] = cost
                sleep(1)
                self.purchase_buildings()

    def purchase_buildings(self):
        """
        Purchase buildings based on gathered costs.
        """
        self.check_menu_status()
        current_money = shared_state.money
        if not self.in_menu:
            self.enter_build_menu()
        for building, cost in self.building_costs.items():
            if cost == -1:
                print("[BUILDER] Not upgrading finished building...")
                continue
            elif self.unsuccessful_purchases == 5:
                print(
                    "[BUILDER] Unsuccessful purchase limit reached (max 6). Exiting..."
                )
                break
            elif current_money < shared_state.BUILD_FINISH_AMOUNT:
                print(
                    f"[BUILDER] Money is {current_money} which is < {shared_state.BUILD_FINISH_AMOUNT}. Stopping builder..."
                )
                break
            elif current_money < cost:
                print(
                    f"[BUILDER] Not enough money for purchase. Unsuccessful purchase # {self.unsuccessful_purchases}"
                )
                self.unsuccessful_purchases += 1
                continue
            elif current_money >= cost and cost > 0:
                # Move to the x, y coordinates of the building
                moveTo(x=self.building_x_coords[building], y=self.y - 50, duration=0.2)
                # Click to purchase the building
                click()
                print("[BUILDER] Building upgraded. Next...")
        else:
            self.gather_building_costs()
        self.exit_build_menu()

    def exit_build_menu(self):
        self.check_menu_status()
        if self.in_menu:
            build_exit = image_cache.load_image("build-exit.png")
            while True:
                location = locateOnScreen(build_exit)
                print("[BUILDER] Exiting build menu...")
                if location:
                    center_x, center_y = center(location)
                    click(center_x, center_y)
                    sleep(2)
                if not location:
                    print("[BUILDER] Exited build menu successfully...")
                    self.stop_autoroller()
                    shared_state.builder_running = False
                    break

    def run(self):
        self.check_menu_status()
        if not self.in_menu:
            self.enter_build_menu()
        self.gather_building_costs()
        shared_state.builder_running = False
