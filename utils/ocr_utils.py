from PIL import Image, ImageGrab
import pyscreeze
import pyautogui
import cv2
import numpy as np
from pytesseract import pytesseract
import pygetwindow as gw
from shared_state import shared_state

pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"


class OCRUtils:
    def __init__(self):
        self.window_size = None

    def find(self, template: np.ndarray) -> pyscreeze.Point | None:
        try:
            screenshot = ImageGrab.grab(
                bbox=(self.window_size)
            )  # Adjust the bbox as needed
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

            res = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
            threshold = 0.75  # Adjust the threshold as needed
            loc = np.where(res >= threshold)

            if loc[0].size == 0:
                # print("[OCR] Can't find the template...")
                return None

            # Get the coordinates of the match
            y, x = loc[0][0], loc[1][0]
            match_center = (x + template.shape[1] // 2, y + template.shape[0] // 2)

            return match_center
        except OSError:
            print("[OCR] Screen grab failed")
            return None

    """ def find(self, image: Image.Image) -> pyscreeze.Point | None:
        try:
            result = pyautogui.locateOnScreen(image, grayscale=True, confidence=0.75)
            if result is None:
                print("[OCR] Can't find go.png...")
                return None
            return pyautogui.center(result)
        except OSError:
            print("[OCR] Screen grab failed") """

    def preprocess_image(
        self,
        image,
        contrast_reduction_percentage,
        target_size=None,
        threshold_value=None,
    ):
        # Resize the image to the target size (if specified)
        if target_size:
            image = cv2.resize(image, target_size, interpolation=cv2.INTER_LINEAR)
        # Convert the image to grayscale
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        mean_intensity = np.mean(gray_image)
        contrast_reduction_factor = 1.0 - (contrast_reduction_percentage / 100.0)
        # Apply the contrast reduction to the image
        reduced_contrast_image = (
            gray_image * contrast_reduction_factor
            + mean_intensity * (1.0 - contrast_reduction_factor)
        )
        # Ensure the image mode is 'L' (grayscale)
        reduced_contrast_image = reduced_contrast_image.astype(np.uint8)
        # Apply thresholding if threshold_value is provided
        if threshold_value is not None:
            _, thresholded_image = cv2.threshold(
                reduced_contrast_image, threshold_value, 255, cv2.THRESH_BINARY
            )
            return thresholded_image
        else:
            return reduced_contrast_image

    def ocr_to_str(
        self,
        region_x_percent,
        region_y_percent,
        region_right_percent,
        region_bottom_percent,
        output_image_path=None,
    ):
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

            self.window_size = (
                self.window_x,
                self.window_y,
                self.window_width,
                self.window_height,
            )
            """ print(
                f"{window_title} = {self.window_x}, {self.window_y}, {self.window_width}, {self.window_height}"
            ) """

            left = int(self.window_x + (self.window_width * (region_x_percent / 100)))
            upper = int(self.window_y + (self.window_height * (region_y_percent / 100)))
            right = int(
                self.window_x + (self.window_width * (region_right_percent / 100))
            )
            bottom = int(
                self.window_y + (self.window_height * (region_bottom_percent / 100))
            )

            region = (left, upper, right, bottom)
            # print(region)

            screenshot = pyautogui.screenshot()
            screenshot_np = np.array(screenshot)
            screenshot_cropped = screenshot_np[upper:bottom, left:right]
            screenshot_size = (
                screenshot_cropped.shape[1] * 2,
                screenshot_cropped.shape[0] * 2,
            )
            screenshot_proc = self.preprocess_image(
                screenshot_cropped, -30, screenshot_size, 150
            )

            if output_image_path:
                cv2.imwrite(output_image_path, screenshot_proc)
            # Perform OCR on the cropped image
            text = pytesseract.image_to_string(screenshot_proc)

            return text
        else:
            print(f"No window with the title '{window_title}' found.")
            return ""
