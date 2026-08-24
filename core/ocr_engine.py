"""
OCR core engine.

Singleton, so the model is loaded once per process rather than per call.
"""
from paddleocr import PaddleOCR
import numpy as np
from PIL import Image
import io


class OCREngine:
    """Singleton wrapper around PaddleOCR."""

    _instance = None
    _ocr = None
    _lang = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, lang="ch"):
        if self._ocr is None:
            print("Loading OCR model...")
            self._ocr = PaddleOCR(
                use_angle_cls=True,   # detect and correct text orientation
                lang=lang,
                use_gpu=False,
                show_log=False,
            )
            self._lang = lang
            print("OCR model ready.")

    def recognize(self, image_input, lang="ch"):
        """
        Run OCR on an image.

        Args:
            image_input: file path, PIL Image, or raw bytes
            lang: 'ch', 'en', 'korean', 'japan', 'fr', 'german', ...

        Returns:
            Raw PaddleOCR result.
        """
        # Reload only when the requested language differs from the loaded one
        if lang != self._lang:
            print(f"Switching language model to: {lang}")
            self._ocr = PaddleOCR(
                use_angle_cls=True,
                lang=lang,
                use_gpu=False,
                show_log=False,
            )
            self._lang = lang

        if isinstance(image_input, str):
            return self._ocr.ocr(image_input, cls=True)

        if isinstance(image_input, bytes):
            img = Image.open(io.BytesIO(image_input))
            if img.mode != "RGB":
                img = img.convert("RGB")
            return self._ocr.ocr(np.array(img), cls=True)

        if isinstance(image_input, Image.Image):
            img = image_input
            if img.mode != "RGB":
                img = img.convert("RGB")
            return self._ocr.ocr(np.array(img), cls=True)

        raise ValueError(f"Unsupported image input type: {type(image_input)}")

    def extract_text(self, result, preserve_layout=False):
        """
        Pull plain text out of an OCR result.

        Args:
            result: raw PaddleOCR result
            preserve_layout: group boxes into rows and keep left-to-right order,
                             joining cells with tabs. Useful for tables and forms.

        Returns:
            str
        """
        if not result or not result[0]:
            return ""

        texts, boxes = [], []
        for line in result[0]:
            texts.append(line[1][0])
            boxes.append(line[0])

        if preserve_layout:
            return self._group_by_rows(texts, boxes)
        return "\n".join(texts)

    def _group_by_rows(self, texts, boxes, threshold=15):
        """
        Reconstruct reading order from bounding boxes.

        Boxes whose vertical centres fall within `threshold` pixels are treated as
        one row, then sorted left to right. Raise the threshold for loosely spaced
        scans, lower it for dense text.
        """
        if not texts or not boxes:
            return ""

        items = [
            {
                "text": text,
                "y": (box[0][1] + box[2][1]) / 2,
                "x": box[0][0],
            }
            for text, box in zip(texts, boxes)
        ]

        items.sort(key=lambda item: item["y"])

        rows = []
        current_row = [items[0]]
        current_y = items[0]["y"]

        for item in items[1:]:
            if abs(item["y"] - current_y) < threshold:
                current_row.append(item)
            else:
                rows.append(current_row)
                current_row = [item]
                current_y = item["y"]
        rows.append(current_row)

        lines = []
        for row in rows:
            row.sort(key=lambda item: item["x"])
            lines.append("\t".join(item["text"] for item in row))

        return "\n".join(lines)

    def get_detailed_result(self, result):
        """
        Return per-box detail including confidence.

        Returns:
            [{"text": str, "confidence": float, "box": [[x, y], ...]}, ...]
        """
        if not result or not result[0]:
            return []

        return [
            {
                "text": line[1][0],
                "confidence": float(line[1][1]),
                "box": [[int(p[0]), int(p[1])] for p in line[0]],
            }
            for line in result[0]
        ]


# Module-level singleton
ocr_engine = OCREngine()
