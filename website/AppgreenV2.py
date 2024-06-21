import os
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template, redirect, url_for, request, flash, Response, session, current_app, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TelField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
import cv2
import subprocess
import numpy as np
from ultralytics import YOLO
import torch
from pathlib import Path
from datetime import datetime, timedelta
import pytz
import threading
import time
import logging
from werkzeug.local import LocalProxy
from adafruit_servokit import ServoKit
import serial


ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)  # Adjust the serial port and baud rate as needed

malaysia_tz = pytz.timezone('Asia/Kuala_Lumpur')

# Set up PCA9685
kit = ServoKit(channels=16)

def malaysia_time():
    return datetime.now(malaysia_tz)

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_PERMANENT'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    contact_number = db.Column(db.String(20), nullable=True)
    registered_on = db.Column(db.DateTime, nullable=False, default=malaysia_time)

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    contact_number = TelField('Contact Number', validators=[Optional()])  # New field, Optional
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
    

FRAMES_FOR_5_SECONDS = 150
monkey_counter = 0

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_frames(user_email):
    # Open the camera
    cap = cv2.VideoCapture(0)

    # Initialize the previous time for FPS calculation
    prev_time = 0
    fps = 0

    # Initialize servo positions and channels
    servo_x_position = 90
    servo_y_position = 90
    servo_channel_horizontal = 1
    servo_channel_vertical = 3

    # Servo movement parameters
    horizontal_step = 2
    vertical_step = 2
    return_horizontal_step = 1.5
    return_vertical_step = 1.5

    # Timer to check if the object is detected for 5 seconds
    detection_start_time = None

    while True:
        ret, frame = cap.read()  # Capture frame-by-frame
        if not ret:
            break

        frame = cv2.flip(frame, 1)  # Flip horizontally
        frame = cv2.resize(frame, (640, 480))  # Reduce the resolution

        # Calculate the FPS
        current_time = time.time()
        if prev_time == 0:
            fps = 0
        else:
            fps = 1 / (current_time - prev_time)
        prev_time = current_time

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

            # Adjust the servo angles based on the object position
            if x_medium < cols // 3:
                servo_x_position -= horizontal_step
            elif x_medium > (cols // 3) * 2:
                servo_x_position += horizontal_step

            if y_medium < rows // 3:
                servo_y_position -= vertical_step
            elif y_medium > (rows // 3) * 2:
                servo_y_position += vertical_step
        else:
            green_object_detected = False
            # Reset the timer
            detection_start_time = None
            # Set the center to the middle of the frame
            x_medium = cols // 2
            y_medium = rows // 2

            # Return to initial position slowly if no green object is detected
            if servo_x_position > 90:
                servo_x_position -= return_horizontal_step
            elif servo_x_position < 90:
                servo_x_position += return_horizontal_step

            if servo_y_position > 90:
                servo_y_position -= return_vertical_step
            elif servo_y_position < 90:
                servo_y_position += return_vertical_step

        # Limit the servo angles between 0 and 180 degrees
        servo_x_position = max(0, min(180, servo_x_position))
        servo_y_position = max(0, min(180, servo_y_position))

        # Move the servos to the calculated angles
        kit.servo[servo_channel_horizontal].angle = servo_x_position
        kit.servo[servo_channel_vertical].angle = servo_y_position

        # Draw lines at the center of the detected object or frame
        cv2.line(frame, (x_medium, 0), (x_medium, rows), (0, 255, 0), 2)
        cv2.line(frame, (0, y_medium), (cols, y_medium), (0, 255, 0), 2)

        # Add the label to the frame
        if green_object_detected:
            cv2.putText(frame, "monkey", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        else:
            cv2.putText(frame, "not_monkey", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Check for monkey detection and run email/whatsapp threads
        if green_object_detected and detection_start_time and (time.time() - detection_start_time) >= 5:
            logging.info("Monkey detected")
            if user_email:
                # Call the run_whatsapp and run_email functions with user_email
                thread_whatsapp = threading.Thread(target=run_whatsapp, args=(user_email,))
                thread_email = threading.Thread(target=run_email, args=(user_email,))
                thread_whatsapp.start()
                thread_email.start()

            # Send serial command to Arduino
            ser.write(b"monkey\n")
            time.sleep(0.1)  # Short delay between repeated commands
            ser.write(b"monkey\n")
            time.sleep(5)  # Rest for 5 seconds
            detection_start_time = None  # Reset the detection timer

        else:
            logging.info("No monkey detected")

        # Add the FPS to the frame
        cv2.putText(frame, f"FPS: {int(fps)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Convert the frame to JPEG format
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()
    cv2.destroyAllWindows()




@app.route("/video_feed")
def video_feed():
    user_email = session.get('user_email')
    if not user_email:
        abort(401, description="Unauthorized: User email not provided.")
    return Response(generate_frames(user_email), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if the contact number already exists
        contact_number_exists = User.query.filter_by(contact_number=form.contact_number.data).first()
        if contact_number_exists:
            return jsonify(status='error', message='Contact number already in use. Please choose another one.')

        user = User(
            name=form.name.data,
            email=form.email.data,
            password=form.password.data,
            contact_number=form.contact_number.data
        )
        db.session.add(user)
        try:
            db.session.commit()
            return jsonify(status='success', message='Your account has been created!')
        except IntegrityError:  # Email already exists
            db.session.rollback()
            return jsonify(status='error', message='Email already in use. Please choose another one.')
    return render_template('register.html', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:
            session['user_email'] = user.email
            session.permanent = True
            return jsonify(status='success', message='You have been logged in!')
        else:
            return jsonify(status='error', message='Login Unsuccessful. Please check email and password')
    return render_template('login.html', form=form)

def run_script_with_context(script_name, duration, user_email, user_contact_number=None):
    def _run_script():
        with app.app_context():
            start_time = time.time()
            args = [script_name, user_email]
            if user_contact_number:
                args.append(user_contact_number)
            process = subprocess.Popen(['python'] + args)
            while time.time() - start_time < duration:
                time.sleep(0.1)  # Check every 0.1 seconds
            process.terminate()
            try:
                process.wait(timeout=1)  # Wait for up to 1 second
            except subprocess.TimeoutExpired:
                process.kill()  # Force kill if it doesn't terminate

    thread = threading.Thread(target=_run_script)
    thread.start()

@app.route("/run_email")
def run_email(user_email):
    print(f"Running email notification for user: {user_email}")
    run_script_with_context('alert_email.py', 5, user_email)
    with app.app_context():
        current_app.logger.info('Email script is running for 5 seconds...')
    return redirect(url_for('dashboard'))

@app.route("/run_whatsapp")
def run_whatsapp(user_email):
    def whatsapp_task():
        with app.app_context():
            user = User.query.filter_by(email=user_email).first()
            if not user:
                print(f"User with email {user_email} not found.")
                return
            print(f"Running WhatsApp notification for user: {user_email}")
            run_script_with_context('alert_whatsapp.py', 5, user_email, user.contact_number)

    thread = threading.Thread(target=whatsapp_task)
    thread.start()
    with app.app_context():
        current_app.logger.info('WhatsApp script is running for 5 seconds...')
    return redirect(url_for('dashboard'))

@app.route("/dashboard")
def dashboard():
    # Get session after login
    user_email = session.get('user_email')
    if not user_email:
        flash('Please log in to access the dashboard.', 'danger')
        return redirect(url_for('login'))
    return render_template('dashboard.html', user_email=user_email)

@app.route('/start_streaming')
def start_streaming():
    user_email = session.get('user_email')
    if not user_email:
        abort(401, description="Unauthorized: User email not provided.")
    
    # Send the "streamStart" command three times
    for _ in range(3):
        ser.write(b"streamStart\n")
        time.sleep(0.1)  # Delay between commands

    return render_template('video_feed.html')

@app.route('/back')
def back():
    # Send the "streamStop" command three times
    for _ in range(3):
        ser.write(b"streamStop\n")
        time.sleep(0.1)  # Delay between commands
    return redirect(url_for('dashboard'))

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='172.20.10.2', port=5000) #Put your Raspberry Pi IP


