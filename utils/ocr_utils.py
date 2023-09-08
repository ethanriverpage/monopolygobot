from PIL import Image
import pyscreeze
from pyautogui import locateOnScreen, center
from cv2 import resize, cvtColor, INTER_LINEAR, COLOR_BGR2GRAY, threshold, THRESH_BINARY
import numpy as np


class OCRUtils:
    def find(self, image: Image.Image) -> pyscreeze.Point | None:
        try:
            result = locateOnScreen(image, grayscale=True, confidence=0.80)
            if result is None:
                return None
            return center(result)
        except OSError:
            print("[OCR] Screen grab failed")

    def preprocess_image(
        self,
        image,
        contrast_reduction_percentage,
        target_size=None,
        threshold_value=None,
    ):
        # Resize the image to the target size (if specified)
        if target_size:
            image = resize(image, target_size, interpolation=INTER_LINEAR)
        # Convert the image to grayscale
        gray_image = cvtColor(image, COLOR_BGR2GRAY)
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
            _, thresholded_image = threshold(
                reduced_contrast_image, threshold_value, 255, THRESH_BINARY
            )
            return thresholded_image
        else:
            return reduced_contrast_image
