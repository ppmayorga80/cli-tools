"""
Usage:
	pyqr.py [--open]
	pyqr.py [--open] <PATH>...

Arguments:
    <FILE>      the qr image to be processed

Options:
    -o,--open      if set, will open the default browser in case the qr is a valid url
"""
import os
import re

from dataclasses import dataclass
from typing import Optional
import pyperclip

import cv2
import fitz
import numpy as np
from docopt import docopt

from PIL import Image, ImageTk
import tkinter
import tkinter.scrolledtext
from tkinterdnd2 import DND_FILES, TkinterDnD


@dataclass
class QRData:
    original_image: Optional[np.ndarray] = None
    detected_image: Optional[np.ndarray] = None
    path: Optional[str] = None
    message: Optional[str] = None


class PyQR:

    def __init__(self, input_path: str):
        self.input_path = input_path
        self.input_data_preprocessed: list[QRData] = []
        self.input_data_processed: list[QRData] = []

    def open_browsers(self):
        for x in self.input_data_processed:
            if re.findall(r"https?://.+", x.message):
                os.system(f"open \"{x.message}\"")

    def get_content(self):
        content = "\n".join([x.message for x in self.input_data_processed])
        return content

    def copy_to_clipboard(self):
        pyperclip.copy(self.get_content())

    def run(self) -> list[QRData]:
        # 1. preprocess images if needed
        if self.input_path.endswith('.pdf'):
            self.input_data_preprocessed = self.read_images_from_pdf(self.input_path)
        else:
            self.input_data_preprocessed = [QRData(original_image=cv2.imread(self.input_path),
                                                   path=self.input_path)]

        self.input_data_processed = self.parse_data(list_of_data=self.input_data_preprocessed)
        return self.input_data_processed

    @classmethod
    def read_images_from_pdf(cls, filename: str, save_images: bool = False) -> list[QRData]:
        file = fitz.open(filename)

        total = 0
        list_of_paths = []
        list_of_cv_images = []
        for k in range(len(file)):
            page = file[k]
            image_list = page.get_images()
            if not image_list:
                continue

            for j, image_j in enumerate(image_list):
                ref_j = image_j[0]
                if not isinstance(ref_j, int):
                    continue
                image_j_base = file.extract_image(ref_j)
                image_j_bytes = image_j_base["image"]

                image_j_array = np.frombuffer(image_j_bytes, dtype=np.uint8)
                image_j_np = cv2.imdecode(image_j_array, cv2.IMREAD_GRAYSCALE)

                if save_images:
                    o_dir = os.path.dirname(filename)
                    b_name, ext = os.path.splitext(os.path.basename(filename))
                    path_string = os.path.join(o_dir, f"{total}__{b_name}.png")
                    cv2.imwrite(path_string, image_j_np)
                    list_of_paths.append(path_string)
                else:
                    list_of_paths.append(None)
                total += 1

                list_of_cv_images.append(image_j_np)

        # dedup images
        uniq_images, uniq_paths = [], []
        for img, pth in zip(list_of_cv_images, list_of_paths):
            flag = any([np.all(img == x) if img.shape == x.shape else False for x in uniq_images])
            if not flag:
                uniq_images.append(img)
                uniq_paths.append(pth)

        result = [
            QRData(original_image=img, path=pth, message=None)
            for img, pth in zip(uniq_images, uniq_paths)
        ]
        return result

    @classmethod
    def parse_data(cls, list_of_data: list[QRData]) -> list[QRData]:
        parsed_list_of_data = []

        detector = cv2.QRCodeDetector()
        for k, data in enumerate(list_of_data, start=1):
            message, vertices, qrcode = detector.detectAndDecode(data.original_image)

            if vertices is not None:
                qr_data = QRData(original_image=data.original_image,
                                 detected_image=qrcode,
                                 path=data.path,
                                 message=message)
                parsed_list_of_data.append(qr_data)

        return parsed_list_of_data


class App:
    IM_WIDTH = 192
    IM_HEIGHT = 192
    IM_PAD = 20

    def __init__(self, open_browser: bool = False) -> None:
        self.open_browser = open_browser
        self.root = TkinterDnD.Tk()
        self.root.title("QR Parser :: Drag and Drop QR Images")

        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_drop)

        self.image = ""
        self.path = ""
        self.load_blank_image()

        self.canvas = tkinter.Canvas(self.root,
                                     width=self.IM_WIDTH + 2 * self.IM_PAD,
                                     height=self.IM_HEIGHT + 2 * self.IM_PAD)
        self.canvas_image = self.canvas.create_image(self.IM_PAD, self.IM_PAD, anchor=tkinter.NW, image=self.image)

        self.output = tkinter.scrolledtext.ScrolledText(self.root, height=10)
        # self.output.configure(state='disabled')

        self.close_btn = tkinter.Button(self.root, text="Close", command=self.root.destroy)

        self.canvas.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
        self.output.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
        self.close_btn.pack()

    def load_blank_image(self):
        img2 = np.zeros([self.IM_HEIGHT, self.IM_WIDTH], dtype=np.uint8)
        img2.fill(255)
        image = Image.fromarray(img2)
        self.image = ImageTk.PhotoImage(image)

    def on_drop(self, event):
        response = re.findall(r"\{([^{}]+)\}|([^\s{}]+)", event.data)
        if response:
            input_paths = [xk for x in response for xk in x if xk]
        else:
            input_paths = [event.data]

        qr_parser_results = []
        for input_path in input_paths:
            qr_parser = PyQR(input_path=input_path)
            qr_parser.run()

            qr_parser_results.append(qr_parser)

        if self.open_browser:
            _ = [x.open_browsers() for x in qr_parser_results]

        contents = "\n".join([x.get_content() for x in qr_parser_results])
        contents = contents.strip()
        pyperclip.copy(contents)
        self.output.delete(1.0, tkinter.END)
        self.output.insert(tkinter.END, contents)

        images = [xk.detected_image for x in qr_parser_results for xk in x.input_data_processed]
        if len(images) != 1:
            self.load_blank_image()
            self.canvas.itemconfig(self.canvas_image, image=self.image)
        else:
            img0 = images[0]
            image0 = Image.fromarray(cv2.resize(img0, dsize=(self.IM_WIDTH, self.IM_HEIGHT)))
            self.image = ImageTk.PhotoImage(image0)
            self.canvas.itemconfig(self.canvas_image, image=self.image)

    def mainloop(self):
        self.root.mainloop()


def main():
    args = docopt(__doc__)

    if args["<PATH>"]:
        all_content = []
        for path in args["<PATH>"]:
            qr = PyQR(input_path=path)
            qr.run()
            if qr.input_data_processed:
                content = qr.get_content()
                all_content.append(content)
                if args["--open"]:
                    qr.open_browsers()
        all_content_string = "\n".join(all_content)
        print(all_content_string)
        pyperclip.copy(all_content_string)
    else:
        parser = App(open_browser=args["--open"])
        parser.mainloop()


if __name__ == '__main__':
    main()
