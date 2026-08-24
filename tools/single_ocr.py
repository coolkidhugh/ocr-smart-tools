"""Recognize a single image."""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.ocr_engine import ocr_engine


def run_single_ocr():
    print("\n" + "=" * 60)
    print("Single image OCR")
    print("=" * 60)

    image_path = input("\nImage path (you can drag the file here): ").strip().strip('"')

    if not os.path.exists(image_path):
        print("File not found.")
        return

    preserve = input("Preserve the original layout? (y/n, default n): ").strip().lower()
    preserve_layout = preserve == "y"

    print("\nRecognizing...")

    try:
        result = ocr_engine.recognize(image_path)
        text = ocr_engine.extract_text(result, preserve_layout=preserve_layout)

        if not text:
            print("No text detected.")
            return

        print("\n" + "=" * 60)
        print("Result")
        print("=" * 60)
        print(text)
        print("=" * 60)

        if input("\nSave the result? (y/n): ").strip().lower() == "y":
            os.makedirs("output", exist_ok=True)
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output_path = os.path.join("output", f"{base_name}_ocr.txt")

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)

            print(f"Saved to: {output_path}")

        if input("Show per-line confidence? (y/n): ").strip().lower() == "y":
            print("\nDetail:")
            for i, item in enumerate(ocr_engine.get_detailed_result(result), 1):
                print(f"{i}. {item['text']} (confidence: {item['confidence']:.2%})")

    except Exception as e:
        print(f"Recognition failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    run_single_ocr()
