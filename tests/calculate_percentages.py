import pygetwindow as gw

b1l = 378
b1u = 1348
b1r = 386
b1b = 1355

b2l = 215
b2u = 1202
b2r = 303
b2b = 1237

b3l = 358
b3u = 1202
b3r = 446
b3b = 1237

b4l = 514
b4u = 1202
b4r = 602
b4b = 1237

b5l = 658
b5u = 1202
b5r = 746
b5b = 1237


windows = gw.getWindowsWithTitle("mgb_bot1")

if windows:
    window = windows[0]
    window_x, window_y, window_width, window_height = (
        window.left,
        window.top,
        window.width,
        window.height,
    )
    print(f"BOT TESTING: {window_x}, {window_y}, {window_width}, {window_height}")

    b1left_percent = b1l / window_width * 100
    b1right_percent = b1r / window_width * 100
    b1upper_percent = b1u / window_height * 100
    b1bottom_percent = b1b / window_height * 100

    b2left_percent = b2l / window_width * 100
    b2right_percent = b2r / window_width * 100
    b2upper_percent = b2u / window_height * 100
    b2bottom_percent = b2b / window_height * 100

    b3left_percent = b3l / window_width * 100
    b3right_percent = b3r / window_width * 100
    b3upper_percent = b3u / window_height * 100
    b3bottom_percent = b3b / window_height * 100

    b4left_percent = b4l / window_width * 100
    b4right_percent = b4r / window_width * 100
    b4upper_percent = b4u / window_height * 100
    b4bottom_percent = b4b / window_height * 100

    b5left_percent = b5l / window_width * 100
    b5right_percent = b5r / window_width * 100
    b5upper_percent = b5u / window_height * 100
    b5bottom_percent = b5b / window_height * 100

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
        b3left_percent,
        b3upper_percent,
        b3right_percent,
        b3bottom_percent,
    )
    building4region = (
        b4left_percent,
        b4upper_percent,
        b4right_percent,
        b4bottom_percent,
    )
    building5region = (
        b5left_percent,
        b5upper_percent,
        b5right_percent,
        b5bottom_percent,
    )

    print(f"B1: {building1region}")
    print(f"B2: {building2region}")
    print(f"B3: {building3region}")
    print(f"B4: {building4region}")
    print(f"B5: {building5region}")
