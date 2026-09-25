# Flood Detection and Early Warning using ESP Cam & Computer Vision

A university project prototype for detecting simulated flood conditions using an **ESP32-CAM, computer vision, and a GSM module**.

The system demonstrates how a camera-based flood monitoring system can identify a simulated flood area and provide an **early warning through an automated phone call** when the detected level reaches a critical threshold.

> **Note:** This is a prototype developed for academic and demonstration purposes. The flood condition is simulated using a black sheet/paper as a visual representation of water/flooded area.

---

## 📌 Project Overview

Floods can develop rapidly and early warnings can help reduce potential damage and improve response time.

This project explores a low-cost computer-vision-based approach to flood detection.

An **ESP32-CAM** captures the monitoring area and sends the video stream to a computer. The system uses **OpenCV-based image processing** to analyze the incoming frames and detect the simulated flood region.

When the detected flood area reaches predefined levels, the system classifies the situation according to its severity.

If the detected level reaches the critical threshold, a **GSM module can automatically make a phone call to a predefined number**, demonstrating an early-warning mechanism.

---

## 🎯 Project Objectives

The main objectives of this project are:

* Detect a simulated flood condition using computer vision.
* Use an ESP32-CAM as the monitoring camera.
* Process the camera stream in real time.
* Estimate the percentage of the detected flood area.
* Classify the detected condition into different risk levels.
* Provide an automated early warning when a critical level is reached.
* Demonstrate GSM-based emergency calling.
* Develop a low-cost prototype for academic research and demonstration.

---

## 🧪 Flood Simulation

Since this is a university prototype, a real flood environment is not required.

A **black sheet/paper is placed in the monitored area to simulate the flooded region**.

The computer vision system detects the visual region and calculates its approximate coverage within the camera frame.

This allows the flood detection and warning mechanism to be demonstrated in a controlled environment.

### Prototype Concept

```text
Black Sheet / Paper
        ↓
Simulated Flood Area
        ↓
ESP32-CAM
        ↓
Video Stream
        ↓
Computer Vision
        ↓
Flood Area Detection
        ↓
Flood Percentage
        ↓
Risk Level
        ↓
Critical Level?
      ↙     ↘
    No       Yes
    ↓         ↓
 Monitor   GSM Alert
              ↓
        Automated Call
```

---

## ⚙️ How the System Works

### 1. Image Capture

The **ESP32-CAM** captures video from the monitored area.

### 2. Video Streaming

The camera provides an HTTP video stream to the computer running the application.

### 3. Computer Vision Processing

The application processes the incoming frames using **OpenCV and NumPy**.

The system identifies the target region and calculates the approximate percentage of the frame occupied by the detected area.

### 4. Flood Level Classification

The calculated percentage is mapped to different risk levels.

Example:

| Detected Area | Risk Level |
| ------------: | ---------- |
|         < 20% | SAFE       |
|        20–39% | LOW        |
|        40–59% | MEDIUM     |
|        60–79% | HIGH       |
|          80%+ | CRITICAL   |

These thresholds are prototype values and can be calibrated for a real deployment environment.

### 5. Early Warning

When the detected level reaches the configured critical threshold, the system can trigger an automated phone call using a **GSM module**.

This demonstrates the concept of an early-warning mechanism where the monitoring system can notify a responsible person without requiring continuous manual observation.

---

## 🚨 Early Warning System

The project supports GSM-based alerting through a GSM module such as **SIM900L**.

When a critical condition is detected:

```text
CRITICAL FLOOD LEVEL
        ↓
Detection System
        ↓
GSM Module
        ↓
Phone Call
        ↓
Responsible Person
```

The system can therefore demonstrate how computer vision and cellular communication can work together for automated early warning.

---

## 🖥️ Dashboard

The project includes a Flask-based web interface for monitoring the camera stream and detection results.

The dashboard can display information such as:

* Live camera feed
* Detection status
* Flood percentage
* Current risk level
* Detection settings
* Critical threshold
* GSM configuration

---

## 🛠️ Technologies Used

### Hardware

* ESP32-CAM
* GSM Module / SIM900L
* Computer/Laptop
* SIM Card
* Prototype flood simulation material

### Software

* Python
* Flask
* OpenCV
* NumPy
* PySerial
* HTML
* CSS
* JavaScript

### Communication

* ESP32-CAM HTTP video streaming
* Serial communication with GSM module
* GSM voice call for early warning

---

## 📂 Project Structure

```text
Flood_Project/
│
├── app.py
├── detector.py
├── call.py
├── gsm_call.py
├── sim900_call_test.py
├── gsm_settings.json
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── templates/
│   └── index.html
│
└── static/
    ├── script.js
    └── style.css
```

---

## 🚀 Installation

Clone the repository:

```bash
git clone https://github.com/YOUR-USERNAME/flood-detection-and-early-warning-esp-cam.git
```

Navigate to the project:

```bash
cd flood-detection-and-early-warning-esp-cam
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python app.py
```

Open the dashboard:

```text
http://127.0.0.1:5000
```

---

## 📷 ESP32-CAM

The ESP32-CAM provides the video stream used by the computer vision system.

Example stream URL:

```text
http://192.168.x.x:81/stream
```

The exact IP address depends on the local network configuration of the ESP32-CAM.

---

## 📞 GSM Early Warning

The GSM module is used to demonstrate automated emergency calling.

The system can initiate a call when the detected flood level reaches the configured critical threshold.

For security, sensitive credentials and personal phone numbers should not be committed to the repository.

---

## 🔐 Security

Do not upload:

* API keys
* Twilio credentials
* Personal phone numbers
* Passwords
* `.env` files
* Other private credentials

Use environment variables for sensitive credentials.

---

## 🎓 Academic Project

This project was developed as a **university academic project** to demonstrate the integration of:

**Computer Vision + IoT Camera + Real-Time Monitoring + GSM Communication + Early Warning**

The current implementation is a prototype and is not intended to replace certified flood monitoring or emergency-warning infrastructure.

---

## 🔮 Future Improvements

Possible future development includes:

* Machine-learning-based flood segmentation
* Real water-level sensors
* Multiple ESP32-CAM monitoring points
* SMS alerts
* Mobile notifications
* GPS-based location identification
* Cloud-based monitoring
* Historical flood-level data
* Database integration
* Weather and rainfall data integration
* More robust environmental calibration
* Solar-powered deployment
* Real-world field testing

---

## 👨‍💻 Project Type

**University Project / Computer Vision & IoT Prototype**

**Domain:** Flood Detection, Computer Vision, IoT, Early Warning Systems

**Status:** Prototype

---

## ⚠️ Disclaimer

This project uses a controlled visual simulation to demonstrate flood detection. The black sheet/paper used in the prototype represents the simulated flooded area.

The detection thresholds and image-processing approach have not been validated for real-world flood monitoring. Real-world deployment would require extensive testing, calibration, environmental validation, and appropriate safety certification.
