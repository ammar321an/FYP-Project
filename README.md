# 🚀 FYP Project: NERF TURRET-INSPIRED GARDEN GUARDIAN

Welcome to my Final Year Project! This project is inspired by the NERF turret and focuses on Computer Vision and IoT for monkey deterrence.

---

## 🌟 Project Title

**NERF TURRET-INSPIRED GARDEN GUARDIAN: COMPUTER VISION & IOT MONKEY DETERRENCE**

---

## 📜 Project Description

This project aims to detect monkeys using an AI model for object detection, ensuring accurate results. The deterrent mechanism employs a 5-inch 30-watt speaker with an amplifier to produce very loud sounds.

### ⚙️ How It Works

1. **Setup**: Place the robot in a high location to guard the garden. The robot's head can move horizontally and vertically to find monkeys.
2. **Buttons**:
    - **Button 1**: Powers on the robot.
    - **Button 2**: Activates manual mode for initial calibration.
    - **Button 3**: Activates AI mode for monkey detection.
3. **WiFi Connection**: The display shows the WiFi or hotspot connection and IP address. Use this IP to open the website on port 5000.
4. **Web Interface**: The website includes live video streaming, registration, and login pages for security. The owner's email and contact number are used for email and WhatsApp notifications.
5. **Detection & Notification**: If a monkey is detected for 3 seconds, the robot emits a sound and sends notifications.

---

## 🔧 Key Components

| Component                     | Description                                                |
|-------------------------------|------------------------------------------------------------|
| **Raspberry Pi 4**            | Main processing unit                                       |
| **Arduino Uno R4**            | Receives commands from the Raspberry Pi to activate the motion sensor and speaker |
| **PCA9685**                   | PWM controller for servos                                  |
| **180° Servo Motors (x2)**    | Enables head movement                                      |
| **5-inch 30W Speaker**        | Outputs deterrent sound                                    |
| **DFPlayer Mini**             | Plays sound files                                          |
| **Amplifier Module (TDA7255)**| Amplifies the sound                                        |
| **ADS1115 Module**            | Analog-to-digital converter                                |
| **Joystick Module**           | Manual control interface                                   |
| **Metal Latch Buttons (x3)**  | Controls power and modes                                   |
| **LCD 1602**                  | Displays connection info                                   |
| **Webcam**                    | Provides video feed                                        |
| **Cooling Fan**               | Prevents overheating                                       |
| **DC Jack (Female)**          | For charging                                               |
| **12V Battery**               | Powers the system                                          |
| **Voltage Regulators (x2)**   | Regulates power supply                                     |
| **Wiring & Resistors**        | Connects components securely                               |
| **Battery Display Module**    | Shows battery percentage                                   |
| **Bearing**                   | Provides smooth rotational movement                        |
| **Metal Base**                | Designed with SolidWorks and bent for the base structure   |
| **3D Printed Head**           | Designed with SolidWorks for the robot's head              |

---

## 🌐 Web Interface Features

- **Live Video Streaming**: Monitor the garden in real-time.
- **User Authentication**: Secure login and registration with email and contact number.
- **Email & WhatsApp Notifications**: Alerts sent when a monkey is detected.

---

## 📞 Contact

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://www.linkedin.com/in/muhammad-ammar-yaseer-azizan-48b28a235/)
[![Linktree](https://img.shields.io/badge/Linktree-Visit-green)](https://linktr.ee/ammarysr)

---

Thank you for exploring my project! Feel free to reach out if you have any questions or would like to collaborate.
