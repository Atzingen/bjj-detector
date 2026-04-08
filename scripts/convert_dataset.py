"""Convert ViCoS BJJ annotations (COCO keypoints) to YOLO detection format."""

import json
import random
import shutil
from pathlib import Path
from typing import Any

POSITION_MAP: dict[str, int] = {
    "standing": 0,
    "takedown": 1,
    "open_guard": 2,
    "half_guard": 3,
    "closed_guard": 4,
    "5050_guard": 5,
    "side_control": 6,
    "mount": 7,
    "back": 8,
    "turtle": 9,
}

CLASS_NAMES: list[str] = [
    "standing", "takedown", "open_guard", "half_guard", "closed_guard",
    "fifty_fifty", "side_control", "mount", "back", "turtle",
]


def map_position_to_class(position: str) -> int:
    """Map a position code like 'mount2' to its base class ID (7).

    Strips trailing '1' or '2' suffix that indicates athlete perspective.
    Special case: 'standing' has no suffix, '50-501'/'50-502' strip last char.
    """
    if position in POSITION_MAP:
        return POSITION_MAP[position]

    base = position[:-1]
    if base in POSITION_MAP:
        return POSITION_MAP[base]

    raise ValueError(f"Unknown position: {position}")


def keypoints_to_bbox(
    pose1: list[list[float]],
    pose2: list[list[float]],
    img_w: int,
    img_h: int,
    padding: float = 0.1,
) -> tuple[float, float, float, float]:
    """Compute YOLO-format bbox from two athletes' keypoints.

    Args:
        pose1: 17 keypoints [[x, y, confidence], ...] for athlete 1
        pose2: 17 keypoints [[x, y, confidence], ...] for athlete 2
        img_w: image width in pixels
        img_h: image height in pixels
        padding: fraction of bbox size to add as padding

    Returns:
        (x_center, y_center, width, height) normalized to [0, 1]
    """
    xs: list[float] = []
    ys: list[float] = []

    for kp in pose1 + pose2:
        x, y, conf = kp[0], kp[1], kp[2]
        if conf > 0:
            xs.append(x)
            ys.append(y)

    if not xs or not ys:
        raise ValueError("No valid keypoints found")

    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)

    w = x_max - x_min
    h = y_max - y_min
    pad_w = w * padding
    pad_h = h * padding

    x_min = max(0, x_min - pad_w)
    y_min = max(0, y_min - pad_h)
    x_max = min(img_w, x_max + pad_w)
    y_max = min(img_h, y_max + pad_h)

    x_center = ((x_min + x_max) / 2) / img_w
    y_center = ((y_min + y_max) / 2) / img_h
    width = (x_max - x_min) / img_w
    height = (y_max - y_min) / img_h

    return x_center, y_center, width, height


def convert_dataset(
    annotations_path: Path,
    images_dir: Path,
    output_dir: Path,
    val_ratio: float = 0.2,
    seed: int = 42,
) -> None:
    """Convert full ViCoS dataset to YOLO detection format."""
    print(f"Loading annotations from {annotations_path} ...")
    with open(annotations_path) as f:
        annotations: list[dict[str, Any]] = json.load(f)

    print(f"Loaded {len(annotations)} annotations")

    for split in ("train", "val"):
        (output_dir / split / "images").mkdir(parents=True, exist_ok=True)
        (output_dir / split / "labels").mkdir(parents=True, exist_ok=True)

    random.seed(seed)
    random.shuffle(annotations)
    split_idx = int(len(annotations) * (1 - val_ratio))
    splits = {
        "train": annotations[:split_idx],
        "val": annotations[split_idx:],
    }

    from PIL import Image as PILImage

    stats = {"total": 0, "skipped": 0}

    for split_name, split_annotations in splits.items():
        for ann in split_annotations:
            img_name = ann["image"]
            position = ann["position"]
            pose1 = ann.get("pose1", [])
            pose2 = ann.get("pose2", [])

            img_path = None
            for ext in ("", ".jpg", ".png", ".jpeg"):
                candidate = images_dir / f"{img_name}{ext}"
                if candidate.exists():
                    img_path = candidate
                    break

            if img_path is None:
                matches = list(images_dir.rglob(f"{img_name}*"))
                if matches:
                    img_path = matches[0]

            if img_path is None:
                stats["skipped"] += 1
                continue

            try:
                class_id = map_position_to_class(position)
            except ValueError:
                stats["skipped"] += 1
                continue

            with PILImage.open(img_path) as img:
                img_w, img_h = img.size

            try:
                x_c, y_c, w, h = keypoints_to_bbox(pose1, pose2, img_w, img_h)
            except ValueError:
                stats["skipped"] += 1
                continue

            dest_img = output_dir / split_name / "images" / img_path.name
            if not dest_img.exists():
                shutil.copy2(img_path, dest_img)

            label_name = img_path.stem + ".txt"
            label_path = output_dir / split_name / "labels" / label_name
            with open(label_path, "w") as lf:
                lf.write(f"{class_id} {x_c:.6f} {y_c:.6f} {w:.6f} {h:.6f}\n")

            stats["total"] += 1

    print(f"Converted {stats['total']} images, skipped {stats['skipped']}")

    yaml_path = output_dir / "dataset.yaml"
    yaml_content = f"""path: .
train: train/images
val: val/images

nc: 10
names:
  0: standing
  1: takedown
  2: open_guard
  3: half_guard
  4: closed_guard
  5: fifty_fifty
  6: side_control
  7: mount
  8: back
  9: turtle
"""
    yaml_path.write_text(yaml_content)
    print(f"Dataset YAML written to {yaml_path}")


def main() -> None:
    project_root = Path(__file__).parent.parent
    convert_dataset(
        annotations_path=project_root / "data" / "annotations.json",
        images_dir=project_root / "data" / "images",
        output_dir=project_root / "dataset",
    )


if __name__ == "__main__":
    main()
