import pyautogui
import pytesseract
import pygetwindow as gw
from time import sleep

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
)

# Get the current screen resolution
screen_width, screen_height = pyautogui.size()

# Specify the title or a portion of the window title
window_title = "BOT TESTING"

# Get a list of windows with the specified title

windows = gw.getWindowsWithTitle(window_title)

if windows:
    # Get the first window in the list (you can adapt this logic if multiple windows match)
    window = windows[0]

    # Get the window's position and size
    window_x, window_y, window_width, window_height = (
        window.left,
        window.top,
        window.width,
        window.height,
    )

    region_x_percent = 47
    region_y_percent = 86.905
    region_right_percent = 58.3
    region_bottom_percent = 89.583
    print(f"{window_title} = {window_x}, {window_y}, {window_width}, {window_height}")

    # Define the region coordinates as percentages of both screen and window sizes
    # print(left_percent, upper_percent, right_percent, bottom_percent)
    # Calculate the region coordinates based on percentages
    left = int(window_x + (window_width * (region_x_percent / 100)))
    upper = int(window_y + (window_height * (region_y_percent / 100)))
    right = int(window_x + (window_width * (region_right_percent / 100)))
    bottom = int(window_y + (window_height * (region_bottom_percent / 100)))

    region = (left, upper, right, bottom)
    print(region)

    # Capture the screen
    screenshot = pyautogui.screenshot()

    # Crop the screenshot to the specified region
    cropped_image = screenshot.crop(region)
    cropped_image.save("cropped_image.png")

    # Perform OCR on the cropped image
    text = pytesseract.image_to_string(cropped_image)

    # Print or process the extracted text
    print(text)
