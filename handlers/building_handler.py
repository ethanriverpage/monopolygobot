from shared_state import shared_state
from utils.image_cache import ImageCache
from pyautogui import locateOnScreen, center, screenshot, moveTo
from pydirectinput import click
from time import sleep
import re
from utils.ocr_utils import OCRUtils
from pytesseract import image_to_string
import numpy as np

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
        self.building_costs = {
            "building1": 0,
            "building2": 0,
            "building3": 0,
            "building4": 0,
            "building5": 0,
        }
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
                print("[BUILDER] Moving to gather_building_costs")
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
        self.check_menu_status()
        if not self.in_menu:
            self.enter_build_menu()
        self.building_costs = {}
        self.y = 1202
        width = 91
        height = 42
        self.building_x_coords = {
            "building1": 940,
            "building2": 1090,
            "building3": 1240,
            "building4": 1393,
            "building5": 1539,
        }
        self.cost_text = None
        building_finished = self.image_cache.load_image("building-complete.png")
        if self.in_menu:
            for building, x in self.building_x_coords.items():
                print(f"[BUILDER] Getting cost of {building}...")
                finished = locateOnScreen(
                    building_finished, region=(x, self.y, width, height)
                )
                if not finished:
                    target_size = (364, 168)
                    cost_region = (x, self.y, width, height)
                    cost_screenshot = screenshot(region=cost_region)
                    cost_screenshot_np = np.array(cost_screenshot)
                    thresholded_cost_image = ocr_utils.preprocess_image(
                        cost_screenshot_np,
                        contrast_reduction_percentage=0,
                        target_size=target_size,
                        threshold_value=150,
                    )
                    self.cost_text = image_to_string(thresholded_cost_image)
                    sleep(0.1)

                    cost = self.extract_and_convert_cost(self.cost_text)
                    self.building_costs[building] = cost
                    print(f"[BUILDER] {building} costs {cost}")
                else:
                    print("[BUILDER] Building finished. Moving on...")
                    cost = -1
                    self.building_costs[building] = cost
            sleep(1)
        else:
            self.enter_build_menu()
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

        self.check_menu_status()
        if self.in_menu:
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
