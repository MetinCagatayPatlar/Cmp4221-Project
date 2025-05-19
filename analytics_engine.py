import cv2
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
model.to("cuda:0")
print(f"Using device: {model.device}")

# Setup font
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 0.7
font_color = (0, 255, 0)
thickness = 2


def process_frame(img):
    results = model.predict(img, device="cuda", verbose=False)[0]
    person_mask = results.boxes.cls == 0
    results.boxes = results.boxes[person_mask]
    return results.plot()q