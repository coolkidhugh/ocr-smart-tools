"""
Batch OCR over a folder.

Walks a directory, runs OCR on every supported image, and writes one .txt per
image plus a combined results.json carrying per-line confidence.
"""
import os
import sys
import json
import time

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.ocr_engine import ocr_engine

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}


def find_images(folder, recursive=True):
    """Return sorted paths of every supported image under `folder`."""
    found = []
    if recursive:
        for root, _dirs, files in os.walk(folder):
            for name in files:
                if os.path.splitext(name)[1].lower() in IMAGE_EXTENSIONS:
                    found.append(os.path.join(root, name))
    else:
        for name in os.listdir(folder):
            path = os.path.join(folder, name)
            if os.path.isfile(path) and os.path.splitext(name)[1].lower() in IMAGE_EXTENSIONS:
                found.append(path)
    return sorted(found)


def batch_ocr(folder, output_dir="output", preserve_layout=False, recursive=True):
    """
    Run OCR across a folder.

    Returns:
        list of {"file", "text", "lines", "error"} records.
    """
    images = find_images(folder, recursive=recursive)

    if not images:
        print(f"No supported images found under: {folder}")
        return []

    os.makedirs(output_dir, exist_ok=True)
    print(f"\nFound {len(images)} image(s). Starting.\n")

    records = []
    started = time.time()

    for i, path in enumerate(images, 1):
        rel = os.path.relpath(path, folder)
        print(f"[{i}/{len(images)}] {rel}")

        record = {"file": rel, "text": "", "lines": [], "error": None}

        try:
            result = ocr_engine.recognize(path)
            text = ocr_engine.extract_text(result, preserve_layout=preserve_layout)
            details = ocr_engine.get_detailed_result(result)

            record["text"] = text
            record["lines"] = details

            if text:
                # Mirror the source tree so filenames from different subfolders
                # cannot overwrite one another
                stem = os.path.splitext(rel)[0].replace(os.sep, "_")
                out_path = os.path.join(output_dir, f"{stem}.txt")
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(text)
                print(f"        {len(details)} line(s) -> {out_path}")
            else:
                print("        no text detected")

        except Exception as e:
            record["error"] = str(e)
            print(f"        failed: {e}")

        records.append(record)

    summary_path = os.path.join(output_dir, "results.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    ok = sum(1 for r in records if r["text"])
    failed = sum(1 for r in records if r["error"])
    elapsed = time.time() - started

    print(f"\nDone in {elapsed:.1f}s. {ok} with text, {failed} failed, "
          f"{len(records) - ok - failed} empty.")
    print(f"Summary: {summary_path}")

    return records


def run_batch_ocr():
    print("\n" + "=" * 60)
    print("Batch folder OCR")
    print("=" * 60)

    folder = input("\nFolder path (default: input): ").strip().strip('"') or "input"

    if not os.path.isdir(folder):
        print("Folder not found.")
        return

    preserve = input("Preserve the original layout? (y/n, default n): ").strip().lower()
    recursive = input("Include subfolders? (y/n, default y): ").strip().lower() != "n"

    batch_ocr(
        folder,
        preserve_layout=(preserve == "y"),
        recursive=recursive,
    )


if __name__ == "__main__":
    run_batch_ocr()
