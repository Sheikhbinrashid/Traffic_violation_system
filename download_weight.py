import cv2
import os
import pandas as pd
import csv
from datetime import datetime
from detectors import detect_objects
from traffic_light import classify_light_color
from plate_ocr_hf import read_plate
from tracker import CentroidTracker
from ultralytics import YOLO

# Core processing for video analysis
def analyze_video(
    video_path: str,
    location: str,
    snapshot_dir: str,
    detailed_csv: str,
    fined_csv: str,
    detect_scale: float = 0.5,
    stop_line_y: int = 700,
    tracker_max_disappeared: int = 40,
) -> tuple[int, int]:
    """
    Analyze a video for red-light violations.

    Args:
        video_path: path to input video file
        location: city name for logs
        snapshot_dir: directory for plate snapshots
        detailed_csv: path for per-violation logging
        fined_csv: path for summary logging
        detect_scale: scale factor for detection
        stop_line_y: y-coordinate of stop line
        tracker_max_disappeared: frames to tolerate missing objects

    Returns:
        (cars_passed, violations)
    """
    os.makedirs(snapshot_dir, exist_ok=True)
    vehicle_tracker = CentroidTracker(max_disappeared=tracker_max_disappeared)
    plate_model = YOLO('license-plate-finetune-v1x.pt')

    cap = cv2.VideoCapture(video_path)
    prev_centroids: dict[int, tuple[int,int]] = {}
    violated_ids: set[int] = set()
    cars_passed = 0
    violations = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        small = cv2.resize(frame, (0,0), fx=detect_scale, fy=detect_scale)
        vehicles_sm, tls_sm, _ = detect_objects(small)

        # scale vehicle bboxes back\        
        vehicles = [(
            int(x1/detect_scale), int(y1/detect_scale),
            int(x2/detect_scale), int(y2/detect_scale)
        ) for x1,y1,x2,y2 in vehicles_sm]

        # detect traffic light color
        current_light = None
        if tls_sm:
            tl = tls_sm[0]
            x1_t,y1_t,x2_t,y2_t = [int(v/detect_scale) for v in tl]
            current_light = classify_light_color(frame, (x1_t,y1_t,x2_t,y2_t))

        # track & count cars
        tracked = vehicle_tracker.update(vehicles)
        for oid, (cx, cy) in tracked.items():
            prev = prev_centroids.get(oid)
            if prev and prev[1] < stop_line_y <= cy:
                cars_passed += 1
                if current_light == 'red' and oid not in violated_ids:
                    violated_ids.add(oid)
                    violations += 1

                    # attempt to find matching plate bbox
                    vb = next((b for b in vehicles if b[0]<=cx<=b[2] and b[1]<=cy<=b[3]), None)
                    plate_bbox = None
                    if vb:
                        # detect plates on original frame
                        res = plate_model(frame)[0]
                        for det in res.boxes.xyxy.cpu().numpy():
                            x1p,y1p,x2p,y2p = map(int, det)
                            if x1p>=vb[0] and y1p>=vb[1] and x2p<=vb[2] and y2p<=vb[3]:
                                plate_bbox = (x1p,y1p,x2p,y2p)
                                break
                    if not plate_bbox:
                        res = plate_model(frame)[0]
                        if res.boxes:
                            bx = res.boxes.xyxy[0].cpu().numpy()
                            plate_bbox = tuple(map(int,bx))

                    if plate_bbox:
                        x1p,y1p,x2p,y2p = plate_bbox
                        crop = frame[y1p:y2p, x1p:x2p]
                        plate_text = read_plate(frame, plate_bbox) or 'UNKNOWN'
                        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                        fn = f"{ts}_{plate_text}.png"
                        cv2.imwrite(os.path.join(snapshot_dir, fn), crop)

                        # detailed log
                        row = {
                            'timestamp': datetime.now().isoformat(),
                            'city': location,
                            'plate': plate_text,
                            'snapshot': fn
                        }
                        first = not os.path.exists(detailed_csv)
                        with open(detailed_csv, 'a', newline='') as f:
                            w = csv.DictWriter(f, fieldnames=row.keys())
                            if first: w.writeheader()
                            w.writerow(row)

            prev_centroids[oid] = (cx, cy)

    cap.release()

    # summary log
    summary = {
        'timestamp': datetime.now().isoformat(),
        'location': location,
        'cars_passed': cars_passed,
        'violations': violations
    }
    first = not os.path.exists(fined_csv)
    with open(fined_csv, 'a', newline='') as f:
        w = csv.DictWriter(f, fieldnames=summary.keys())
        if first: w.writeheader()
        w.writerow(summary)

    return cars_passed, violations
