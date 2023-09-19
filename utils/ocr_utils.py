from PIL import ImageGrab
import pyscreeze
import cv2
import numpy as np
from pytesseract import pytesseract
from shared_state import shared_state

pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"


class OCRUtils:
    def __init__(self):
        """
        Initialize the OCRUtils class.

        This class provides utility functions for performing optical character recognition (OCR) on screen captures.
        It uses various libraries such as PIL, OpenCV, NumPy, and pytesseract.

        Attributes:
            window: A tuple representing the window coordinates (x, y, width, height).
            window_x: The x-coordinate of the window's top-left corner.
            window_y: The y-coordinate of the window's top-left corner.
            window_width: The width of the window.
            window_height: The height of the window.
            window_coords: A tuple representing the window coordinates (left, top, right, bottom).
            window_size: The size of the window.
        """
        self.window = shared_state.window
        (
            self.window_x,
            self.window_y,
            self.window_width,
            self.window_height,
        ) = self.window
        self.window_coords = shared_state.window_coords
        self.window_size = self.window

    def find(self, template: np.ndarray, bbox=None) -> pyscreeze.Point | None:
        """
        Find a template image within the specified region of the screen.

        Args:
            template (np.ndarray): The template image to search for.
            bbox (tuple, optional): The region of the screen to search within (left, top, right, bottom).

        Returns:
            pyscreeze.Point | None: The coordinates of the found match center, or None if not found.
        """
        try:
            if bbox is None:
                bbox = self.window_size
            screenshot = ImageGrab.grab(
                bbox=bbox
            )  # Capture a screenshot of the specified region
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

            res = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
            threshold = 0.75  # Adjust the threshold as needed
            loc = np.where(res >= threshold)

            if loc[0].size == 0:
                return None

            # Get the coordinates of the match
            y, x = loc[0][0], loc[1][0]
            match_center = (x + template.shape[1] // 2, y + template.shape[0] // 2)

            return match_center
        except OSError:
            print("[OCR] Screen grab failed")
            return None

    def preprocess_image(
        self,
        image,
        target_size=None,
        threshold_value=None,
        invert=None,
    ):
        """
        Preprocess an image for OCR by resizing, converting to grayscale, and thresholding.

        Args:
            image: The input image to preprocess.
            target_size (tuple, optional): The target size for resizing (width, height).
            threshold_value (int, optional): The threshold value for binarization.
            invert (bool, optional): Whether to invert the colors (black background).

        Returns:
            np.ndarray: The preprocessed image.
        """
        # Resize the image to the target size (if specified)
        if target_size:
            image = cv2.resize(image, target_size, interpolation=cv2.INTER_LANCZOS4)
        # Convert the image to grayscale
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Apply thresholding if threshold_value is provided\
        if invert:
            if threshold_value is not None:
                _, thresholded_image = cv2.threshold(
                    gray_image,
                    threshold_value,
                    255,
                    cv2.THRESH_BINARY_INV,
                )
                return thresholded_image
            if threshold_value is None:
                gray_image_inv = 255 - gray_image
                return gray_image_inv
        else:
            if threshold_value is not None:
                _, thresholded_image = cv2.threshold(
                    gray_image,
                    threshold_value,
                    255,
                    cv2.THRESH_BINARY,
                )
                return thresholded_image
            if threshold_value is None:
                return gray_image

    def ocr_to_str(
        self,
        region_x_percent,
        region_y_percent,
        region_right_percent,
        region_bottom_percent,
        output_image_path=None,
        ocr_settings=None,
        process_settings=None,
    ):
        """
        Perform OCR on a specified region of the screen and return the recognized text.

        Args:
            region_x_percent (float): The X-coordinate percentage of the left edge of the region.
            region_y_percent (float): The Y-coordinate percentage of the top edge of the region.
            region_right_percent (float): The X-coordinate percentage of the right edge of the region.
            region_bottom_percent (float): The Y-coordinate percentage of the bottom edge of the region.
            output_image_path (str, optional): The path to save the preprocessed image.
            ocr_settings (str, optional): Additional OCR configuration settings.
            process_settings (dict, optional): Image preprocessing settings.

        Returns:
            str: The recognized text within the specified region.
        """
        left = int(
            self.window_coords[0] + (self.window_coords[2] * (region_x_percent / 100))
        )
        upper = int(
            self.window_coords[1] + (self.window_coords[3] * (region_y_percent / 100))
        )
        right = int(
            self.window_coords[0]
            + (self.window_coords[2] * (region_right_percent / 100))
        )
        bottom = int(
            self.window_coords[1]
            + (self.window_coords[3] * (region_bottom_percent / 100))
        )

        screenshot = ImageGrab.grab(bbox=(left, upper, right, bottom))
        screenshot_np = np.array(screenshot)
        # screenshot_cropped = screenshot_np[upper:bottom, left:right]
        if process_settings:
            screenshot_size = (
                screenshot_np.shape[1] * process_settings["scale_factor"],
                screenshot_np.shape[0] * process_settings["scale_factor"],
            )
            screenshot_proc = self.preprocess_image(
                image=screenshot_np,
                target_size=screenshot_size,
                threshold_value=process_settings["threshold_value"],
                invert=process_settings["invert"],
            )
        else:
            screenshot_proc = screenshot_np
        if output_image_path:
            cv2.imwrite(output_image_path, screenshot_proc)
        if ocr_settings:
            text = pytesseract.image_to_string(screenshot_proc, config=ocr_settings)
        else:
            text = pytesseract.image_to_string(screenshot_proc)

        return text

    def screenshot(self, name):
        """
        Capture a screenshot of the entire window and save it to a file.

        Args:
            name (str): The name and path of the output screenshot file.
        """
        screenshot = ImageGrab.grab(bbox=self.window_coords)
        screenshot.save(name)
