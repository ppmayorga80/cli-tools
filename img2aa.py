"""Convert an image into ascii art (aa)

Usage:
    img2aa [--charset=CHARSET] [--colors=N] [--pixel-size=SIZE] <IMAGE>

Arguments:
    <IMAGE>         input image name in any format

Options:
    -c CHARSET, --charset=CHARSET   set a charset from 0 to 1 [default: .#]
    -n N, --colors=N                set the number of colors to map the <IMAGE> [default: 2]
    -p N, --pixel-size=N            se pixel size [default: 1]

Examples:
    img2aa -p 30 /local/path/to/image
    img2aa -p 30 gs://bucket/path/to/image
    img2aa -p 30 http://url/point/to/image
    img2aa -p 50 -n 4 -c ".o*#" https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Google_2015_logo.svg/2560px-Google_2015_logo.svg.png

"""
from typing import Type

import docopt
import sys
import smart_open
from PIL import Image


def str2num(text: str, default=None, class_type: Type = int):
    val = default
    try:
        val = class_type(eval(text))
    except TypeError:
        pass
    except NameError:
        pass
    return val


def main():
    # read arguments and validate
    args = docopt.docopt(__doc__)
    n_colors = str2num(args["--colors"], default=None, class_type=int)
    charset = args["--charset"]
    pixel_size = str2num(args["--pixel-size"], default=None, class_type=int)
    filename = args["<IMAGE>"]

    # in case of an error, exit
    if n_colors != len(charset):
        raise ValueError("given --colors=N and --charset=CHARSET, len(CHARSET)==N")
    if pixel_size < 1:
        raise ValueError("pixel size must be an integer greater than zero")

    # read the image in gray scale. the "L" is for Luminance or grayscale
    with smart_open.open(filename, "rb") as fp:
        img = Image.open(fp).convert("L")
    image_width, image_height = img.size

    # resize the image based on pixel size
    img = img.resize((image_width // pixel_size, image_height // pixel_size), resample=Image.NEAREST)
    w, h = img.size

    # print each pixel as ascii-art
    print(f"#Size: {w}x{h}", file=sys.stderr)
    for i in range(h):
        for j in range(w):
            # get pixel value between [0,255]
            v = img.getpixel((j, i))
            # map this value to [0,1] and then to [0, n_colors - 1]
            k = round(v / 255.0 * (n_colors - 1))
            # get the output character
            c = charset[k]
            # print without end line
            print(c, end="", file=sys.stdout)
        # at the end of every row, print a new line character
        print("", file=sys.stdout)


if __name__ == '__main__':
    main()
