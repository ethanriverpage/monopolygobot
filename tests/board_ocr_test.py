import re
from utils.ocr_utils import OCRUtils
from shared_state import shared_state

ocr_utils = OCRUtils()


class BoardOCRTest:
    def __init__(self):
        self.board_name = None

    def process_board_name(self, board_name):
        pattern = r"\d+/30"
        match = re.search(pattern, board_name)
        if match:
            start, _ = match.span()
            extracted_text = board_name[:start].strip()
            return extracted_text
        else:
            return board_name

    def gather_board_name(self):
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
            "board-name.png",
            True,
            "--psm 7 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789/ ",
            board_process_settings,
        )
        board_name = self.process_board_name(board_name)
        self.board_name = board_name
        print(self.board_name)


BoardOCRTest.gather_board_name(BoardOCRTest())
