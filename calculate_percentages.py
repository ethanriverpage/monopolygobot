import pygetwindow as gw

b1l = 407
b1u = 1850
b1r = 663
b1b = 1901

b2l = 289
b2u = 1752
b2r = 422
b2b = 1806

left_diff = b2l - b1l
right_diff = b2r - b1r

b3l = b2l + left_diff
b3u = 1752
b3r = b2r + right_diff
b3b = 1806


windows = gw.getWindowsWithTitle("BOT TESTING")

if windows:
    window = windows[0]
    window_x = 0
    window_y = 0
    window_width = 1082
    window_height = 2016
    print(f"BOT TESTING: {window_x}, {window_y}, {window_width}, {window_height}")

    b1left_percent = b1l / window_width * 100
    b1right_percent = b1r / window_width * 100
    b1upper_percent = b1u / window_height * 100
    b1bottom_percent = b1b / window_height * 100

    b2left_percent = b2l / window_width * 100
    b2right_percent = b2r / window_width * 100
    b2upper_percent = b2u / window_height * 100
    b2bottom_percent = b2b / window_height * 100

    building1region = (
        b1left_percent,
        b1upper_percent,
        b1right_percent,
        b1bottom_percent,
    )
    building2region = (
        b2left_percent,
        b2upper_percent,
        b2right_percent,
        b2bottom_percent,
    )
    building3region = (
        b3l / window_width * 100,
        b3u / window_height * 100,
        b3r / window_width * 100,
        b3b / window_height * 100,
    )

    print(f"B1: {building1region}")
    print(f"B2: {building2region}")
    print(f"B3: {building3region}")
