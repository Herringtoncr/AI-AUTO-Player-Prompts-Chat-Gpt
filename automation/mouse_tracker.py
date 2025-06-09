import pyautogui

while True:
    x, y = pyautogui.position()  # Get exact coordinates
    print(f"X={x}, Y={y}", end="\r")  # Show only two numbers