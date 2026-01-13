import cv2
import pytesseract
from typing import Tuple, Optional

def _resize_for_ocr(gray: "cv2.Mat", scale: float = 2.5) -> "cv2.Mat":
    """Upscale the image to improve OCR on small text."""
    h, w = gray.shape[:2]
    new_w, new_h = int(w * scale), int(h * scale)
    return cv2.resize(gray, (new_w, new_h), interpolation=cv2.INTER_CUBIC)

def _preprocess(gray: "cv2.Mat") -> Tuple["cv2.Mat", "cv2.Mat"]:
    """
    Create two preprocessed variants:
    1) Otsu threshold (often good for clean scans)
    2) Adaptive threshold (often good for uneven lighting / screenshots)
    """
    # Denoise (helps with JPEG artifacts)
    denoised = cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)

    # Slight sharpen (unsharp mask)
    blur = cv2.GaussianBlur(denoised, (0, 0), sigmaX=1.0)
    sharpened = cv2.addWeighted(denoised, 1.6, blur, -0.6, 0)

    # Otsu binarization
    _, otsu = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Adaptive binarization
    adaptive = cv2.adaptiveThreshold(
        sharpened,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        2
    )

    return otsu, adaptive

def extract_text_from_image(image_path: str, lang: str = "spa") -> str:
    """
    Extract all visible text from an image using Tesseract OCR.
    Tries two preprocessing variants and picks the one with better average confidence.
    """
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = _resize_for_ocr(gray, scale=2.5)

    v1, v2 = _preprocess(gray)

    # Tesseract config:
    # --oem 3  : LSTM engine
    # --psm 4  : assume a single column of text (often good for receipts)
    # You can try --psm 6 if your layout is more "block-like".
    base_config = f"--oem 3 --psm 4 -l {lang}"

    # Get text + confidence via TSV so we can choose the better preprocessing
    def ocr_with_conf(img: "cv2.Mat") -> Tuple[str, float]:
        data = pytesseract.image_to_data(img, config=base_config, output_type=pytesseract.Output.DICT)
        words = data.get("text", [])
        confs = data.get("conf", [])

        # Average confidence over non-empty words with valid confidence
        vals = []
        for w, c in zip(words, confs):
            w = (w or "").strip()
            try:
                c = float(c)
            except Exception:
                continue
            if w and c >= 0:
                vals.append(c)

        avg_conf = sum(vals) / len(vals) if vals else 0.0
        text = pytesseract.image_to_string(img, config=base_config)
        return text, avg_conf

    text1, conf1 = ocr_with_conf(v1)
    text2, conf2 = ocr_with_conf(v2)

    best_text = text1 if conf1 >= conf2 else text2
    return best_text

if __name__ == "__main__":
    path = "/Users/pedro/Downloads/WhatsApp Image 2025-12-30 at 12.41.26.jpeg"
    text = extract_text_from_image(path, lang="spa")
    print(text)
