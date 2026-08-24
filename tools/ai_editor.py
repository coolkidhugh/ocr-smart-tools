"""
Optional LLM cleanup pass over OCR output.

OCR gets characters wrong in predictable ways and breaks lines in the middle of
sentences. This runs the raw text through an LLM to repair it. It is optional:
everything else in this project works offline, this step does not.
"""
import os
import time
import requests
from typing import Optional

PROMPTS = {
    "clean": """You are a careful text editor. Clean up the following OCR output.

1. Fix common OCR confusions (0 vs O, 1 vs l, rn vs m)
2. Repair broken line wrapping and spacing
3. Normalize punctuation
4. Preserve the original structure and meaning. Do not summarize or reword
5. Return only the cleaned text, with no commentary

OCR output:
{text}

Cleaned text:""",

    "extract": """You are an information extraction specialist. Extract the key fields from the following OCR text.

1. Identify the document type (invoice, contract, table, form, ...)
2. Pull out the key fields and values
3. Return structured output as JSON or a Markdown table

OCR output:
{text}

Extracted fields:""",

    "translate": """Translate the following OCR text into English.

1. Preserve the original formatting
2. Translate domain terminology accurately
3. Produce natural English, not a literal gloss

OCR output:
{text}

Translation:""",

    "summarize": """Summarize the following OCR text.

1. Capture the core content
2. Keep key figures and names intact
3. Be concise

OCR output:
{text}

Summary:""",

    "structure": """Convert the following OCR text into structured data.

1. Identify the fields and their types
2. Return valid JSON
3. Do not drop or invent data

OCR output:
{text}

JSON:""",
}


class AIEditor:
    """Thin client over an OpenAI-compatible chat completions endpoint."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "deepseek-chat",
        base_url: str = "https://api.deepseek.com/v1/chat/completions",
    ):
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        self.model = model
        self.base_url = base_url

    def edit_text(self, ocr_text: str, task: str = "clean") -> str:
        """
        Run one cleanup task.

        Args:
            ocr_text: raw OCR output
            task: one of clean, extract, translate, summarize, structure
        """
        if not self.api_key:
            return "No API key configured. Set the DEEPSEEK_API_KEY environment variable."

        prompt = PROMPTS.get(task, PROMPTS["clean"]).format(text=ocr_text)

        try:
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 4000,
                },
                timeout=60,
            )

            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            return f"API call failed: {response.status_code} - {response.text}"

        except Exception as e:
            return f"Request failed: {e}"

    def batch_edit(self, texts: list, task: str = "clean") -> list:
        results = []
        for i, text in enumerate(texts, 1):
            print(f"Processing [{i}/{len(texts)}]...")
            results.append(self.edit_text(text, task))
        return results


def run_ai_editor():
    print("\n" + "=" * 60)
    print("LLM cleanup pass")
    print("=" * 60)

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("\nNo API key found in DEEPSEEK_API_KEY.")
        if input("Enter one now for this session? (y/n): ").strip().lower() == "y":
            api_key = input("API key: ").strip()
            os.environ["DEEPSEEK_API_KEY"] = api_key
            print("Set for this session only.")
        else:
            print("Cleanup pass unavailable without a key.")
            return

    editor = AIEditor(api_key)

    print("\nInput source:")
    print("  1. Type the text")
    print("  2. Read from a file")
    choice = input("\nSelect (1-2): ").strip()

    if choice == "1":
        print("\nPaste the OCR text, then type END on its own line:")
        lines = []
        while True:
            line = input()
            if line.strip().upper() == "END":
                break
            lines.append(line)
        ocr_text = "\n".join(lines)

    elif choice == "2":
        filepath = input("File path: ").strip().strip('"')
        if not os.path.exists(filepath):
            print("File not found.")
            return
        with open(filepath, "r", encoding="utf-8") as f:
            ocr_text = f.read()

    else:
        print("Not a valid option.")
        return

    if not ocr_text.strip():
        print("Nothing to process.")
        return

    print("\nTask:")
    print("  1. Clean and reformat")
    print("  2. Extract key fields")
    print("  3. Translate to English")
    print("  4. Summarize")
    print("  5. Convert to structured JSON")

    task = {
        "1": "clean",
        "2": "extract",
        "3": "translate",
        "4": "summarize",
        "5": "structure",
    }.get(input("\nSelect (1-5): ").strip(), "clean")

    print(f"\nRunning '{task}'...")
    result = editor.edit_text(ocr_text, task)

    print("\n" + "=" * 60)
    print("Result")
    print("=" * 60)
    print(result)

    if input("\nSave the result? (y/n): ").strip().lower() == "y":
        os.makedirs("output", exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join("output", f"cleaned_{timestamp}.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"Saved to: {output_path}")


if __name__ == "__main__":
    run_ai_editor()
