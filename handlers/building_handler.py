"""
building_handler.py

This module contains the BuildingHandler class, which is responsible for handling building upgrades. It is called by the building_monitor.py and runs in a separate thread.
It is responsible for:
    - Entering the build menu
    - OCR to get the cost of each building upgrade
    - Upgrading buildings
    - Gathering data about each board
"""

from shared_state import shared_state
from pyautogui import moveTo
from pydirectinput import click
from time import sleep
import re
from utils.ocr_utils import OCRUtils
import os
import json
from utils.logger import logger

ocr_utils = OCRUtils()


class BuildingHandler:
    """
    The BuildingHandler class manages building-related operations in the game.

    Attributes:
        current_path (str): The current working directory.
        game_data_file (str): The name of the game data file (JSON format).
        current_money (int): The current amount of in-game currency.
        window_x (int): The x-coordinate of the game window.
        window_y (int): The y-coordinate of the game window.
        window_width (int): The width of the game window.
        window_height (int): The height of the game window.
        current_board_data (dict): Data for the current game board.
        buildings (list): A list of dictionaries containing building information.
        data (list): A list containing game data.

    Methods:
        __init__(self):
            Initializes a BuildingHandler object.

        load_data(self):
            Loads game data from the game_data_file.

        save_data(self):
            Batch saves game data to the game_data_file.

        process_board_name(self, board_name):
            Processes board name from OCR results.

        gather_board_name(self):
            Retrieves the game board name using OCR.

        enter_build_menu(self):
            Navigates to the game's build menu.

        check_menu_status(self):
            Checks if the game is in the build menu.

        extract_and_convert_cost(self, cost_text):
            Extracts and converts building costs from OCR results.

        gather_board_number(self):
            Retrieves the board number for the current game board.

        find_max_board_number(self):
            Finds the maximum board number in the game data.

        create_new_board(self):
            Creates a new game board entry.

        update_and_append_board_data(self):
            Updates and appends board data to the game data.

        exit_build_menu(self):
            Exits the game's build menu.

        run(self):
            Main method that manages the building process in the game.
    """

    def __init__(self):
        # Establish current path and game data file
        self.current_path = shared_state.current_path
        self.game_data_file = str(shared_state.WINDOW_TITLE.strip()) + "_game_data.json"
        # Wait for money to update
        with shared_state.money_condition:
            shared_state.money_condition.wait()
        self.all_buildings_upgraded = False
        shared_state.builder_finished = False
        self.current_money = shared_state.money
        # Initialize window coordinates
        (
            self.window_x,
            self.window_y,
            self.window_width,
            self.window_height,
        ) = shared_state.window
        # Initialize current_board_data
        self.current_board_data = {}
        self.buildings = [
            {
                "name": "building1",
                "x_percent": 6.3,
                "y_percent": 86.4,
                "right_percent": 19,
                "bottom_percent": 88.9,
                "upgrade_level": 0,
                "upgrade0": 0,
                "upgrade1": 0,
                "upgrade2": 0,
                "upgrade3": 0,
                "upgrade4": 0,
                "upgrade5": 0,
                "upgrade6": 0,
            },
            {
                "name": "building2",
                "x_percent": 25,
                "y_percent": 86.4,
                "right_percent": 38,
                "bottom_percent": 88.9,
                "upgrade_level": 0,
                "upgrade0": 0,
                "upgrade1": 0,
                "upgrade2": 0,
                "upgrade3": 0,
                "upgrade4": 0,
                "upgrade5": 0,
                "upgrade6": 0,
            },
            {
                "name": "building3",
                "x_percent": 43.9,
                "y_percent": 86.4,
                "right_percent": 56.9,
                "bottom_percent": 88.9,
                "upgrade_level": 0,
                "upgrade0": 0,
                "upgrade1": 0,
                "upgrade2": 0,
                "upgrade3": 0,
                "upgrade4": 0,
                "upgrade5": 0,
                "upgrade6": 0,
            },
            {
                "name": "building4",
                "x_percent": 63.4,
                "y_percent": 86.4,
                "right_percent": 76.4,
                "bottom_percent": 88.9,
                "upgrade_level": 0,
                "upgrade0": 0,
                "upgrade1": 0,
                "upgrade2": 0,
                "upgrade3": 0,
                "upgrade4": 0,
                "upgrade5": 0,
                "upgrade6": 0,
            },
            {
                "name": "building5",
                "x_percent": 81.9,
                "y_percent": 86.4,
                "right_percent": 94.3,
                "bottom_percent": 88.9,
                "upgrade_level": 0,
                "upgrade0": 0,
                "upgrade1": 0,
                "upgrade2": 0,
                "upgrade3": 0,
                "upgrade4": 0,
                "upgrade5": 0,
                "upgrade6": 0,
            },
        ]
        self.data = self.load_data()

        logger.debug("[BUILDER] Initialized successfully.")

    def load_data(self):
        """
        Loads game data from the game_data_file.

        Returns:
            list: A list containing game data.
        """
        try:
            with open(self.game_data_file, "r") as f:
                logger.debug(f"[BUILDER] Loaded data from {self.game_data_file}.")
                return json.load(f)

        except FileNotFoundError:
            logger.error("[BUILDER] game_data.json not found.")
            return []

    def save_data(self):
        """
        Batch saves game data to the game_data_file.
        """
        logger.debug(f"[BUILDER] Saving data to {self.game_data_file}...")
        with open(self.game_data_file, "w") as f:
            json.dump(self.data, f, indent=4)
        # logger.debug(f"[BUILDER] Saved data: {self.data}.")

    def process_board_name(self, board_name):
        """
        Processes board name from OCR results.
        """
        pattern = r"\d+/30"  # Matches the progress of building upgrades
        cleaned_name = re.sub(
            r"[^a-zA-Z0-9/ ]", "", board_name
        )  # Remove all non-alphanumeric characters except for "/" and " "
        match = re.search(pattern, cleaned_name)
        if match:
            start, _ = match.span()
            extracted_text = board_name[
                :start
            ].strip()  # Remove the progress of building upgrades
            return extracted_text
        else:
            return board_name

    def gather_board_name(self):
        """
        Retrieves the game board name using OCR.
        """
        board_name_region = (1, 91.7, 94.9, 95)
        board_x_percent = board_name_region[0]
        board_y_percent = board_name_region[1]
        board_right_percent = board_name_region[2]
        board_bottom_percent = board_name_region[3]
        board_process_settings = {
            "contrast_reduction_percentage": 0,
            "threshold_value": 75,
            "invert": False,
            "scale_factor": 4,
        }
        board_name = None
        board_name = ocr_utils.ocr_to_str(
            board_x_percent,
            board_y_percent,
            board_right_percent,
            board_bottom_percent,
            ocr_settings="--psm 7 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789/ ",
            process_settings=board_process_settings,
        )
        board_name_proc = self.process_board_name(board_name)
        logger.debug(f"[BUILDER] Board name is {board_name_proc}.")
        return board_name_proc

    def enter_build_menu(self):
        """
        Navigates to the game's build menu.
        When called, will loop until the game is in the build menu.
        """
        in_menu = self.check_menu_status()
        print(in_menu)
        while not in_menu:
            in_menu = self.check_menu_status()
            print(in_menu)
            if not in_menu:
                logger.debug("[BUILDER] Not in menu, looking for build icon")
                build_path = os.path.join(self.current_path, "images", "build.png")
                build_image = shared_state.load_image(build_path)
                location = ocr_utils.find(build_image)
                if location:
                    logger.debug("[BUILDER] Found build menu icon. Clicking...")
                    x, y = location
                    click(x, y)
                    sleep(2)
                    in_menu = self.check_menu_status()
                    print(in_menu)

    def check_menu_status(self):
        """
        When called, will check if the game is in the build menu.
        Returns:
            bool: True if the game is in the build menu, False otherwise.
        """
        exit_path = os.path.join(self.current_path, "images", "build-exit.png")
        exit_image = shared_state.load_image(exit_path)
        location = ocr_utils.find(exit_image)
        if not location:
            # logger.debug("[BUILDER] Not in build menu.")
            return False
        if location:
            # logger.debug("[BUILDER] In build menu.")
            return True

    def extract_and_convert_cost(self, cost_text):
        """
        Extracts and converts building costs from OCR results.
        Returns:
            int: The cost of the building upgrade.
        """
        pattern = r"(\d+(\.\d+)?)([MK]?)"  # Matches numbers with optional decimal point and optional "M" or "K" at the end
        match = re.search(pattern, cost_text)
        if match:
            numeric_part, decimal_part, unit_part = match.groups()
            if not unit_part and decimal_part:
                # Numeric part has a decimal point but no "M" or "K"
                conversion_factor = 1000
            else:
                conversion_factor = (
                    1_000_000
                    if unit_part == "M"
                    else (1_000 if unit_part == "K" else 1)
                )
            numeric_part = numeric_part.replace(
                ",", ""
            )  # Remove commas as digit separators
            self.cost_value = int(float(numeric_part) * conversion_factor)
            return self.cost_value
        else:
            return 0

    def gather_board_number(self):
        """
        Retrieves the board number for the current game board if the board number exists in the current game data.
        Returns:
            int: The board number for the current game board.
        """
        active_board_name = self.gather_board_name()
        for board_data in self.data:
            if board_data["board_name"] == active_board_name:
                return board_data["board_number"]
        return None

    def find_max_board_number(self):
        """
        Finds the maximum board number in the game data.
        Returns:
            int: The maximum board number in the game data.
        """
        max_board_number = 0
        for board_data in self.data:
            board_number = board_data.get("board_number", 0)
            max_board_number = max(max_board_number, board_number)
        return max_board_number

    def create_new_board(self):
        """
        Creates a new game board entry.
        Returns:
            dict: A dictionary containing the new game board data.
        """
        if self.board_number is not None:
            new_board_number = self.board_number + 1
        else:
            # Get the maximum board number from existing data and increment it by 1
            new_board_number = self.find_max_board_number() + 1

        new_board_name = self.board_name
        new_board_data = {
            "board_number": new_board_number,
            "board_name": new_board_name,
            "building1": [0, 0, 0, 0, 0, 0],
            "building2": [0, 0, 0, 0, 0, 0],
            "building3": [0, 0, 0, 0, 0, 0],
            "building4": [0, 0, 0, 0, 0, 0],
            "building5": [0, 0, 0, 0, 0, 0],
        }
        # logger.debug(f"[BUILDER] Created a new board: {new_board_data}")
        return new_board_data

    def update_and_append_board_data(self):
        """
        Updates and appends board data to the game data.
        If board name exists in game data, update the existing entry.
        If board name does not exist in game data, append a new entry.
        """
        found_board = False
        for board_data in self.data:
            if board_data["board_name"] == self.board_name:
                # Merge the building data into the existing board_data
                for building_info in self.buildings:
                    building_name = building_info["name"]
                    upgrades = [building_info[f"upgrade{i}"] for i in range(6)]
                    board_data[building_name] = upgrades
                found_board = True
                # logger.debug(f"[BUILDER] Updated board_data: {board_data}")
                break

        if not found_board:
            # If the board name doesn't exist in self.data, add a new entry
            new_board_data = self.create_new_board()
            for building_info in self.buildings:
                building_name = building_info["name"]
                upgrades = [building_info[f"upgrade{i}"] for i in range(6)]
                new_board_data[building_name] = upgrades
            self.data.append(new_board_data)
            # logger.debug(f"[BUILDER] Appended new board_data: {new_board_data}")

    def calculate_total_cost(self):
        """
        Calculate the total cost of all building upgrades on the current board.
        """
        total_cost = 0
        for building_info in self.buildings:
            building_name = building_info["name"]
            upgrades = [
                building_info[f"upgrade{i}"] for i in range(6)
            ]  # Get upgrade costs
            total_cost += sum(upgrades)  # Sum the upgrade costs for this building
        return total_cost

    def update_total_cost_in_json(self):
        """
        Update the JSON data with the total cost of the current board.
        """
        board_name = self.board_name
        total_cost = self.calculate_total_cost()

        # Iterate through the existing data to find the board by name
        for board_data in self.data:
            if board_data["board_name"] == board_name:
                board_data["total_cost"] = total_cost
                break  # Exit the loop after updating the data

        # Save the updated data to the JSON file
        self.save_data()

    def exit_build_menu(self):
        """
        Exits the game's build menu.
        Currently not used, as when a board is finished, the game automatically exits the build menu.
        """
        in_menu = self.check_menu_status()
        print(in_menu)
        if in_menu:
            build_exit_path = os.path.join(
                self.current_path, "images", "build-exit.png"
            )
            build_exit_image = shared_state.load_image(build_exit_path)
            in_menu = self.check_menu_status()
            print(in_menu)
            while in_menu:
                location = ocr_utils.find(build_exit_image)
                logger.debug("[BUILDER] Exiting build menu...")
                if location:
                    with shared_state.moveTo_lock:
                        moveTo(location)
                        sleep(0.5)
                        click()
                    sleep(2)
                if not location:
                    logger.debug("[BUILDER] Exited build menu successfully...")
                    break
                break
            with shared_state.builder_finished_condition:
                shared_state.builder_finished_condition.notify_all()
        else:
            with shared_state.builder_finished_condition:
                shared_state.builder_finished_condition.notify_all()

    def run(self):
        """
        Main method that manages the building process in the game.
        Exits upon completing all building upgrades.
        """
        building_finished_path = os.path.join(
            self.current_path, "images", "building-finished.png"
        )
        building_finished_image = shared_state.load_image(building_finished_path)
        in_menu = self.check_menu_status()
        if not in_menu:
            self.enter_build_menu()
        with shared_state.builder_running_condition:
            shared_state.builder_running_condition.wait_for(
                lambda: shared_state.builder_running
            )
        while True:  # Loop until builder_running is False
            self.board_name = self.gather_board_name()  # Get board name
            self.board_number = self.gather_board_number()  # Get board number
            while (
                self.board_name != "" or self.board_name is not None
            ):  # Loop until board name is empty or None
                in_menu = self.check_menu_status()
                if in_menu:
                    self.board_name = self.gather_board_name()
                    self.current_board_data["board_name"] = self.board_name
                    if self.board_name == "" or self.board_name is None:
                        break
                    # Screenshot the window for data verification
                    """ base_name = shared_state.current_path + self.board_name + ".png"
                    counter = 1
                    name = base_name
                    while os.path.exists(name):
                        name = (
                            shared_state.current_path
                            + f"{self.board_name}_{counter}.png"
                        )
                        counter += 1
                    try:
                        ocr_utils.screenshot(name)
                    except Exception as e:
                        print(e) """
                    # Gather building cost
                    for building_info in self.buildings:
                        in_menu = self.check_menu_status()
                        while not in_menu:
                            in_menu = self.check_menu_status()
                            sleep(1)
                        self.current_building_info = building_info
                        # Get building name and coordinates
                        building_name = building_info["name"]
                        x_percent = building_info["x_percent"]
                        y_percent = building_info["y_percent"]
                        right_percent = building_info["right_percent"]
                        bottom_percent = building_info["bottom_percent"]
                        self.x = int(
                            self.window_x + (self.window_width * (x_percent / 100))
                        )
                        self.y = int(
                            self.window_y + (self.window_height * (y_percent / 100))
                        )
                        self.right = int(
                            self.window_x + (self.window_width * (right_percent / 100))
                        )
                        self.bottom = int(
                            self.window_y
                            + (self.window_height * (bottom_percent / 100))
                        )
                        self.coords = (self.x, self.y, self.right, self.bottom)
                        logger.debug(f"[BUILDER] Getting cost of {building_name}...")
                        ocr_settings = (
                            r"--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789.MK"
                        )
                        process_settings = {
                            "threshold_value": 74,
                            "invert": False,
                            "scale_factor": 2,
                        }
                        # Check if building is finished
                        finished = ocr_utils.find(
                            building_finished_image, bbox=self.coords
                        )
                        if not finished:
                            cost_text = ocr_utils.ocr_to_str(
                                x_percent,
                                y_percent,
                                right_percent,
                                bottom_percent,
                                ocr_settings=ocr_settings,
                                process_settings=process_settings,
                            )
                            cost = self.extract_and_convert_cost(cost_text)
                            logger.debug(
                                f"[BUILDER] Cost of {building_name} at upgrade level {building_info['upgrade_level']} is {cost}."
                            )
                            if (
                                cost <= 1000 and cost > 0
                            ):  # If cost is too low, retry until cost is updated
                                logger.debug(
                                    f"[BUILDER] Cost of {building_name} is too low, waiting and retrying..."
                                )
                                sleep(1)
                                cost_text = ocr_utils.ocr_to_str(
                                    x_percent,
                                    y_percent,
                                    right_percent,
                                    bottom_percent,
                                    output_image_path=f"{building_name}.png",
                                    ocr_settings=ocr_settings,
                                    process_settings=process_settings,
                                )
                                cost = self.extract_and_convert_cost(cost_text)
                                with shared_state.money_condition:
                                    shared_state.money_condition.wait()
                                self.current_money = shared_state.money
                                logger.debug(
                                    f"[BUILDER] Current money is {self.current_money}."
                                )
                            building_info[  # Update building info with cost
                                f"upgrade{building_info['upgrade_level']}"
                            ] = cost
                            self.current_board_data[
                                building_name
                            ] = {  # Update current board data with building info, ignoring coordinates and upgrade level
                                key: value
                                for key, value in building_info.items()
                                if key
                                not in [
                                    "x_percent",
                                    "y_percent",
                                    "right_percent",
                                    "bottom_percent",
                                    "upgrade_level",
                                ]
                            }
                            """ logger.debug(
                                f"[BUILDER] Updated current board data: {self.current_board_data}"
                            ) """
                            self.update_and_append_board_data()
                            # Upgrade building
                            if (
                                cost > 0
                            ):  # If cost is 0, building is already at max level
                                with shared_state.moveTo_lock:
                                    moveTo(self.x, self.y)
                                    click()
                                building_info[
                                    "upgrade_level"
                                ] += 1  # Increment upgrade level
                                logger.debug(f"[BUILDER] Upgraded {building_name}.")

                                if any(
                                    building_info["upgrade_level"] <= 5
                                    for building_info in self.buildings
                                ):
                                    self.all_buildings_upgraded = False
                                else:
                                    self.all_buildings_upgraded = True
                                    self.update_total_cost_in_json()
                    # Screenshot the window
                    """ try:
                        name = (
                            self.board_name
                            + str(building_info["upgrade_level"])
                            + ".png"
                        )
                        ocr_utils.screenshot(name)
                    except Exception as e:
                        print(e) """

                    if (
                        self.all_buildings_upgraded
                    ):  # If all buildings are upgraded, exit build menu
                        logger.debug("[BUILDER] All buildings upgraded.")
                        break
                else:
                    self.board_name = None
                    self.enter_build_menu()
            logger.debug("[BUILDER] Exiting building handler...")
            logger.debug("[BUILDER] Saving data to JSON...")
            self.save_data()
            with shared_state.builder_finished_condition:
                shared_state.builder_finished = (
                    True  # Notify building_monitor that building is finished
                )
                shared_state.builder_finished_condition.notify_all()
            break
