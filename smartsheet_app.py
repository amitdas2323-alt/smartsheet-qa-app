"""
Smartsheet Executive Summary & Prompt on Data.

Usage:
  python smartsheet_app.py summary          # Print executive summary
  python smartsheet_app.py prompt "question" # Answer a question using sheet data
  python smartsheet_app.py prompt           # Interactive prompt mode

Requires .env or environment:
  SMARTSHEET_ACCESS_TOKEN   (required)
  SMARTSHEET_SHEET_ID       (required)
  OPENAI_API_KEY            (optional, for natural-language answers to prompts)
"""

import sys
from pathlib import Path

# Load .env from the folder containing this script (project root)
_project_dir = Path(__file__).resolve().parent
_env_file = _project_dir / ".env"
try:
    from dotenv import load_dotenv
    load_dotenv(_env_file, override=True)  # .env in project folder overrides shell env
except ImportError:
    pass

# So you can verify which .env is used (e.g. if you get 401)
ENV_FILE_PATH = str(_env_file)

from smartsheet_client import get_sheet, sheet_to_table, get_client_config
from summary import build_executive_summary, summary_to_console
from prompt_on_data import answer_prompt


def load_sheet_data():
    """Fetch sheet and return (column_names, rows, sheet_name)."""
    if not _env_file.exists():
        print(f"Warning: .env not found at {ENV_FILE_PATH}")
    else:
        print(f"Using .env: {ENV_FILE_PATH}")
    get_client_config()  # validate env
    sheet = get_sheet()
    column_names, rows = sheet_to_table(sheet)
    sheet_name = sheet.get("name", "Smartsheet")
    return column_names, rows, sheet_name


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("Commands: summary | prompt [question]")
        sys.exit(0)

    command = sys.argv[1].lower()

    if command == "summary":
        column_names, rows, sheet_name = load_sheet_data()
        summary_to_console(column_names, rows, sheet_name=sheet_name)
        return

    if command == "prompt":
        column_names, rows, sheet_name = load_sheet_data()
        if len(sys.argv) > 2:
            question = " ".join(sys.argv[2:])
        else:
            question = input("Ask a question about the Smartsheet data: ").strip()
            if not question:
                print("No question entered.")
                sys.exit(1)
        answer = answer_prompt(column_names, rows, question, sheet_name=sheet_name)
        print("\n" + answer)
        return

    print("Unknown command. Use: summary | prompt [question]")
    sys.exit(1)


if __name__ == "__main__":
    main()
