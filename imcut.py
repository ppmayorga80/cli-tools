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

DEFAULT_DIRNAME = os.path.join(os.environ['HOME'], "Downloads")


def get_pb_image() -> Optional[np.ndarray]:
    """Get an image from the clipboard and return as an OpenCV BGR numpy array."""
    img = ImageGrab.grabclipboard()

    if isinstance(img, Image.Image):  # check if it's a valid PIL image
        # Convert to numpy array
        img_np = np.array(img)

        # Convert RGB -> BGR (since OpenCV uses BGR)
        img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        return img_cv
    return None


def get_image(args):
    img = None
    if args['<INPUT>'] is not None:
        try:
            img = cv2.imread(args["<INPUT>"])
        except Exception as e:
            print(f"'{args['<INPUT>']}' is not a valid image.'", sys.stderr)
            print(f"{e}", sys.stderr)
            exit(1)
    elif args['--pbcopy']:
        img = get_pb_image()
    if img is None:
        print(f"--pbcopy is not a valid image.'", sys.stderr)
        exit(1)
    return img


def get_heights(args, img) -> tuple[int, int]:
    hs = [eval(s.strip()) for s in args['--height'].split(',')]
    for i in range(len(hs)):
        if isinstance(hs[i], float):
            hs[i] = int(hs[i] * img.shape[0])
        if hs[i] < 0:
            hs[i] += img.shape[0]
    return hs


def get_cut_heights(args, img) -> list[tuple[int, int]]:
    w = eval(args['--cut'])
    n = eval(args['--cut-count'])
    if isinstance(w, float):
        w = int(w * img.shape[0])
    if isinstance(n, float):
        n = int(n * img.shape[1])

    rc = [
        (random.randint(-w, w), int(ci))
        for _, ci in enumerate(np.linspace(0, img.shape[1] - 1, n + 1))
    ]
    return rc


def get_paths(args, n) -> tuple:
    dirname = os.path.dirname(args['--output'])
    if not dirname:
        dirname = os.path.dirname(args['<INPUT>'] or "")
        if not dirname:
            dirname = DEFAULT_DIRNAME

    base = os.path.basename(args['--output'])
    filename, ext = os.path.splitext(base)

    p = tuple([
        os.path.join(dirname, f"{filename}-{k}{ext}")
        for k in range(n)
    ])
    return p


def split_image(img, h, rc):
    mp = max([r for r, c in rc])
    mn = -min([r for r, c in rc])

    if len(img.shape) == 1:
        I = cv2.cvtColor(img, cv2.COLOR_GRAY2BGRA)
    elif len(img.shape) == 3:
        I = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    elif len(img.shape) == 4:
        I = img
    else:
        I = img

    img_top = I[0:h + mn, :].copy()
    img_bottom = I[h + 1 - mp:, :].copy()

    r00, c0 = h + rc[0][0], rc[0][1]
    for dri, ci in rc[1:]:
        ri0 = h + dri
        li0_fn = lambda x: (ri0 - r00) / (ci - c0) * (x - c0) + r00
        for x in range(c0, ci + 1):
            y0 = int(li0_fn(x))
            y1 = y0 - h + mn
            img_top[y0:, x] = 0
            img_bottom[:y1, x] = 0
        r00, c0 = ri0, ci

    return img_top, img_bottom


def main():
    args = docopt(__doc__)

    img = get_image(args)

    heights = get_heights(args, img)
    nhs = len(heights)
    paths = get_paths(args, nhs + 1)
    rc = get_cut_heights(args, img)

    images = []
    imk = img
    h_cum = 0
    for hi in heights:
        i1, i2 = split_image(imk, hi - h_cum, rc)
        h_cum += hi
        images.append(i1)
        imk = i2
    images.append(i2)

    print("Output written to:")
    for img, path in zip(images, paths):
        cv2.imwrite(path, img)
        print(f"    {path}")


if __name__ == '__main__':
    main()
