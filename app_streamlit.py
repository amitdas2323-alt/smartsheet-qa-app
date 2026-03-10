"""
Simple web UI to prompt on the same Smartsheet data.
Run: streamlit run app_streamlit.py
Share the URL with others so they can ask questions in the browser (no Python or token needed on their side).
Locally: use .env (SMARTSHEET_ACCESS_TOKEN, SMARTSHEET_SHEET_ID). On Streamlit Cloud: use app Secrets.
"""

import os
import sys
from pathlib import Path

_project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(_project_dir))
_env_file = _project_dir / ".env"
try:
    from dotenv import load_dotenv
    load_dotenv(_env_file, override=True)
except ImportError:
    pass

import streamlit as st

# Streamlit Community Cloud: inject Secrets into os.environ so smartsheet_client and prompt_on_data see them
try:
    _secret_keys = (
        "SMARTSHEET_ACCESS_TOKEN", "SMARTSHEET_SHEET_ID", "OPENAI_API_KEY", "OPENAI_MODEL",
        "JLL_GPT_TOKEN_URL", "JLL_GPT_CLIENT_ID", "JLL_GPT_CLIENT_SECRET", "JLL_GPT_REFRESH_TOKEN",
    )
    for key in _secret_keys:
        if key in st.secrets and st.secrets[key]:
            os.environ[key] = str(st.secrets[key]).strip()
except Exception:
    pass
import pandas as pd
from smartsheet_client import get_sheet, sheet_to_table, get_client_config
from summary import build_executive_summary
from prompt_on_data import answer_prompt_structured


@st.cache_data(ttl=300)
def load_sheet_data():
    """Fetch sheet once per 5 min so prompts are fast."""
    get_client_config()
    sheet = get_sheet()
    column_names, rows = sheet_to_table(sheet)
    sheet_name = sheet.get("name", "Smartsheet")
    return column_names, rows, sheet_name


def main():
    st.set_page_config(page_title="Smartsheet Q&A", layout="centered")
    st.title("Smartsheet data — ask a question")

    try:
        column_names, rows, sheet_name = load_sheet_data()
    except Exception as e:
        st.error(f"Cannot load sheet: {e}. Check .env or Streamlit Secrets (SMARTSHEET_ACCESS_TOKEN, SMARTSHEET_SHEET_ID).")
        return

    st.caption(f"Sheet: **{sheet_name}** · {len(rows)} rows")

    question = st.text_input("Ask a question about the data", placeholder="e.g. How many accounts are on track?")
    if question:
        with st.spinner("Answering..."):
            result = answer_prompt_structured(column_names, rows, question, sheet_name=sheet_name)
        st.markdown("---")
        if result["type"] == "table":
            st.caption(result.get("message", ""))
            display_cols = result["columns"]
            table_rows = [{c: r.get(c, "") for c in display_cols} for r in result["rows"]]
            df = pd.DataFrame(table_rows, columns=display_cols)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.markdown(result["content"])

    with st.expander("Executive summary"):
        summary_text = build_executive_summary(column_names, rows, sheet_name=sheet_name)
        st.markdown(summary_text)


if __name__ == "__main__":
    main()
