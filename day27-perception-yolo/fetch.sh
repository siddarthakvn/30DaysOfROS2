#!/usr/bin/env bash
# Weights and the street photo stay out of git. The smoke test downloads them.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODEL="$ROOT/assets/models/yolov8n.onnx"
FRAME="$ROOT/assets/frames/street.jpg"
mkdir -p "$ROOT/assets/models" "$ROOT/assets/frames" "$ROOT/assets/annotated"

if [[ ! -s "$MODEL" ]]; then
  curl -fL --retry 3 --connect-timeout 20 --max-time 180 \
    -o "$MODEL" \
    "https://github.com/ultralytics/assets/releases/download/v8.4.0/yolov8n.onnx"
fi
if [[ ! -s "$FRAME" ]]; then
  curl -fL --retry 3 --connect-timeout 20 --max-time 60 \
    -o "$FRAME" \
    "https://ultralytics.com/images/bus.jpg"
fi
test -s "$MODEL"
test -s "$FRAME"
echo "model=$MODEL"
echo "frame=$FRAME"
