import sys
from rpi_lcd import LCD
import threading
import time

# Set up LCD
lcd = LCD()

lcd_lock = threading.Lock()

def display_lcd(message1, message2):
    with lcd_lock:
        lcd.text(message1, 1)
        lcd.text(message2, 2)
    time.sleep(3)

def display_ip(message1, message2):
    with lcd_lock:
        lcd.text(message1, 1)
        lcd.text(message2, 2)
    time.sleep(4)

def clear_lcd():
    with lcd_lock:
        lcd.text("", 1)
        lcd.text("", 2)

def countdown(seconds):
    for i in range(seconds, 0, -1):
        with lcd_lock:
            lcd.text(f"Countdown: {i}", 2)
        time.sleep(1)

if __name__ == "__main__":
    if len(sys.argv) == 4:
        message1 = sys.argv[1]
        message2 = sys.argv[2] + " " + sys.argv[3]
        display_lcd(message1, message2)
        countdown(5)  # Countdown for 5 seconds
    elif len(sys.argv) == 3:
        message1 = sys.argv[1]
        message2 = sys.argv[2]
        if "IP:" in message1:
            display_ip(message1, message2)
        else:
            display_lcd(message1, message2)
    elif len(sys.argv) == 2 and sys.argv[1] == "clear":
        clear_lcd()
    clear_lcd()  # Clear the LCD after the countdown or immediately if no countdown
