import os
import cv2
import numpy as np
import subprocess
import time
import board
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from gpiozero import Button, Device
from gpiozero.pins.lgpio import LGPIOFactory
from adafruit_servokit import ServoKit
from rpi_lcd import LCD
import busio
from signal import signal, SIGTERM, SIGHUP
import threading
import serial

# Set up LCD
lcd = LCD()

# Set up I2C bus
i2c = board.I2C()

# Set up ADS1115
ads = ADS.ADS1115(i2c)

# Set up joystick channels
chan_x = AnalogIn(ads, ADS.P0)  # VRX connected to A0
chan_y = AnalogIn(ads, ADS.P1)  # VRY connected to A1
chan_sw = AnalogIn(ads, ADS.P2)  # SW connected to A2

# Set up PCA9685
kit = ServoKit(channels=16)

# Set up GPIO for button input using gpiozero
Device.pin_factory = LGPIOFactory(chip=4)
button = Button(25, pull_up=True)
button2 = Button(24, pull_up=True)

deadband = 5000

# Initialize servo positions to None
servo_x_position = None
servo_y_position = None
kit.servo[1].angle = None
kit.servo[3].angle = None

# Define the servo channels
servo_channel_horizontal = 1
servo_channel_vertical = 3

# Initialize a lock for LCD display
lcd_lock = threading.Lock()

# Initialize serial communication
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
ser.flush()

servo_x_position = 90         # Initial horizontal servo position
servo_y_position = 90        # Initial vertical servo position

def track_object(servo_channel_horizontal, servo_channel_vertical, servo_x_position, servo_y_position, horizontal_step, vertical_step, return_horizontal_step, return_vertical_step):
    # Open the camera
    cap = cv2.VideoCapture(0)

    # Flag to track if a green object is detected
    green_object_detected = False

    # Timer to check if the object is detected for 5 seconds
    detection_start_time = None

    while read_button1() and button2.is_pressed:
        # Read the camera frame
        _, frame = cap.read()

        # Get the frame dimensions
        rows, cols, _ = frame.shape

        # Convert the frame to HSV color space
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Define the strong green color range
        low_green = np.array([45, 100, 100])
        high_green = np.array([75, 255, 255])

        # Create a mask for the green color
        green_mask = cv2.inRange(hsv_frame, low_green, high_green)

        # Find contours in the green mask
        contours, _ = cv2.findContours(green_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Sort the contours by area (largest first)
        contours = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)

        # Check if any contours are found
        if contours:
            cnt = contours[0]
            (x, y, w, h) = cv2.boundingRect(cnt)
            # Calculate the center of the detected object
            x_medium = int(x + (w / 2))
            y_medium = int(y + (h / 2))
            green_object_detected = True

            # Draw the bounding box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Start the timer if not already started
            if detection_start_time is None:
                detection_start_time = time.time()
        else:
            green_object_detected = False
            # Reset the timer
            detection_start_time = None
            # Set the center to the middle of the frame
            x_medium = cols // 2
            y_medium = rows // 2

        # Draw lines at the center of the bounding box or frame
        cv2.line(frame, (x_medium, 0), (x_medium, rows), (0, 255, 0), 2)
        cv2.line(frame, (0, y_medium), (cols, y_medium), (0, 255, 0), 2)

        # Add the label to the frame
        if green_object_detected:
            cv2.putText(frame, "monkey", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        else:
            cv2.putText(frame, "not_monkey", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Send serial command based on detection time
        if green_object_detected and detection_start_time and (time.time() - detection_start_time) >= 3:
            if detection_start_time is not None:
                ser.write(b"monkey\n")
                time.sleep(0.1)  # Delay between repeated commands
                ser.write(b"monkey\n")
                time.sleep(5)  # Rest for 5 seconds
                detection_start_time = None  # Reset the detection timer


        # Adjust the servo angles based on the object position
        if green_object_detected:
            if x_medium < cols // 3:
                servo_x_position += horizontal_step
            elif x_medium > (cols // 3) * 2:
                servo_x_position -= horizontal_step

            if y_medium < rows // 3:
                servo_y_position -= vertical_step
            elif y_medium > (rows // 3) * 2:
                servo_y_position += vertical_step
        else:
            # Return to initial position slowly if no green object is detected
            if servo_x_position > 90:
                servo_x_position -= return_horizontal_step
            elif servo_x_position < 90:
                servo_x_position += return_horizontal_step

            if servo_y_position > 140:
                servo_y_position -= return_vertical_step
            elif servo_y_position < 140:
                servo_y_position += return_vertical_step

        # Limit the servo angles between 0 and 180 degrees
        servo_x_position = max(0, min(180, servo_x_position))
        servo_y_position = max(0, min(180, servo_y_position))

        # Move the servos to the calculated angles
        kit.servo[servo_channel_horizontal].angle = servo_x_position
        kit.servo[servo_channel_vertical].angle = servo_y_position

        # Display the frame
        cv2.imshow("Frame", frame)

        # Exit the loop if the 'Esc' key is pressed
        key = cv2.waitKey(1)
        if key == 27:
            break

    # Release the camera and close the windows
    cap.release()
    cv2.destroyAllWindows()

            
def ai_mode():
    with lcd_lock:
        lcd.text("AI Mode:", 1)
        lcd.text("Running", 2)

def displayLcd():
    with lcd_lock:
        lcd.text("Mode :: Manual", 1)
        lcd.text("Calibration", 2)

def SWJoy():
    with lcd_lock:
        lcd.text("AI Ready :::", 1)
        lcd.text("Push Button 2", 2)
        time.sleep(5)

        # Countdown for 3 seconds
        for i in range(3, -1, -1):
            lcd.text(f"Counting down: {i}", 1)
            lcd.text("", 2)
            time.sleep(1)

        # Display for a while
        lcd.text("Back To", 1)
        lcd.text("Manual Mode", 2)
        time.sleep(3)
        lcd.text("", 1)
        lcd.text("", 2)
        

def clear():
    with lcd_lock:
        lcd.text("", 1)
        lcd.text("", 2)

def read_button1():
    return button.is_pressed

def read_joystick():
    x_val = chan_x.value
    y_val = chan_y.value
    sw_val = chan_sw.value  # Add this line to read the SW value
    return x_val, y_val, sw_val  # Add this line to return the SW value

def map_to_angle(val, min_val, max_val):
    mapped_val = int((val / (max_val - min_val)) * 180)
    return mapped_val

def apply_deadband(val, deadband):
    if abs(val) > deadband:
        return val
    else:
        return 0

def analog_to_direction(value, center_value_min, center_value_max):
    if value < center_value_min:
        return -1
    elif value > center_value_max:
        return 1
    else:
        return 0

def move_servos(x_val, y_val):
    global servo_x_position, servo_y_position

    # Initialize positions if None
    if servo_x_position is None:
        servo_x_position = kit.servo[1].angle if kit.servo[1].angle is not None else 90
    if servo_y_position is None:
        servo_y_position = kit.servo[3].angle if kit.servo[3].angle is not None else 90

    # Get direction from joystick for X axis #Adjust the direction to remove the drift shifting
    x_direction = analog_to_direction(x_val, 17500, 20070)
    # Get direction from joystick for Y axis #Adjust the direction to remove the drift shifting
    y_direction = analog_to_direction(y_val, 17500, 20500)

    # Calculate speed based on joystick position (wider range = faster speed)
    x_speed = int((abs(x_val - 17500) / 20070) * 5) + 1
    y_speed = int((abs(y_val - 17500) / 20500) * 5) + 1

    # Move servo X based on direction and speed
    if x_direction == 1:
        servo_x_position += x_speed
    elif x_direction == -1:
        servo_x_position -= x_speed

    # Move servo Y based on direction and speed
    if y_direction == 1:
        servo_y_position += y_speed
    elif y_direction == -1:
        servo_y_position -= y_speed

    # Clamp the servo positions to valid range [0, 180]
    servo_x_position = max(0, min(180, servo_x_position))
    servo_y_position = max(0, min(180, servo_y_position))

    # Update servo positions
    kit.servo[1].angle = servo_x_position
    kit.servo[3].angle = servo_y_position

    print(f"X Joystick value: {x_val}, X Direction: {x_direction}, X Speed: {x_speed}, X Servo position: {servo_x_position}")
    print(f"Y Joystick value: {y_val}, Y Direction: {y_direction}, Y Speed: {y_speed}, Y Servo position: {servo_y_position}")

def safe_exit(signum, frame):
    exit(1)

def lcd_thread():
    while True:
        if read_button1() and not button2.is_pressed:
            displayLcd()
        else:
            clear()
        time.sleep(0.5)

# Start the LCD display thread
lcd_thread_instance = threading.Thread(target=lcd_thread)
lcd_thread_instance.daemon = True
lcd_thread_instance.start()

swjoy_thread_running = False  # Flag to control swjoy_thread execution

def swjoy_thread():
    global sw_val, swjoy_thread_running
    if read_button1() and not button2.is_pressed and sw_val is not None and -10 < sw_val <= 5:
        SWJoy()
    clear()
    swjoy_thread_running = False  # Reset flag after the thread completes

button2_thread_running = False

def button2_thread():
    global button2_thread_running
    button2_released = False
    on_count = 0
    off_count = 0
    
    while read_button1() and button2.is_pressed:
        with lcd_lock:
            lcd.text("AI Mode:", 1)
            lcd.text("Running", 2)
        if on_count < 3:
            ser.write(b"button on\n")  # 'button on' command when button 2 is pressed
            on_count += 1
        time.sleep(0.1)  # Add a short delay to reduce CPU usage
    button2_thread_running = False
    button2_released = True
    clear()

    if button2_released:
        while off_count < 3:
            ser.write(b"button off\n")  # 'button off' command when button 2 is released
            off_count += 1
            time.sleep(0.1)  # Add a short delay to reduce CPU usage


# Main loop with correct function call
try:
    signal(SIGTERM, safe_exit)
    signal(SIGHUP, safe_exit)

    while True:
        x_val, y_val, sw_val_local = read_joystick()
        sw_val = sw_val_local  # Update the global sw_val
        
        # Handle button1 press
        if read_button1() and not button2.is_pressed:
            if -10 < sw_val <= 5 and not swjoy_thread_running:  # Check the flag before starting the thread
                swjoy_thread_running = True  # Set the flag to indicate the thread is running
                threading.Thread(target=swjoy_thread).start()
                print(sw_val)
                # Stop the servos while the thread is running
                kit.servo[1].angle = None
                kit.servo[3].angle = None
            elif not swjoy_thread_running:  # Only move servos if swjoy_thread is not running
                move_servos(x_val, y_val)
        
        if read_button1() and button2.is_pressed:
            horizontal_step = 2
            vertical_step = 2
            return_horizontal_step = 1.5 # Set the return speed for horizontal movement
            return_vertical_step = 1.5    # Set the return speed for vertical movement
            if not button2_thread_running:  # Check the flag before starting the thread
                button2_thread_running = True  # Set the flag to indicate the thread is running
                threading.Thread(target=button2_thread).start()
            while read_button1() and button2.is_pressed:
                track_object(
                    servo_channel_horizontal, servo_channel_vertical, 
                    servo_x_position, servo_y_position, 
                    horizontal_step, vertical_step, 
                    return_horizontal_step, return_vertical_step
                )

        time.sleep(0.01)

except KeyboardInterrupt:
    pass

finally:
    kit.servo[1].angle = None
    kit.servo[3].angle = None
    time.sleep(0.25)
    



