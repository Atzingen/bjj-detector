"""Tests for the Gradio app inference function."""

from unittest.mock import MagicMock, patch
from PIL import Image

from app import detect, CLASS_NAMES


def test_detect_returns_annotated_image_and_table():
    """detect() should return (PIL.Image, list of [class, confidence])."""
    dummy_img = Image.new("RGB", (640, 480), color="red")

    mock_box = MagicMock()
    mock_box.cls = MagicMock()
    mock_box.cls.__int__ = lambda self: 7  # mount
    mock_box.conf = MagicMock()
    mock_box.conf.__float__ = lambda self: 0.92

    mock_result = MagicMock()
    mock_result.plot.return_value = dummy_img
    mock_result.boxes = [mock_box]

    with patch("app.model") as mock_model:
        mock_model.return_value = [mock_result]
        mock_model.names = CLASS_NAMES

        annotated, detections = detect(dummy_img)

    assert annotated is not None
    assert len(detections) == 1
    assert detections[0][0] == "Montada"


def test_detect_no_detections():
    """detect() with no boxes should return empty table."""
    dummy_img = Image.new("RGB", (640, 480), color="red")

    mock_result = MagicMock()
    mock_result.plot.return_value = dummy_img
    mock_result.boxes = []

    with patch("app.model") as mock_model:
        mock_model.return_value = [mock_result]
        mock_model.names = CLASS_NAMES

        annotated, detections = detect(dummy_img)

    assert annotated is not None
    assert len(detections) == 1
    assert detections[0][0] == "Nenhuma posicao detectada"
