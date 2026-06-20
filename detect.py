from ultralytics import YOLO
import easyocr
import cv2
import time
import os
import json
from datetime import datetime


captured_violations = set()

# ============================================
# FRONTEND VIOLATIONS FOLDER
# ============================================

VIOLATION_FOLDER = (
    "Traffic Violation Frontend/violations"
)

os.makedirs(VIOLATION_FOLDER, exist_ok=True)

json_file = (
    f"{VIOLATION_FOLDER}/violations.json"
)

# Create empty JSON file if not exists
if not os.path.exists(json_file):

    with open(json_file, "w") as f:
        json.dump([], f)

# ============================================
# LOAD YOLO MODEL
# ============================================
model = YOLO("yolov8n.pt")

# ============================================
# LOAD OCR MODEL
# ============================================
reader = easyocr.Reader(['en'])

# ============================================
# VIDEO INPUT
# ============================================
video_path = "traffic.mp4"
cap = cv2.VideoCapture(video_path)

# ============================================
# CUSTOM NUMBER PLATE IMAGE
# ============================================
number_plate_image = cv2.imread("number_plate.jpg")

# ============================================
# GLOBAL VARIABLES
# ============================================
allowed_classes = ["car", "truck", "bus", "motorcycle"]

# obstruction timer
obstruction_start_time = {}

# ============================================
# MAIN LOOP
# ============================================
while cap.isOpened():

    ret, frame = cap.read()

    if not ret:
        break

    # ============================================
    # FRAME SETTINGS
    # ============================================
    frame = cv2.resize(frame, (1280, 720))

    frame_height, frame_width, _ = frame.shape

    # ============================================
    # CENTER LANE REGION
    # ============================================
    CENTER_X1 = int(frame_width * 0.32)
    CENTER_X2 = int(frame_width * 0.68)

    # ============================================
    # SIDE LANES
    # ============================================
    LEFT_X2 = CENTER_X1
    RIGHT_X1 = CENTER_X2

    # ============================================
    # OBSTRUCTION BASELINE
    # ============================================
    BASELINE_Y = int(frame_height * 0.72)

    # ============================================
    # YOLO TRACKING
    # ============================================
    results = model.track(
        frame,
        persist=True,
        tracker="bytetrack.yaml",
        conf=0.35
    )

    detections = []

    # ============================================
    # COLLECT DETECTIONS
    # ============================================
    for result in results:

        boxes = result.boxes

        if boxes.id is not None:
            ids = boxes.id.int().cpu().tolist()
        else:
            ids = [None] * len(boxes)

        for box, track_id in zip(boxes, ids):

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            cls = int(box.cls[0])
            label = model.names[cls]

            # Filter only vehicle classes
            if label not in allowed_classes:
                continue

            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

            area = (x2 - x1) * (y2 - y1)

            detections.append({
                "id": track_id,
                "label": label,
                "bbox": (x1, y1, x2, y2),
                "center": (center_x, center_y),
                "area": area
            })

    # ============================================
    # FRONT VEHICLE DETECTION
    # ============================================

    front_vehicle = None

    closest_y = 0
    largest_area = 0

    for d in detections:

        center_x, center_y = d["center"]

        x1, y1, x2, y2 = d["bbox"]

        # Must be inside center lane
        if CENTER_X1 < center_x < CENTER_X2:

            # Vehicle closest to camera
            vehicle_bottom = y2

            # Priority 1 → closest to bottom
            # Priority 2 → largest area
            if (
                vehicle_bottom > closest_y
                or
                (
                    vehicle_bottom == closest_y
                    and d["area"] > largest_area
                )
            ):

                closest_y = vehicle_bottom
                largest_area = d["area"]

                front_vehicle = d

    # ============================================
    # SIDE LANE OCCUPANCY
    # ============================================
    left_lane_occupied = False
    right_lane_occupied = False

    for d in detections:

        center_x, _ = d["center"]

        # Ignore front vehicle
        if front_vehicle is not None and d["id"] == front_vehicle["id"]:
            continue

        # Left lane occupied
        if center_x < LEFT_X2:
            left_lane_occupied = True

        # Right lane occupied
        if center_x > RIGHT_X1:
            right_lane_occupied = True

    # At least one side lane should be free
    side_space_available = (
        not left_lane_occupied
        or
        not right_lane_occupied
    )

    # ============================================
    # PROCESS DETECTIONS
    # ============================================
    for d in detections:

        track_id = d["id"]

        x1, y1, x2, y2 = d["bbox"]

        label = d["label"]

        # ============================================
        # DEFAULT SETTINGS
        # ============================================
        color = (0, 255, 0)

        display_label = f"{label} ID:{track_id}"

        # ============================================
        # FRONT VEHICLE
        # ============================================
        if (
            front_vehicle is not None
            and
            track_id == front_vehicle["id"]
        ):

            # Default front vehicle appearance
            color = (255, 0, 0)

            display_label = f"FRONT VEHICLE ID:{track_id}"

            # ============================================
            # BASELINE CHECK
            # ============================================
            obstruction = False

            vehicle_bottom = y2

            # Vehicle crosses baseline
            if vehicle_bottom > BASELINE_Y:

                # Space available to move aside
                if side_space_available:

                    obstruction = True

            # ============================================
            # OBSTRUCTION TIMER
            # ============================================
            if obstruction:

                # Start timer
                if track_id not in obstruction_start_time:
                    obstruction_start_time[track_id] = time.time()

                elapsed = (
                    time.time()
                    -
                    obstruction_start_time[track_id]
                )

                # ========================================
                # GREEN STAGE
                # ========================================
                if elapsed < 2:

                    color = (0, 255, 0)

                    display_label = (
                        f"WARNING ID:{track_id}"
                    )

                # ========================================
                # YELLOW STAGE
                # ========================================
                elif elapsed < 4:

                    color = (0, 255, 255)

                    display_label = (
                        f"POTENTIAL OBSTRUCTION ID:{track_id}"
                    )

                # ========================================
                # RED STAGE
                # ========================================
                else:

                    color = (0, 0, 255)

                    display_label = (
                        f"OBSTRUCTING ID:{track_id}"
                    )

                    # ====================================
                    # SAVE VIOLATION ONLY ONCE
                    # ====================================
                    if track_id not in captured_violations:

                        timestamp = datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )

                        filename_timestamp = datetime.now().strftime(
                            "%Y%m%d_%H%M%S"
                        )

                        # ====================================
                        # COPY FRAME FOR TIMESTAMP DRAWING
                        # ====================================
                        evidence_frame = frame.copy()

                        # Draw timestamp on full frame
                        cv2.putText(
                            evidence_frame,
                            f"Violation Time: {timestamp}",
                            (30, 50),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (0, 0, 255),
                            3
                        )

                        # Save full evidence frame
                        frame_path = (
                            f"{VIOLATION_FOLDER}/frame_"
                            f"{track_id}_{filename_timestamp}.jpg"
                        )

                        cv2.imwrite(frame_path, evidence_frame)

                        # ====================================
                        # CROPPED VEHICLE IMAGE
                        # ====================================
                        vehicle_crop = frame[y1:y2, x1:x2].copy()

                        # Add timestamp to crop
                        cv2.putText(
                            vehicle_crop,
                            timestamp,
                            (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 0, 255),
                            2
                        )

                        crop_path = (
                            f"{VIOLATION_FOLDER}/vehicle_"
                            f"{track_id}_{filename_timestamp}.jpg"
                        )

                        cv2.imwrite(crop_path, vehicle_crop)

                        print(
                            f"[INFO] Violation Captured: {track_id}"
                        )

                        captured_violations.add(track_id)   

                        # ====================================
                        # NUMBER PLATE EXTRACTION
                        # ====================================

                        ocr_results = reader.readtext(number_plate_image)

                        plate_text = "UNKNOWN"

                        if len(ocr_results) > 0:

                            # Take highest confidence text
                            plate_text = ocr_results[0][1]

                        # ====================================
                        # FORMAT INDIAN NUMBER PLATE
                        # ====================================

                        plate_text = plate_text.upper()

                        # Remove spaces
                        plate_text = plate_text.replace(" ", "")

                        corrected = ""

                        for i, ch in enumerate(plate_text):

                            # First 2 should be alphabets
                            if i < 2:

                                if ch == "0":
                                    ch = "O"

                                elif ch == "1":
                                    ch = "I"

                            # Next 2 should be numbers
                            elif i < 4:

                                if ch == "O":
                                    ch = "0"

                                elif ch == "I":
                                    ch = "1"

                                elif ch == "A":
                                    ch = "4"

                            # Remaining alphanumeric corrections
                            else:

                                if ch == "O":
                                    ch = "0"

                            corrected += ch

                        plate_text = corrected
                        
                        # Common OCR fixes
                        plate_text = (
                            plate_text
                            .replace("4V", "AV")
                        )

                        print(f"[NUMBER PLATE]: {plate_text}")

                        # Save extracted plate number
                        txt_path = (
                            f"{VIOLATION_FOLDER}/plate_{track_id}_{filename_timestamp}.txt"
                        )

                        with open(txt_path, "w") as f:

                            f.write(f"Detected Plate Number: {plate_text}")     

                        # ====================================
                        # SAVE VIOLATION DATA TO JSON
                        # ====================================

                        violation_data = {
                            "vehicle_id": track_id,
                            "plate_number": plate_text,
                            "timestamp": timestamp,
                            "status": "OBSTRUCTION",
                            "frame_image": frame_path.replace(
                                "Traffic Violation Frontend/", ""
                            ),

                            "vehicle_image": crop_path.replace(
                                "Traffic Violation Frontend/", ""
                            )
                        }

                        # Read existing JSON
                        with open(json_file, "r") as f:

                            data = json.load(f)

                        # Append new violation
                        data.append(violation_data)

                        # Save updated JSON
                        with open(json_file, "w") as f:

                            json.dump(data, f, indent=4)                            

            else:

                # Reset timer
                if track_id in obstruction_start_time:
                    del obstruction_start_time[track_id]

        # ============================================
        # DRAW BOX
        # ============================================
        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            color,
            2
        )

        cv2.putText(
            frame,
            display_label,
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2
        )

    # ============================================
    # DRAW CENTER LANE LINES
    # ============================================
    cv2.line(
        frame,
        (CENTER_X1, 0),
        (CENTER_X1, frame_height),
        (255, 255, 255),
        1
    )

    cv2.line(
        frame,
        (CENTER_X2, 0),
        (CENTER_X2, frame_height),
        (255, 255, 255),
        1
    )

    # ============================================
    # DRAW BASELINE
    # ============================================
    cv2.line(
        frame,
        (0, BASELINE_Y),
        (frame_width, BASELINE_Y),
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        "OBSTRUCTION BASELINE",
        (40, BASELINE_Y - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )

    # ============================================
    # SHOW OUTPUT
    # ============================================
    cv2.imshow(
        "Emergency Vehicle Obstruction Detection",
        frame
    )

    # Exit key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ============================================
# CLEANUP
# ============================================
cap.release()
cv2.destroyAllWindows()