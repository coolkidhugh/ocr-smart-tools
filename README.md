# OCR Smart Tools

Local OCR toolbox built on PaddleOCR. Recognition runs entirely on your machine, so documents never leave it.

Built for the case where someone is retyping text off scans, PDFs that block copy, or a legacy application that has no export.

---

## What it does

| | |
|---|---|
| **Single image** | One file, optional layout preservation, optional per-line confidence |
| **Batch folder** | Walks a directory, one `.txt` per image plus a combined `results.json` with confidence scores |
| **Screen capture** | Captures the screen and OCRs it. Immediate, delayed, or on an interval for scrolling through a long document |
| **LLM cleanup** | Optional pass to repair OCR errors, extract fields, or convert to JSON. The only step that needs network access |

**Layout preservation** is the part worth knowing about. Instead of returning boxes in detection order, it groups them into rows by their vertical centre and sorts each row left to right, joining cells with tabs. Tables and forms come back readable rather than scrambled. The row threshold is tunable for dense or loosely spaced scans.

---

## Install

```bash
pip install -r requirements.txt
```

PaddleOCR downloads its models on first run, roughly 10 MB, once. After that the tool works offline.

## Run

```bash
python main.py
```

Or use a module directly:

```bash
python tools/batch_ocr.py
python tools/single_ocr.py
```

Or from your own code:

```python
from core.ocr_engine import ocr_engine

result = ocr_engine.recognize("invoice.png")
text = ocr_engine.extract_text(result, preserve_layout=True)
lines = ocr_engine.get_detailed_result(result)   # text, confidence, bounding box
```

```python
from tools.batch_ocr import batch_ocr

records = batch_ocr("scans/", output_dir="output", preserve_layout=True)
```

---

## Optional: LLM cleanup

Only needed for menu option 4. Everything else runs offline.

```bash
export DEEPSEEK_API_KEY=your_key      # Windows: set DEEPSEEK_API_KEY=your_key
```

Any OpenAI-compatible endpoint works. Point `AIEditor` at a different `base_url` and `model`, including a local one:

```python
from tools.ai_editor import AIEditor

editor = AIEditor(
    api_key="not-needed",
    model="qwen2.5",
    base_url="http://localhost:11434/v1/chat/completions",
)
```

---

## Layout

```
ocr-smart-tools/
├── main.py                      interactive entry point
├── core/
│   └── ocr_engine.py            singleton PaddleOCR wrapper, layout reconstruction
├── tools/
│   ├── single_ocr.py            one image
│   ├── batch_ocr.py             folder walk, txt + results.json
│   ├── screenshot_to_text.py    screen capture to text
│   └── ai_editor.py             optional LLM cleanup
├── input/                       drop files here
└── output/                      results land here
```

---

## Languages

Defaults to Chinese, which also handles mixed Chinese and English. Pass another code to switch:

```python
ocr_engine.recognize("page.png", lang="en")     # en, japan, korean, fr, german, ...
```

The model reloads on a language change, so group work by language when processing in bulk.

---

## Notes

- CPU by default. For GPU, install `paddlepaddle-gpu` and set `use_gpu=True` in `core/ocr_engine.py`.
- The engine is a singleton: the model loads once per process. Long batches pay that cost a single time.
- Screen capture uses PIL's `ImageGrab` and is tested on Windows.

## License

MIT
