"""
Answer user prompts using Smartsheet data.
Uses OpenAI when OPENAI_API_KEY is set; otherwise uses shared matching logic.

Shared logic (CLI and web app): _get_matching_rows() applies in order:
  1) Account name filter (" for X" → Account Name contains X; "go live" → show go-live columns)
  2) Column filters (Vertical e.g. life sciences, Baseline status e.g. on track, AI accounts)
  3) Region filter ("EMEA accounts", "AMER", "APAC", "LATAM" → Lead Region or Account Region(s) contains that)
  4) Assignee filter ("assigned to X" → WDAA BA / Client Success Lead etc. contain X)
  5) Keyword search fallback (question words anywhere in row)
"""

import os
import re
from datetime import datetime, timedelta
from typing import Any

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Month name or abbreviation -> number (1-12)
_MONTH_NAMES = {
    "january": 1, "jan": 1,
    "february": 2, "feb": 2,
    "march": 3, "mar": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10,
    "november": 11, "nov": 11,
    "december": 12, "dec": 12,
}


def _rows_to_context(column_names: list[str], rows: list[dict[str, Any]], max_chars: int = 12000) -> str:
    """Serialize table to a string for LLM context, truncating if needed."""
    header = " | ".join(column_names)
    lines = [header]
    for r in rows:
        cells = [str(r.get(c, ""))[:50] for c in column_names]
        lines.append(" | ".join(cells))
    text = "\n".join(lines)
    if len(text) > max_chars:
        text = text[: max_chars - 50] + "\n... (truncated)"
    return text


def _parse_go_live_month_year(question: str) -> tuple[int, int] | None:
    """
    If the question asks for go live in a specific month/year (e.g. 'April 2026', 'expected to go live in March 2027'),
    return (month, year). Else return None.
    """
    q = question.lower().strip()
    if "go live" not in q and "golive" not in q:
        return None
    # Match "April 2026", "Apr 2026", "in April 2026", "April 2026 go live"
    year_match = re.search(r"\b(20[2-4]\d)\b", q)  # 2020-2049
    if not year_match:
        return None
    year = int(year_match.group(1))
    month = None
    for name, num in _MONTH_NAMES.items():
        if name in q:
            month = num
            break
    if month is None:
        # Try "4/2026" or "04/2026"
        m = re.search(r"\b(1[0-2]|[1-9])\s*/\s*(20[2-4]\d)\b", q)
        if m:
            month = int(m.group(1))
            year = int(m.group(2))
        else:
            return None
    return (month, year)


def _parse_cell_date(value: Any) -> tuple[int, int] | None:
    """Parse a cell value as a date; return (month, year) or None."""
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    # ISO: 2026-04-15 or 2026-04-15T00:00:00Z
    m = re.match(r"(\d{4})-(\d{1,2})-(\d{1,2})", s)
    if m:
        try:
            return (int(m.group(2)), int(m.group(1)))
        except ValueError:
            return None
    # US format: 04/15/2026 or 4/15/2026
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if m:
        try:
            return (int(m.group(1)), int(m.group(3)))
        except ValueError:
            return None
    # Excel serial (days since 1900-01-01): number
    try:
        n = float(s)
        if n > 1000:  # likely Excel serial
            d = datetime(1899, 12, 30)  # Excel epoch
            d = d + timedelta(days=int(n))
            return (d.month, d.year)
    except (ValueError, TypeError):
        pass
    # Try Python date parse for "April 15, 2026" etc.
    for fmt in ("%B %d, %Y", "%b %d, %Y", "%d %B %Y", "%d %b %Y", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(s[:50], fmt)
            return (dt.month, dt.year)
        except ValueError:
            continue
    return None


def _try_go_live_month_filter(
    column_names: list[str], rows: list[dict[str, Any]], question: str
) -> tuple[list[dict[str, Any]], bool] | None:
    """
    If the question asks for accounts expected to go live in a specific month/year
    (e.g. 'show me all accounts expected to go live in April 2026'), filter rows where
    the baseline go live target date falls in that month/year.
    """
    parsed = _parse_go_live_month_year(question)
    if parsed is None:
        return None
    target_month, target_year = parsed
    # Find go live target column (e.g. "Baseline Go Live Target", "Go Live Target")
    go_live_col = None
    for c in column_names:
        cl = c.lower()
        if "go live" in cl and ("target" in cl or "date" in cl):
            go_live_col = c
            break
    if not go_live_col:
        return None
    matches = []
    for r in rows:
        val = r.get(go_live_col)
        cell_date = _parse_cell_date(val)
        if cell_date is None:
            continue
        month, year = cell_date
        if month == target_month and year == target_year:
            matches.append(r)
    return (matches, True)


def _get_matching_rows(
    column_names: list[str], rows: list[dict[str, Any]], question: str
) -> tuple[list[dict[str, Any]], bool]:
    """
    Single source of truth for matching rows. Used by both CLI and web app.
    Returns (matches, display_go_live). Order: 1) account name, 2) go live month/year, 3) column filters,
    4) region, 5) assignee, 6) keyword search fallback.
    """
    # 1) " for <account name>" e.g. "go live date for Amgen"
    account_result = _try_account_name_filter(column_names, rows, question)
    if account_result is not None:
        return account_result

    # 2) "expected to go live in April 2026" -> filter by baseline go live target month/year
    go_live_result = _try_go_live_month_filter(column_names, rows, question)
    if go_live_result is not None:
        return go_live_result

    # 3) Column filters (Vertical, Baseline status, AI accounts)
    matches = _try_column_filter(column_names, rows, question)
    if matches is not None:
        return (matches, False)

    # 3) Region filter (EMEA, AMER, APAC, LATAM accounts)
    region_matches = _try_region_filter(column_names, rows, question)
    if region_matches is not None:
        return (region_matches, False)

    # 4) "assigned to X" / "accounts assigned to X"
    assignee_matches = _try_assignee_filter(column_names, rows, question)
    if assignee_matches is not None:
        return (assignee_matches, False)

    # 5) Keyword search fallback
    words = [w.lower() for w in question.split() if len(w) > 2]
    if not words:
        return ([], False)
    matches = [
        r for r in rows
        if any(w in " ".join(str(r.get(c, "")).lower() for c in column_names) for w in words)
    ]
    return (matches, False)


# Column-aware filters: (column_name, list of (question_phrase, cell_value_to_match))
# When the question contains the phrase, filter rows where column value equals or contains cell_value_to_match (case-insensitive).
_COLUMN_FILTERS = [
    ("Vertical", [
        ("life sciences", "Life Sciences"),
        ("life science", "Life Sciences"),
        ("financial services", "Financial Services"),
        ("technology", "Technology"),
        ("industrials", "Industrials"),
        ("healthcare", "Healthcare"),
        ("consumer goods", "Consumer Goods"),
    ]),
    ("Baseline: Overall Status", [
        ("on track", "On Track"),
        ("not started", "Not Started"),
        ("pre-requisites", "Pre-Requisites"),
        ("complete", "Complete"),
        ("live", "Live"),
    ]),
]


def _try_account_name_filter(
    column_names: list[str], rows: list[dict[str, Any]], question: str
) -> tuple[list[dict[str, Any]], bool] | None:
    """
    If the question asks about a specific account (e.g. 'go live date for Amgen'), filter by Account Name.
    Returns (matches, include_go_live_columns) or None.
    """
    name_col = "Account Name"
    if name_col not in column_names:
        return None
    q = question.strip()
    # " for X" or " for X?" at end → X is account name
    if " for " not in q:
        return None
    after_for = q.split(" for ", 1)[-1].strip()
    # Remove trailing ?
    after_for = after_for.rstrip("?").strip()
    if len(after_for) < 2:
        return None
    term = after_for.lower()
    matches = [
        r for r in rows
        if term in str(r.get(name_col, "") or "").lower()
    ]
    if not matches:
        return None
    include_go_live = "go live" in q.lower() or "golive" in q.lower()
    return (matches, include_go_live)


def _try_column_filter(
    column_names: list[str], rows: list[dict[str, Any]], question: str
) -> list[dict[str, Any]] | None:
    """
    If the question clearly asks for a specific column value, return filtered rows.
    Otherwise return None (caller will use keyword search).
    """
    q = question.lower().strip()
    for col_name, phrase_value_pairs in _COLUMN_FILTERS:
        if col_name not in column_names:
            continue
        for phrase, value in phrase_value_pairs:
            if phrase in q:
                value_lower = value.lower()
                matches = [
                    r for r in rows
                    if value_lower in str(r.get(col_name, "") or "").lower()
                ]
                return matches
    # "AI accounts" or "accounts where ... AI" → Unique Product Acct ID starts with AI
    if " ai " in f" {q} " or q.startswith("ai ") or "unique product" in q and "ai" in q:
        id_col = "Unique Product Acct ID"
        if id_col in column_names:
            matches = [
                r for r in rows
                if str(r.get(id_col, "") or "").strip().upper().startswith("AI")
            ]
            if matches:
                return matches
    return None


def _try_region_filter(
    column_names: list[str], rows: list[dict[str, Any]], question: str
) -> list[dict[str, Any]] | None:
    """'EMEA accounts', 'all AMER', 'APAC', 'LATAM' → filter by Lead Region only so table shows only that region."""
    q = question.lower().strip()
    region_keywords = [("emea", "EMEA"), ("amer", "AMER"), ("apac", "APAC"), ("latam", "LATAM")]
    lead_col = "Lead Region"
    if lead_col not in column_names:
        return None
    for phrase, value in region_keywords:
        if phrase in q:
            value_upper = value.upper()
            matches = [
                r for r in rows
                if value_upper in str(r.get(lead_col, "") or "").upper()
            ]
            return matches if matches else None
    return None


def _try_assignee_filter(
    column_names: list[str], rows: list[dict[str, Any]], question: str
) -> list[dict[str, Any]] | None:
    """'assigned to X' or 'accounts assigned to X' → filter rows where assignee columns contain X."""
    q = question.lower().strip()
    if "assigned to " not in q:
        return None
    after = q.split("assigned to ", 1)[-1].strip().rstrip("?").strip()
    if len(after) < 2:
        return None
    # Assignee-related columns (same as terminal one-offs)
    assignee_cols = [c for c in column_names if c in (
        "WDAA BA", "Client Success Lead (DO NOT DELETE)",
        "Account or Transition Tech Lead (if applicable)", "Acct Director/Regional Acct Director",
    )]
    if not assignee_cols:
        return None
    terms = after.lower().split()
    def row_has_assignee(r: dict) -> bool:
        for col in assignee_cols:
            val = str(r.get(col, "") or "").lower()
            if all(t in val for t in terms):
                return True
        return False
    matches = [r for r in rows if row_has_assignee(r)]
    return matches if matches else None


def _keyword_search(column_names: list[str], rows: list[dict[str, Any]], question: str) -> str:
    """Format matching rows as text for CLI. Uses same _get_matching_rows() as web app."""
    matches, _ = _get_matching_rows(column_names, rows, question)
    if not matches:
        words = [w for w in question.split() if len(w) > 2]
        if not words:
            return "No search terms. Ask something like 'show accounts that are life sciences' or 'go live date for Amgen'."
        return "No matching rows found. Try different terms or check the summary."
    lines = ["Matching rows (up to 15):", ""]
    key_cols = [c for c in column_names if c in ("Account Name", "Unique Product Acct ID", "Baseline: Overall Status", "Vertical")][:6]
    display_cols = (key_cols + [c for c in column_names if c not in key_cols])[:6]
    for i, r in enumerate(matches[:15]):
        parts = [f"{c}: {r.get(c)}" for c in display_cols]
        lines.append(f"Row {i+1}: " + " | ".join(parts))
    if len(matches) > 15:
        lines.append(f"\n... and {len(matches) - 15} more matches.")
    return "\n".join(lines)


# Keywords that suggest a column holds a person/name/role (for "who" or "name" questions)
_PERSON_COLUMN_KEYWORDS = (
    "president", "director", "lead", "name", "owner", "contact", "email",
    "divisional", "division", "assignee", "manager", "rep", "success",
    "account director", "client success", "wdaa", "acct ",
    " div ", " dp ", "dp/", "/dp", "div.", "divisional",
)


def _columns_relevant_to_question(column_names: list[str], question: str) -> list[str]:
    """
    Return columns whose names are suggested by the question (e.g. 'who is divisional president'
    -> prefer column 'Divisional President'). For 'who' / name questions, also prefer person/role columns.
    """
    q = question.lower().strip()
    words = [w for w in re.split(r"[\s,?]+", q) if len(w) > 1]
    phrases = []
    for i in range(len(words)):
        for j in range(i + 1, min(i + 4, len(words) + 1)):
            phrases.append(" ".join(words[i:j]))
    phrases = [p for p in phrases if len(p) > 2]
    relevant = []
    # Match question phrases and words to column names (e.g. "divisional president" -> "Divisional President")
    for col in column_names:
        col_lower = col.lower()
        for p in phrases:
            if p in col_lower:
                if col not in relevant:
                    relevant.append(col)
                break
        else:
            for w in words:
                if len(w) > 2 and w in col_lower:
                    if col not in relevant:
                        relevant.append(col)
                    break
    # When question asks "who" or for a name, add any column that looks like a person/role field
    if "who" in q or "name" in q or "president" in q or "director" in q or "lead" in q:
        for col in column_names:
            col_lower = col.lower()
            for kw in _PERSON_COLUMN_KEYWORDS:
                if kw in col_lower and col not in relevant:
                    relevant.append(col)
                    break
    return relevant


def _keyword_search_structured(
    column_names: list[str], rows: list[dict[str, Any]], question: str
) -> dict[str, Any]:
    """Structured result for web app. Uses same _get_matching_rows() as CLI."""
    matches, display_go_live = _get_matching_rows(column_names, rows, question)
    if not matches:
        return {"type": "text", "content": "No matching rows found. Try different terms or check the summary."}

    # Question-relevant columns first (e.g. "Divisional President" for "who is divisional president"),
    # then Account Name for context, then other key cols, go-live when relevant, then rest.
    # Single-row results: show more columns (25) so the answer is almost always visible.
    key_cols = [c for c in column_names if c in ("Account Name", "Unique Product Acct ID", "Baseline: Overall Status", "Vertical", "Lead Region", "Deployment Type")][:6]
    question_cols = _columns_relevant_to_question(column_names, question)
    go_live_cols = [c for c in column_names if "go live" in c.lower() or "target go live" in c.lower()]
    display_cols = []
    for c in question_cols:
        if c not in display_cols:
            display_cols.append(c)
    # Account Name early so user sees which account the answer refers to
    if "Account Name" in column_names and "Account Name" not in display_cols:
        display_cols.append("Account Name")
    for c in key_cols:
        if c not in display_cols:
            display_cols.append(c)
    if display_go_live and go_live_cols:
        for c in go_live_cols:
            if c not in display_cols:
                display_cols.append(c)
    for c in column_names:
        if c not in display_cols:
            display_cols.append(c)
    max_cols = 25 if len(matches) == 1 else 15
    display_cols = display_cols[:max_cols]
    return {
        "type": "table",
        "columns": display_cols,
        "rows": matches[:50],
        "total_matches": len(matches),
        "message": f"Found {len(matches)} matching row(s). Showing up to 50." if len(matches) > 50 else f"Found {len(matches)} matching row(s).",
    }


def _get_openai_key() -> str | None:
    """Return a valid API key (handles JLL GPT JWT expiry and optional refresh)."""
    try:
        from jll_gpt_token import get_effective_openai_key
        return get_effective_openai_key()
    except ImportError:
        return os.environ.get("OPENAI_API_KEY", "").strip() or None


def answer_with_openai(
    column_names: list[str],
    rows: list[dict[str, Any]],
    question: str,
    sheet_name: str = "Smartsheet",
) -> str:
    """Use OpenAI API to answer the question given the sheet data as context."""
    try:
        import openai
    except ImportError:
        return (
            "OpenAI package not installed. Run: pip install openai\n"
            "Falling back to keyword search."
        )

    api_key = _get_openai_key()
    if not api_key:
        return "OPENAI_API_KEY not set or JLL GPT token expired. Update Secrets or configure token refresh. Using keyword search instead."

    client = openai.OpenAI(api_key=api_key)
    context = _rows_to_context(column_names, rows)

    system = (
        "You are an assistant that answers questions based only on the provided Smartsheet table. "
        "Answer concisely for executives. If the data does not contain the answer, say so."
    )
    user_content = (
        f"Sheet: {sheet_name}\n\nTable (columns then rows):\n{context}\n\n"
        f"Question: {question}"
    )

    try:
        resp = client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_content},
            ],
            max_tokens=800,
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as e:
        return f"OpenAI error: {e}. Falling back to keyword search."


def answer_prompt(
    column_names: list[str],
    rows: list[dict[str, Any]],
    question: str,
    sheet_name: str = "Smartsheet",
    use_llm: bool = True,
) -> str:
    """
    Answer a user question using sheet data.
    If use_llm and OPENAI_API_KEY is set, uses OpenAI; otherwise uses keyword search.
    """
    if use_llm and _get_openai_key():
        result = answer_with_openai(column_names, rows, question, sheet_name)
        if "Falling back" not in result and "OPENAI_API_KEY not set" not in result and "token expired" not in result:
            return result
    return _keyword_search(column_names, rows, question)


def _parse_go_live_modified_days(question: str) -> int | None:
    """If question asks for go live modified in last N days, return N; else None."""
    q = question.lower().strip()
    if "go live" not in q or "modified" not in q:
        return None
    if "last week" in q or "past week" in q:
        return 7
    m = re.search(r"last\s+(\d+)\s+day", q)
    if m:
        return int(m.group(1))
    if "last day" in q or "past day" in q:
        return 1
    # default for "go live modified" with no number
    if "day" in q or "week" in q:
        return 7
    return None


def answer_prompt_structured(
    column_names: list[str],
    rows: list[dict[str, Any]],
    question: str,
    sheet_name: str = "Smartsheet",
    use_llm: bool = True,
) -> dict[str, Any]:
    """
    Like answer_prompt but returns a dict for UI: {"type": "table", "columns", "rows", "message"} or {"type": "text", "content"}.
    Use this in the web app to render a proper table when results are from keyword search.
    """
    # "Go live date modified in the last N days" → use Cell History report (same as terminal), exact 4 columns
    days = _parse_go_live_modified_days(question)
    if days is not None:
        try:
            from go_live_modified_report import get_go_live_modified_report
            report_rows = get_go_live_modified_report(days)
            cols = ["Account Name", "Go Live Target", "Modified", "Modified by"]
            return {
                "type": "table",
                "columns": cols,
                "rows": report_rows,
                "total_matches": len(report_rows),
                "message": f"Accounts where Go Live Target was modified in the last {days} day(s): {len(report_rows)} row(s). Query uses cell history (same as terminal report).",
            }
        except Exception as e:
            return {"type": "text", "content": f"Could not run go-live-modified report: {e}. Try running the terminal report: python go_live_modified_report.py --days {days}."}
    if use_llm and _get_openai_key():
        text = answer_with_openai(column_names, rows, question, sheet_name)
        if "Falling back" not in text and "OPENAI_API_KEY not set" not in text and "token expired" not in text:
            return {"type": "text", "content": text}
    return _keyword_search_structured(column_names, rows, question)
