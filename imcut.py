"""Image cutter

Usage:
    imcut.py [--output=PATH] [--height=H] [--cut=W] [--cut-count=N] <INPUT>
    imcut.py [--output=PATH] [--height=H] [--cut=W] [--cut-count=N] --pbcopy

Arguments:
    <INPUT>  Input image path

Options:
-o,--output=PATH    the output path [default: a.out.png]
-h,--height=H       the height cut [default: 0.5]
-c,--cut=M          the cut width [default: 0.02]
-f,--cut-count=N    cut count [default: 0.05]
-p,--pbcopy         take the input image from paste board
"""
import numpy as np
import cv2
import os
import sys
from docopt import docopt
from typing import Optional
from PIL import ImageGrab, Image
import random

DEFAULT_DIRNAME = os.path.join(os.environ["HOME"], "Downloads")


def get_pb_image() -> Optional[np.ndarray]:
    """Get an image from the clipboard and return as an OpenCV BGR numpy array."""
    img = ImageGrab.grabclipboard()
    if isinstance(img, Image.Image):
        img_np = np.array(img)
        return cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    return None


def get_image(args):
    img = None
    if args["<INPUT>"] and os.path.exists(args["<INPUT>"]):
        img = cv2.imread(args["<INPUT>"])
    elif args["--pbcopy"]:
        img = get_pb_image()
    if img is None:
        print("❌ No valid image (--pbcopy or <INPUT> required).", file=sys.stderr)
        sys.exit(1)
    return img


def get_heights(args, img) -> tuple[int, int]:
    """Parse --height argument (support one or two values)."""
    hs = [eval(s.strip()) for s in args["--height"].split(",")]
    if len(hs) == 1:
        hs = [hs[0], hs[0]]

    H = img.shape[0]
    h1, h2 = hs
    if isinstance(h1, float):
        h1 = int(h1 * H)
    if isinstance(h2, float):
        h2 = int(h2 * H)
    if h1 < 0:
        h1 += H
    if h2 < 0:
        h2 += H
    return min(h1, h2), max(h1, h2)


def get_cut_heights(args, img) -> tuple[list[tuple[int, int]], int]:
    """Generate random vertical cut offsets across the image width."""
    w = eval(args["--cut"])
    n = eval(args["--cut-count"])
    if isinstance(w, float):
        w = int(w * img.shape[0])
    if isinstance(n, float):
        n = int(n * img.shape[1])

    rc = [
        (random.randint(-w, w), int(ci))
        for _, ci in enumerate(np.linspace(0, img.shape[1] - 1, n + 1))
    ]
    return rc, abs(w)


def get_paths(args) -> tuple[str, str, str]:
    dirname = os.path.dirname(args["--output"])
    if not dirname:
        dirname = os.path.dirname(args["<INPUT>"] or "")
        if not dirname:
            dirname = DEFAULT_DIRNAME

    base = os.path.basename(args["--output"])
    filename, ext = os.path.splitext(base)
    return (
        os.path.join(dirname, f"{filename}-top{ext}"),
        os.path.join(dirname, f"{filename}-middle{ext}"),
        os.path.join(dirname, f"{filename}-bottom{ext}"),
    )


def draw_cut(mask, base_h, rc):
    """Draw a wavy cut contour into a binary mask (bottom side of mask = 0)."""
    H, W = mask.shape
    r00, c0 = base_h + rc[0][0], rc[0][1]
    for dri, ci in rc[1:]:
        ri0 = base_h + dri
        li0_fn = lambda x: (ri0 - r00) / (ci - c0) * (x - c0) + r00
        for x in range(c0, ci + 1):
            y = int(li0_fn(x))
            if 0 <= y < H:
                mask[y:, x] = 0
        r00, c0 = ri0, ci


def split_image_band(img, h1: int, h2: int, rc, w: int):
    """Split image into top/middle/bottom with cuts included."""
    H, W = img.shape[:2]
    I = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

    # masks for cuts
    mask_top = np.ones((H, W), dtype=np.uint8) * 255
    mask_bottom = np.ones((H, W), dtype=np.uint8) * 255

    draw_cut(mask_top, h1, rc)
    draw_cut(mask_bottom, h2, rc)

    # Use masks to separate
    top_part = cv2.bitwise_and(I, I, mask=mask_top)
    bottom_mask = cv2.bitwise_not(mask_bottom)
    bottom_part = cv2.bitwise_and(I, I, mask=bottom_mask)
    mid_mask = cv2.bitwise_not(mask_top) & mask_bottom
    mid_part = cv2.bitwise_and(I, I, mask=mid_mask)

    # Include the wavy band (±w) inside each cropped region
    y_top1 = 0
    y_top2 = min(H, h1 + w)
    y_mid1 = max(0, h1 - w)
    y_mid2 = min(H, h2 + w)
    y_bot1 = max(0, h2 - w)
    y_bot2 = H

    top_crop = top_part[y_top1:y_top2, :].copy()
    mid_crop = mid_part[y_mid1:y_mid2, :].copy()
    bot_crop = bottom_part[y_bot1:y_bot2, :].copy()

    return top_crop, mid_crop, bot_crop


def main():
    args = docopt(__doc__)
    img = get_image(args)
    h1, h2 = get_heights(args, img)
    rc, w = get_cut_heights(args, img)
    top_path, mid_path, bot_path = get_paths(args)

    img_top, img_mid, img_bot = split_image_band(img, h1, h2, rc, w)

    cv2.imwrite(top_path, img_top)
    cv2.imwrite(mid_path, img_mid)
    cv2.imwrite(bot_path, img_bot)

    print("✅ Output written to:")
    print(f"  Top:    {top_path}")
    print(f"  Middle: {mid_path}")
    print(f"  Bottom: {bot_path}")


if __name__ == "__main__":
    main()
