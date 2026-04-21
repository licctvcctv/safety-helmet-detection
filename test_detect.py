"""Smoke test: run available YOLO models on sample images and save results."""
from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np
import torch

from models.experimental import attempt_load
from utils.general import check_img_size, non_max_suppression, scale_coords
from utils.plots import plot_one_box
from utils.torch_utils import select_device


PROJECT_ROOT = Path(__file__).resolve().parent
MODEL_DIR = PROJECT_ROOT / "ptmodel"
TEST_IMAGE_DIR = PROJECT_ROOT / "datasets" / "test_images"
OUTPUT_DIR = PROJECT_ROOT / "test_results"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def letterbox(img, new_shape=640, color=(114, 114, 114)):
    shape = img.shape[:2]
    r = min(new_shape / shape[0], new_shape / shape[1])
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw = new_shape - new_unpad[0]
    dh = new_shape - new_unpad[1]
    dw, dh = dw / 2, dh / 2
    img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)
    return img


def parse_args():
    parser = argparse.ArgumentParser(description="对仓库中的模型做快速推理验证")
    parser.add_argument("--weights", nargs="*", help="指定一个或多个 .pt 模型路径")
    parser.add_argument("--images", nargs="*", help="指定测试图片路径")
    parser.add_argument("--imgsz", type=int, default=640, help="推理尺寸")
    parser.add_argument("--conf-thres", type=float, default=0.25, help="置信度阈值")
    parser.add_argument("--iou-thres", type=float, default=0.45, help="IoU 阈值")
    parser.add_argument("--device", default="", help="推理设备，例如 cpu 或 0")
    return parser.parse_args()


def resolve_models(args):
    if args.weights:
        return [Path(weight).resolve() for weight in args.weights]
    return sorted(MODEL_DIR.glob("*.pt"))


def resolve_images(args):
    if args.images:
        return [Path(image).resolve() for image in args.images]
    return sorted(
        path for path in TEST_IMAGE_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def load_model(weights, device, imgsz):
    model = attempt_load(str(weights), map_location=device)
    stride = int(model.stride.max())
    imgsz = check_img_size(imgsz, s=stride)
    names = model.module.names if hasattr(model, 'module') else model.names
    colors = [[np.random.randint(0, 255) for _ in range(3)] for _ in names]
    return model, imgsz, names, colors


def run_model(weights, images, args):
    device = select_device(args.device)
    model, imgsz, names, colors = load_model(weights, device, args.imgsz)
    output_dir = OUTPUT_DIR / weights.stem
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Model loaded: {weights}")
    print(f"Classes: {names}")
    print(f"Device: {device}")
    print("-" * 50)

    total_detected = 0
    processed = 0
    for img_path in images:
        if not img_path.exists():
            print(f"SKIP: {img_path} not found")
            continue

        im0 = cv2.imread(str(img_path))
        if im0 is None:
            print(f"SKIP: failed to read {img_path}")
            continue

        processed += 1
        img = letterbox(im0, imgsz)
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR->RGB, HWC->CHW
        img = np.ascontiguousarray(img)
        img = torch.from_numpy(img).to(device).float() / 255.0
        img = img.unsqueeze(0)

        with torch.no_grad():
            pred = model(img)[0]
        pred = non_max_suppression(pred, args.conf_thres, args.iou_thres)

        det = pred[0]
        basename = img_path.name
        if len(det):
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()
            for *xyxy, conf, cls in reversed(det):
                c = int(cls)
                label = f'{names[c]} {conf:.2f}'
                plot_one_box(xyxy, im0, label=label, color=colors[c], line_thickness=3)

            total_detected += len(det)
            print(f"{basename}: detected {len(det)} objects")
            for *xyxy, conf, cls in det:
                print(f"  - {names[int(cls)]}: {conf:.2f}")
        else:
            print(f"{basename}: no detection")

        save_path = output_dir / basename
        cv2.imwrite(str(save_path), im0)
        print(f"  Saved: {save_path}")
        print()

    print(f"Summary: processed={processed}, total_detected={total_detected}, output={output_dir}")
    print()
    return processed > 0


def main():
    args = parse_args()
    models = resolve_models(args)
    images = resolve_images(args)

    if not models:
        raise SystemExit("未找到可用模型，请检查 ptmodel/ 目录")
    if not images:
        raise SystemExit("未找到测试图片，请检查 datasets/test_images/ 目录")

    all_ok = True
    for weights in models:
        all_ok = run_model(weights, images, args) and all_ok

    raise SystemExit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
