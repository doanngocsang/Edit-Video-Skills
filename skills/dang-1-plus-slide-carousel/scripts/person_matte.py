#!/usr/bin/env python3
"""Tach nguoi khoi nen (person matte) cho 1 doan video -> chuoi PNG trong suot.

Dung cho: carousel 3D (the chay sau lung nguoi) va chu sau lung nguoi.
Ghep: video goc -> lop SAU (the/chu) -> PNG nguoi nay -> lop TRUOC.

Vi du:
  python person_matte.py --video work/cut.mp4 --start 0.0 --duration 4 --out work/matte
Model MediaPipe tu tai lan dau vao assets/models/ (can mang).
"""
import argparse, shutil, subprocess, sys, urllib.request
from pathlib import Path

import cv2
import numpy as np

MODEL_URL = ("https://storage.googleapis.com/mediapipe-models/image_segmenter/"
             "selfie_multiclass_256x256/float32/latest/selfie_multiclass_256x256.tflite")


def ensure_model(path: Path):
    if path.exists() and path.stat().st_size > 100_000:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Tai model tach nguoi -> {path}")
    urllib.request.urlretrieve(MODEL_URL, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--start", type=float, required=True)
    ap.add_argument("--duration", type=float, required=True)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="assets/models/selfie_multiclass_256x256.tflite")
    ap.add_argument("--feather", type=int, default=5, help="lam mem mep (px)")
    ap.add_argument("--shrink", type=int, default=2, help="co mep vao (px) de bot vien nen")
    ap.add_argument("--smooth", type=float, default=0.55, help="lam muot theo thoi gian 0-1 (cao = muot hon)")
    a = ap.parse_args()

    import mediapipe as mp
    from mediapipe.tasks import python as mpt
    from mediapipe.tasks.python import vision

    model = Path(a.model)
    ensure_model(model)

    out = Path(a.out)
    if out.exists():
        shutil.rmtree(out)
    raw = out / "_raw"
    raw.mkdir(parents=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a.start), "-i", a.video,
                    "-t", str(a.duration), "-vf", f"fps={a.fps}", "-q:v", "2",
                    str(raw / "%04d.jpg")], check=True)
    frames = sorted(raw.glob("*.jpg"))
    if not frames:
        sys.exit("Khong trich duoc khung hinh.")

    opts = vision.ImageSegmenterOptions(
        base_options=mpt.BaseOptions(model_asset_path=str(model)),
        running_mode=vision.RunningMode.VIDEO,
        output_confidence_masks=True)
    seg = vision.ImageSegmenter.create_from_options(opts)

    prev = None
    k = np.ones((3, 3), np.uint8)
    for i, fp in enumerate(frames):
        bgr = cv2.imread(str(fp))
        h, w = bgr.shape[:2]
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        res = seg.segment_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb),
                                    int(i * 1000 / a.fps))
        masks = res.confidence_masks
        # multiclass: kenh 0 = nen -> nguoi = 1 - nen. Model 1 kenh: dung truc tiep.
        m = 1.0 - masks[0].numpy_view() if len(masks) > 1 else masks[0].numpy_view()
        m = cv2.resize(np.squeeze(m).astype(np.float32), (w, h), interpolation=cv2.INTER_LINEAR)
        if prev is not None:  # chong nhap nhay mep
            m = a.smooth * prev + (1 - a.smooth) * m
        prev = m
        m = np.clip((m - 0.35) / 0.3, 0, 1)  # smoothstep don gian quanh nguong 0.5
        if a.shrink > 0:
            m = cv2.erode(m, k, iterations=a.shrink)
        if a.feather > 0:
            m = cv2.GaussianBlur(m, (0, 0), a.feather / 2)
        rgba = np.dstack([bgr, (m * 255).astype(np.uint8)])
        cv2.imwrite(str(out / f"{i+1:04d}.png"), rgba)
    seg.close()
    shutil.rmtree(raw)
    print(f"OK {len(frames)} khung -> {out}")


if __name__ == "__main__":
    main()
