"""Train YOLO11 model on BJJ position dataset."""

import argparse
from pathlib import Path

from ultralytics import YOLO


def main() -> None:
    parser = argparse.ArgumentParser(description="Train BJJ position detector")
    parser.add_argument("--model", default="yolo11n.pt", help="Base model")
    parser.add_argument("--data", default="dataset/dataset.yaml", help="Dataset YAML")
    parser.add_argument("--epochs", type=int, default=50, help="Training epochs")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--name", default="bjj-detector", help="Run name")
    parser.add_argument("--workers", type=int, default=0, help="Dataloader workers")
    parser.add_argument("--device", default="0", help="Device (0 for GPU, cpu for CPU)")
    args = parser.parse_args()

    model = YOLO(args.model)
    model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        name=args.name,
        workers=args.workers,
        device=args.device,
    )

    best_pt = Path(f"runs/detect/{args.name}/weights/best.pt")
    if best_pt.exists():
        dest = Path("best.pt")
        best_pt.rename(dest)
        print(f"Best model saved to {dest}")


if __name__ == "__main__":
    main()
