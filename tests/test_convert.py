"""Tests for dataset conversion logic."""

from scripts.convert_dataset import keypoints_to_bbox, map_position_to_class


def test_keypoints_to_bbox_basic():
    """Two athletes with known keypoints should produce correct bbox."""
    pose1 = [[100, 80, 0.9]] + [[90, 120, 0.8]] + [[0, 0, 0]] * 15
    pose2 = [[200, 130, 0.9]] + [[210, 170, 0.8]] + [[0, 0, 0]] * 15
    img_w, img_h = 640, 480

    bbox = keypoints_to_bbox(pose1, pose2, img_w, img_h, padding=0.1)

    x_c, y_c, w, h = bbox
    assert 0.22 < x_c < 0.25
    assert 0.25 < y_c < 0.27
    assert 0.20 < w < 0.25
    assert 0.20 < h < 0.25


def test_keypoints_to_bbox_clamps_to_image():
    """Bbox should not exceed image boundaries."""
    pose1 = [[5, 5, 0.9]] + [[0, 0, 0]] * 16
    pose2 = [[635, 475, 0.9]] + [[0, 0, 0]] * 16
    img_w, img_h = 640, 480

    bbox = keypoints_to_bbox(pose1, pose2, img_w, img_h, padding=0.1)
    x_c, y_c, w, h = bbox

    assert x_c - w / 2 >= 0
    assert y_c - h / 2 >= 0
    assert x_c + w / 2 <= 1.0
    assert y_c + h / 2 <= 1.0


def test_keypoints_to_bbox_skips_zero_confidence():
    """Keypoints with confidence=0 should be ignored."""
    pose1 = [[100, 100, 0.9], [999, 999, 0.0]] + [[0, 0, 0]] * 15
    pose2 = [[200, 200, 0.8]] + [[0, 0, 0]] * 16
    img_w, img_h = 640, 480

    bbox = keypoints_to_bbox(pose1, pose2, img_w, img_h, padding=0.0)
    x_c, y_c, w, h = bbox

    assert abs(x_c - 150 / 640) < 0.01
    assert abs(y_c - 150 / 480) < 0.01


def test_map_position_standing():
    assert map_position_to_class("standing") == 0


def test_map_position_removes_suffix():
    """mount1 and mount2 should both map to 'mount' (class 7)."""
    assert map_position_to_class("mount1") == 7
    assert map_position_to_class("mount2") == 7


def test_map_position_all_classes():
    expected = {
        "standing": 0, "takedown1": 1, "takedown2": 1,
        "open_guard1": 2, "open_guard2": 2,
        "half_guard1": 3, "half_guard2": 3,
        "closed_guard1": 4, "closed_guard2": 4,
        "50-501": 5, "50-502": 5,
        "side_control1": 6, "side_control2": 6,
        "mount1": 7, "mount2": 7,
        "back1": 8, "back2": 8,
        "turtle1": 9, "turtle2": 9,
    }
    for pos, cls_id in expected.items():
        assert map_position_to_class(pos) == cls_id, f"Failed for {pos}"
