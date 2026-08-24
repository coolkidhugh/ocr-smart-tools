"""
OCR Smart Tools

Interactive entry point. Every menu item below maps to a module that exists.
"""
import sys


def show_menu():
    print("""
OCR Smart Tools
Local OCR built on PaddleOCR. Runs offline.

  1. Single image
  2. Batch folder
  3. Screen capture to text
  4. LLM cleanup pass on existing text  (needs DEEPSEEK_API_KEY)

  0. Quit
""")


def main():
    while True:
        show_menu()
        choice = input("Select (0-4): ").strip()

        if choice == "0":
            break

        elif choice == "1":
            from tools.single_ocr import run_single_ocr
            run_single_ocr()

        elif choice == "2":
            from tools.batch_ocr import run_batch_ocr
            run_batch_ocr()

        elif choice == "3":
            from tools.screenshot_to_text import run_screenshot_ocr
            run_screenshot_ocr()

        elif choice == "4":
            from tools.ai_editor import run_ai_editor
            run_ai_editor()

        else:
            print("\nNot a valid option.")

        input("\nPress Enter to continue...")
        print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()
