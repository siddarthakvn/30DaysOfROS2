"""YOLOv8n through OpenCV DNN. No torch, no ultralytics package."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "assets" / "models" / "yolov8n.onnx"
FRAME = ROOT / "assets" / "frames" / "street.jpg"
INPUT = 640
CONF = 0.25
IOU = 0.45
SEEN_SCORE = 0.50

COCO = (
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat",
    "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
    "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack",
    "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball",
    "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket",
    "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple",
    "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair",
    "couch", "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse",
    "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
    "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier",
    "toothbrush",
)


def load_net(path: Path | None = None) -> cv2.dnn.Net:
    model = path or MODEL
    if not model.is_file() or model.stat().st_size == 0:
        raise FileNotFoundError(f"missing YOLOv8n weights: {model}")
    return cv2.dnn.readNetFromONNX(str(model))


def letterbox(image: np.ndarray, size: int = INPUT):
    height, width = image.shape[:2]
    scale = min(size / height, size / width)
    resized_w = int(round(width * scale))
    resized_h = int(round(height * scale))
    resized = cv2.resize(image, (resized_w, resized_h), interpolation=cv2.INTER_LINEAR)
    canvas = np.full((size, size, 3), 114, np.uint8)
    pad_x = (size - resized_w) // 2
    pad_y = (size - resized_h) // 2
    canvas[pad_y:pad_y + resized_h, pad_x:pad_x + resized_w] = resized
    return canvas, scale, pad_x, pad_y


def detect(image: np.ndarray, net: cv2.dnn.Net, conf: float = CONF, iou: float = IOU) -> list[dict]:
    """Return boxes in the original image, highest score first."""
    canvas, scale, pad_x, pad_y = letterbox(image)
    blob = cv2.dnn.blobFromImage(canvas, 1 / 255.0, (INPUT, INPUT), swapRB=True, crop=False)
    net.setInput(blob)
    pred = net.forward()[0].T
    boxes = pred[:, :4]
    classes = pred[:, 4:]
    class_ids = classes.argmax(axis=1)
    scores = classes.max(axis=1)
    keep = scores >= conf
    boxes, class_ids, scores = boxes[keep], class_ids[keep], scores[keep]
    if len(scores) == 0:
        return []

    xywh = []
    for cx, cy, bw, bh in boxes:
        xywh.append([
            float((cx - bw / 2 - pad_x) / scale),
            float((cy - bh / 2 - pad_y) / scale),
            float(bw / scale),
            float(bh / scale),
        ])
    kept = cv2.dnn.NMSBoxes(xywh, scores.tolist(), conf, iou)
    if kept is None or len(kept) == 0:
        return []
    found = []
    for index in np.array(kept).reshape(-1):
        x, y, w, h = xywh[int(index)]
        name = COCO[int(class_ids[int(index)])]
        found.append({
            "name": name,
            "score": float(scores[int(index)]),
            "cx": x + w / 2.0,
            "cy": y + h / 2.0,
            "sx": w,
            "sy": h,
        })
    found.sort(key=lambda row: row["score"], reverse=True)
    return found


def blank_frame() -> np.ndarray:
    return np.full((480, 640, 3), 114, np.uint8)


def street_frame() -> np.ndarray:
    image = cv2.imread(str(FRAME))
    if image is None:
        raise FileNotFoundError(f"missing street frame: {FRAME}")
    return image


def load_scene(scene: str) -> np.ndarray:
    if scene == "blank":
        return blank_frame()
    if scene == "street":
        return street_frame()
    raise ValueError(f"unknown scene: {scene}")


def best_person(rows: list[dict]) -> dict | None:
    people = [row for row in rows if row["name"] == "person"]
    if not people:
        return None
    return max(people, key=lambda row: row["score"])
