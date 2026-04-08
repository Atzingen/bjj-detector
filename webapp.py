"""BJJ Position Detector — Flask web application."""

import io
import os
import tempfile
from functools import wraps
from pathlib import Path

import cv2
import numpy as np
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify, send_file,
)
from PIL import Image
from ultralytics import YOLO
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "bjj-detector-dev-key-change-me")

MODEL_PATH = os.environ.get("MODEL_PATH", "best.pt")

USERS = {
    "admin": "admin",
    "demo": "demo1234",
}

CLASS_LABELS_PT = {
    "standing": "Em Pe",
    "takedown": "Queda",
    "open_guard": "Guarda Aberta",
    "half_guard": "Meia Guarda",
    "closed_guard": "Guarda Fechada",
    "fifty_fifty": "50-50",
    "side_control": "Cem Quilos",
    "mount": "Montada",
    "back": "Pegada nas Costas",
    "turtle": "Tartaruga",
}

POSITIONS_INFO = [
    {"id": 0, "name": "standing", "label": "Em Pe", "desc": "Ambos atletas de pe, antes do engajamento"},
    {"id": 1, "name": "takedown", "label": "Queda", "desc": "Transicao de pe para o chao"},
    {"id": 2, "name": "open_guard", "label": "Guarda Aberta", "desc": "Guardeiro com pernas abertas controlando"},
    {"id": 3, "name": "half_guard", "label": "Meia Guarda", "desc": "Uma perna do passador presa entre as pernas"},
    {"id": 4, "name": "closed_guard", "label": "Guarda Fechada", "desc": "Pernas cruzadas nas costas do oponente"},
    {"id": 5, "name": "fifty_fifty", "label": "50-50", "desc": "Ambos com controle simetrico de perna"},
    {"id": 6, "name": "side_control", "label": "Cem Quilos", "desc": "Controle lateral, peito a peito"},
    {"id": 7, "name": "mount", "label": "Montada", "desc": "Sentado sobre o torso do oponente"},
    {"id": 8, "name": "back", "label": "Pegada nas Costas", "desc": "Controle pelas costas com ganchos"},
    {"id": 9, "name": "turtle", "label": "Tartaruga", "desc": "Posicao defensiva de quatro apoios"},
]

if Path(MODEL_PATH).exists():
    model = YOLO(MODEL_PATH)
else:
    model = None
    print(f"WARNING: Model not found at {MODEL_PATH}")


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def run_detection(pil_image: Image.Image) -> tuple[np.ndarray, list[dict]]:
    """Run YOLO detection on a PIL image. Returns (annotated_bgr, detections)."""
    if model is None:
        img_array = np.array(pil_image)
        return cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR), []

    results = model(pil_image)
    annotated = results[0].plot()
    detections = []
    for box in results[0].boxes:
        cls_name = model.names[int(box.cls)]
        cls_label = CLASS_LABELS_PT.get(cls_name, cls_name)
        conf = float(box.conf)
        xyxy = box.xyxy[0].tolist()
        detections.append({
            "class": cls_name,
            "label": cls_label,
            "confidence": round(conf * 100, 1),
            "bbox": [round(v) for v in xyxy],
        })
    return annotated, detections


@app.route("/")
def landing():
    return render_template("landing.html", positions=POSITIONS_INFO)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username in USERS and USERS[username] == password:
            session["user"] = username
            return redirect(url_for("detect"))
        flash("Usuario ou senha incorretos")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("landing"))


@app.route("/detect")
@login_required
def detect():
    return render_template("detect.html")


@app.route("/api/detect", methods=["POST"])
@login_required
def api_detect():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400

    file = request.files["image"]
    pil_image = Image.open(file.stream).convert("RGB")

    annotated_bgr, detections = run_detection(pil_image)

    _, buffer = cv2.imencode(".jpg", annotated_bgr, [cv2.IMWRITE_JPEG_QUALITY, 90])
    import base64
    img_b64 = base64.b64encode(buffer).decode("utf-8")

    return jsonify({
        "image": f"data:image/jpeg;base64,{img_b64}",
        "detections": detections,
    })


@app.route("/api/detect-video", methods=["POST"])
@login_required
def api_detect_video():
    if "video" not in request.files:
        return jsonify({"error": "No video provided"}), 400

    file = request.files["video"]
    skip_frames = int(request.form.get("skip_frames", 3))

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    try:
        cap = cv2.VideoCapture(tmp_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        out_path = tmp_path.replace(".mp4", "_out.mp4")
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(out_path, fourcc, fps, (width, height))

        frame_idx = 0
        all_detections = []
        last_annotated = None

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % (skip_frames + 1) == 0:
                pil_frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                annotated_bgr, detections = run_detection(pil_frame)
                last_annotated = annotated_bgr
                if detections:
                    all_detections.append({
                        "frame": frame_idx,
                        "time": round(frame_idx / fps, 2),
                        "detections": detections,
                    })
            else:
                annotated_bgr = last_annotated if last_annotated is not None else frame

            out.write(annotated_bgr)
            frame_idx += 1

        cap.release()
        out.release()

        with open(out_path, "rb") as f:
            import base64
            video_b64 = base64.b64encode(f.read()).decode("utf-8")

        os.unlink(out_path)

        return jsonify({
            "video": f"data:video/mp4;base64,{video_b64}",
            "total_frames": total_frames,
            "processed_frames": frame_idx,
            "detections": all_detections,
        })
    finally:
        os.unlink(tmp_path)


if __name__ == "__main__":
    app.run(
        host=os.environ.get("FLASK_HOST", "0.0.0.0"),
        port=int(os.environ.get("FLASK_PORT", "5000")),
        debug=os.environ.get("FLASK_DEBUG", "true").lower() == "true",
    )
