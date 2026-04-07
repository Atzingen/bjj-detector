"""BJJ Position Detector — Gradio interface styled like Quickium."""

import os
from pathlib import Path

import gradio as gr
from PIL import Image
from ultralytics import YOLO

MODEL_PATH = os.environ.get("MODEL_PATH", "best.pt")

CLASS_NAMES = {
    0: "standing", 1: "takedown", 2: "open_guard", 3: "half_guard",
    4: "closed_guard", 5: "fifty_fifty", 6: "side_control", 7: "mount",
    8: "back", 9: "turtle",
}

CLASS_LABELS_PT = {
    "standing": "Em pe", "takedown": "Queda", "open_guard": "Guarda aberta",
    "half_guard": "Meia guarda", "closed_guard": "Guarda fechada",
    "fifty_fifty": "50-50", "side_control": "Cem quilos", "mount": "Montada",
    "back": "Pegada nas costas", "turtle": "Tartaruga",
}

# Load model at startup
if Path(MODEL_PATH).exists():
    model = YOLO(MODEL_PATH)
else:
    model = None
    print(f"WARNING: Model not found at {MODEL_PATH}. Run train.py first.")


def detect(image: Image.Image) -> tuple:
    """Run YOLO detection and return annotated image + detections table."""
    if model is None:
        return image, [["Modelo nao encontrado", "-"]]

    results = model(image)
    annotated = results[0].plot()
    detections = []
    for box in results[0].boxes:
        cls_name = model.names[int(box.cls)]
        cls_label = CLASS_LABELS_PT.get(cls_name, cls_name)
        conf = float(box.conf)
        detections.append([cls_label, f"{conf:.1%}"])

    if not detections:
        detections = [["Nenhuma posicao detectada", "-"]]

    return annotated, detections


CUSTOM_CSS = """
/* Quickium-inspired dark theme */
.gradio-container {
    background: #0a0f1a !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}

/* Header */
.header-title {
    color: #f8fafc;
    font-size: 2rem;
    font-weight: 700;
    text-align: center;
    margin-bottom: 0.25rem;
}
.header-subtitle {
    color: #76A9FA;
    font-size: 1.1rem;
    text-align: center;
    margin-bottom: 1.5rem;
}

/* Cards / blocks */
.gr-panel, .gr-box, .gr-form, .gr-input, .gr-padded {
    background: #111827 !important;
    border: 1px solid #1e293b !important;
    border-radius: 12px !important;
    color: #f8fafc !important;
}

/* Image upload area */
.gr-image, .gr-file-upload {
    background: #111827 !important;
    border: 2px dashed #2B5B9C !important;
    border-radius: 12px !important;
}

/* Buttons */
.gr-button-primary {
    background: #2B5B9C !important;
    border: none !important;
    border-radius: 8px !important;
    color: white !important;
    font-weight: 600 !important;
}
.gr-button-primary:hover {
    background: #3b6db5 !important;
}

/* Dataframe */
.gr-dataframe {
    background: #111827 !important;
    color: #f8fafc !important;
}

/* Labels */
label, .gr-label {
    color: #94a3b8 !important;
}

/* Footer */
footer {
    display: none !important;
}
"""


def build_app() -> gr.Blocks:
    with gr.Blocks(css=CUSTOM_CSS, title="BJJ Position Detector") as app:
        gr.HTML('<div class="header-title">BJJ Position Detector</div>')
        gr.HTML('<div class="header-subtitle">Detecte posicoes de jiu-jitsu com Inteligencia Artificial</div>')

        with gr.Row():
            with gr.Column():
                input_image = gr.Image(
                    type="pil",
                    label="Upload de Imagem",
                    height=400,
                )
            with gr.Column():
                output_image = gr.Image(
                    label="Resultado",
                    height=400,
                )

        detections_table = gr.Dataframe(
            headers=["Posicao", "Confianca"],
            label="Deteccoes",
            interactive=False,
        )

        input_image.change(
            fn=detect,
            inputs=input_image,
            outputs=[output_image, detections_table],
        )

        examples_dir = Path("examples")
        if examples_dir.exists():
            example_images = sorted(examples_dir.glob("*.jpg"))[:5]
            if example_images:
                gr.Examples(
                    examples=[[str(p)] for p in example_images],
                    inputs=input_image,
                )

    return app


if __name__ == "__main__":
    app = build_app()
    app.launch(
        server_name=os.environ.get("GRADIO_SERVER_NAME", "0.0.0.0"),
        server_port=int(os.environ.get("GRADIO_SERVER_PORT", "7860")),
    )
