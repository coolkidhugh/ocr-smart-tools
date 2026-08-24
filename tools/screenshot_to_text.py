"""
Screen capture to text.

For content that is on screen but not selectable: a PDF viewer that blocks copy,
a legacy desktop application, a remote desktop session, a scanned page open in an
image viewer. Capture the screen, OCR it, get text back.

Uses PIL's ImageGrab only, so there are no dependencies beyond the base install.
"""
import os
import sys
import time

from PIL import ImageGrab

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.ocr_engine import ocr_engine


class ScreenshotOCR:
    def __init__(self, screenshots_dir="screenshots"):
        self.screenshots_dir = screenshots_dir
        os.makedirs(self.screenshots_dir, exist_ok=True)

    def _save(self, image, prefix):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(self.screenshots_dir, f"{prefix}_{timestamp}.png")
        image.save(filepath)
        print(f"Saved: {filepath}")
        return filepath

    def capture_now(self):
        """Capture the full screen immediately."""
        print("Capturing...")
        return self._save(ImageGrab.grab(), "screen")

    def capture_delayed(self, delay=3):
        """Capture after a delay, so you can bring the target window forward."""
        print(f"Capturing in {delay}s. Switch to the target window now.")
        for i in range(delay, 0, -1):
            print(f"  {i}...")
            time.sleep(1)
        return self._save(ImageGrab.grab(), "delayed")

    def capture_interval(self, interval=5, count=10):
        """
        Capture repeatedly at a fixed interval.

        Intended for long documents: start this, then scroll the source at a
        steady pace and OCR the whole run at the end.
        """
        print(f"\nCapturing {count} time(s), every {interval}s. Starting in 3s.")
        time.sleep(3)

        filepaths = []
        for i in range(count):
            print(f"\n[{i + 1}/{count}]")
            filepaths.append(self._save(ImageGrab.grab(), f"seq{i + 1:03d}"))
            if i < count - 1:
                time.sleep(interval)

        return filepaths

    def ocr(self, image_path, preserve_layout=True):
        print(f"Recognizing: {os.path.basename(image_path)}")
        try:
            result = ocr_engine.recognize(image_path)
            text = ocr_engine.extract_text(result, preserve_layout=preserve_layout)
            if not text:
                print("  no text detected")
            return text
        except Exception as e:
            print(f"  failed: {e}")
            return ""

    def save_result(self, text, filename=None):
        os.makedirs("output", exist_ok=True)
        if filename is None:
            filename = f"screen_ocr_{time.strftime('%Y%m%d_%H%M%S')}.txt"
        output_path = os.path.join("output", filename)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Saved to: {output_path}")
        return output_path


def run_screenshot_ocr():
    tool = ScreenshotOCR()

    print("\n" + "=" * 60)
    print("Screen capture to text")
    print("=" * 60)

    print("\n  1. Capture now")
    print("  2. Capture after 3s (time to switch windows)")
    print("  3. Capture on an interval (for scrolling through a long document)")
    print("  4. OCR an image already on disk")

    choice = input("\nSelect (1-4): ").strip()
    filepaths = []

    if choice == "1":
        filepaths.append(tool.capture_now())

    elif choice == "2":
        filepaths.append(tool.capture_delayed())

    elif choice == "3":
        interval = int(input("Interval in seconds (default 5): ").strip() or "5")
        count = int(input("How many captures (default 10): ").strip() or "10")
        filepaths = tool.capture_interval(interval, count)

    elif choice == "4":
        filepath = input("Image path: ").strip().strip('"')
        if not os.path.exists(filepath):
            print("File not found.")
            return
        filepaths.append(filepath)

    else:
        print("Not a valid option.")
        return

    if not filepaths:
        print("Nothing to recognize.")
        return

    print(f"\nRunning OCR on {len(filepaths)} image(s).\n")

    sections = []
    for i, filepath in enumerate(filepaths, 1):
        print(f"[{i}/{len(filepaths)}]", end=" ")
        text = tool.ocr(filepath)
        if text:
            sections.append(text)

    if not sections:
        print("\nNo text found in any capture.")
        return

    separator = "\n\n" + "=" * 60 + "\n\n"
    combined = separator.join(sections)

    print("\n" + "=" * 60)
    print(f"Done. {len(sections)} of {len(filepaths)} capture(s) produced text, "
          f"{len(combined)} characters total.")
    print("=" * 60)
    print(combined[:500] + "..." if len(combined) > 500 else combined)

    if input("\nSave the result? (y/n): ").strip().lower() == "y":
        tool.save_result(combined)

    return combined


if __name__ == "__main__":
    run_screenshot_ocr()
