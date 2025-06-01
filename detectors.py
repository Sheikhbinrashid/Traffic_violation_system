# detectors.py

from ultralytics import YOLO

# 1. Load a pretrained YOLO model. 
#    'yolov8n.pt' is the lightweight nano model—fast to download & test.
model = YOLO('yolov8n.pt')

# Define COCO class IDs for vehicles & traffic lights
VEHICLE_CLASSES = {2, 3, 5, 7}   # car, motorcycle, bus, truck
TRAFFIC_LIGHT_CLASS = 9

def detect_objects(frame):
    """
    Runs YOLO on `frame` and returns:
      - vehicle_boxes: list of [x1,y1,x2,y2]
      - tl_boxes:      list of [x1,y1,x2,y2]
      - raw_results:   the full YOLO results object (for debugging)
    """
    results = model(frame)[0]  
    vehicle_boxes = []
    tl_boxes = []
    
    # Iterate detections
    for box, cls in zip(results.boxes.xyxy, results.boxes.cls):
        coords = box.cpu().numpy().tolist()     # [x1, y1, x2, y2]
        cls_id  = int(cls.cpu().numpy())
        
        if cls_id in VEHICLE_CLASSES:
            vehicle_boxes.append(coords)
        elif cls_id == TRAFFIC_LIGHT_CLASS:
            tl_boxes.append(coords)
    
    return vehicle_boxes, tl_boxes, results
