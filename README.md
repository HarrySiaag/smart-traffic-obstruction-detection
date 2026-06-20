# Smart Traffic Monitoring and Obstruction Detection for Emergency Vehicle Path Management

## Overview

This project is an AI-powered traffic monitoring system developed to detect vehicles obstructing the path of emergency vehicles such as ambulances, police vehicles, and fire brigades.

The system uses Computer Vision, Vehicle Tracking, Obstruction Analysis, OCR-based Number Plate Recognition, and a Web Dashboard to identify violations and store evidence automatically.

---

## Problem Statement

Emergency vehicles often face delays because vehicles ahead fail to provide a clear path.

The objective of this project is to:

* Detect vehicles in front of an emergency vehicle
* Monitor their movement
* Determine whether they are obstructing the emergency vehicle
* Capture evidence of violations
* Extract vehicle number plate information
* Display violations through a dashboard

---

## Features

### Vehicle Detection

* Real-time vehicle detection using YOLOv8n
* Supports:

  * Cars
  * Buses
  * Trucks
  * Motorcycles

### Vehicle Tracking

* ByteTrack-based tracking
* Unique ID assigned to every detected vehicle
* Continuous tracking across frames

### Front Vehicle Identification

* Identifies the nearest vehicle in the emergency vehicle's lane
* Ignores side-lane vehicles

### Obstruction Detection

* Virtual lane analysis
* Baseline-based obstruction monitoring
* Movement analysis of front vehicle

### Warning Escalation System

* Green Warning (0–2 seconds)
* Yellow Warning (2–4 seconds)
* Red Warning (4+ seconds)

### Evidence Generation

* Captures complete frame image
* Captures violating vehicle image
* Adds timestamp to saved evidence

### OCR Number Plate Recognition

* EasyOCR integration
* Number plate extraction
* Indian registration format correction

### Violation Logging

* Stores violation records in JSON format
* Maintains:

  * Vehicle ID
  * Number Plate
  * Timestamp
  * Status
  * Evidence Image Paths

### Frontend Dashboard

* Displays total violations
* Shows captured vehicle images
* Shows number plates
* Shows timestamps
* Provides evidence viewing functionality

---

## Technologies Used

### Backend

* Python
* OpenCV
* YOLOv8n
* ByteTrack
* EasyOCR
* NumPy

### Frontend

* HTML
* CSS
* JavaScript

---

## Project Structure

```text
Smart-Traffic-Obstruction-Detection
│
├── Traffic Violation Frontend
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   │
│   └── violations
│       ├── violations.json
│       ├── vehicle_xxx.jpg
│       └── frame_xxx.jpg
│
├── detect.py
├── number_plate.jpg
├── traffic.mp4
├── traffic2.mp4
├── traffic4.mp4
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/smart-traffic-obstruction-detection.git
```

Navigate to project folder:

```bash
cd smart-traffic-obstruction-detection
```

---

## Create Virtual Environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / Mac

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Required Packages

```text
ultralytics
opencv-python
easyocr
numpy
torch
torchvision
```

---

## Running the Project

Place your input traffic video in the project directory.

Update video path inside:

```text
detect.py
```

Run:

```bash
python detect.py
```

---

## Generated Output

Whenever a violation is confirmed:

The system automatically generates:

### Full Evidence Frame

```text
frame_<id>_<timestamp>.jpg
```

### Vehicle Crop

```text
vehicle_<id>_<timestamp>.jpg
```

### OCR Result

```text
plate_<id>_<timestamp>.txt
```

### Violation Log

```text
violations.json
```

Example:

```json
[
  {
    "vehicle_id": 1,
    "plate_number": "MH01AV8866",
    "timestamp": "2026-05-22 04:05:13",
    "status": "OBSTRUCTION",
    "frame_image": "violations/frame_1.jpg",
    "vehicle_image": "violations/vehicle_1.jpg"
  }
]
```

---

## Frontend Dashboard

Open:

```text
Traffic Violation Frontend/index.html
```

using:

* VS Code Live Server
  or
* Any local web server

Dashboard displays:

* Total Violations
* Vehicle Image
* Vehicle Number Plate
* Timestamp
* Evidence Viewer

---

## System Workflow

```text
Input Video
      ↓
YOLOv8 Vehicle Detection
      ↓
ByteTrack Vehicle Tracking
      ↓
Front Vehicle Identification
      ↓
Movement Analysis
      ↓
Obstruction Detection
      ↓
Warning Escalation
      ↓
Violation Confirmation
      ↓
Evidence Capture
      ↓
OCR Number Plate Recognition
      ↓
JSON Logging
      ↓
Frontend Dashboard
```

---

## Team Member Roles

### Team Member 1 – Detection and Tracking Module

Responsibilities:

* YOLOv8 vehicle detection
* ByteTrack vehicle tracking
* Vehicle ID assignment
* Front vehicle identification

### Team Member 2 – Obstruction Analysis Module

Responsibilities:

* Lane division logic
* Obstruction baseline implementation
* Warning escalation system
* Evidence capture
* OCR number plate extraction

### Team Member 3 – Frontend Dashboard and System Integration

Responsibilities:

* Dashboard development
* JSON integration
* Evidence visualization
* Vehicle card generation
* Complete system integration

---

## Future Scope

* Automatic E-Challan Generation
* Live CCTV Deployment
* Cloud Database Integration
* Mobile Application
* Smart City Integration
* GPS-based Emergency Vehicle Tracking
* Real-Time Traffic Authority Alerts

---

## Authors

Capstone Project

Smart Traffic Monitoring and Obstruction Detection for Emergency Vehicle Path Management

Developed using:

* YOLOv8n
* OpenCV
* ByteTrack
* EasyOCR
* HTML
* CSS
* JavaScript

---

## License

This project is intended for academic and research purposes only.
