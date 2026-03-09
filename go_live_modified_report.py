"""
List accounts where the Baseline Go Live Target cell was modified in the last N days.

Uses Smartsheet Cell History API. The API requires the sheet's numeric ID (from the
GET sheet response), not the URL token—so we fetch the sheet first and use sheet["id"].

Usage:
  python go_live_modified_report.py           # Last 7 days
  python go_live_modified_report.py --days 1  # Last 1 day

Rate limit: 30 cell-history requests per minute; the script throttles automatically.
"""

import sys
import time
from pathlib import Path
from datetime import datetime, timezone, timedelta

_project_dir = Path(__file__).resolve().parent
_env_file = _project_dir / ".env"
try:
    from dotenv import load_dotenv
    load_dotenv(_env_file, override=True)
except ImportError:
    pass

from smartsheet_client import get_sheet, get_cell_history, get_client_config


def cell_val(row, col_id):
    for cell in row.get("cells", []):
        if cell.get("columnId") == col_id:
            return cell.get("value")
    return None


def parse_dt(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return datetime.fromtimestamp(v / 1000.0, tz=timezone.utc)
    try:
        return datetime.fromisoformat(str(v).replace("Z", "+00:00"))
    except Exception:
        return None


def get_go_live_modified_report(days: int = 7) -> list[dict]:
    """
    Returns list of dicts with keys: Account Name, Go Live Target, Modified, Modified by.
    Used by both the CLI script and the web app so results match exactly.
    Rate limit: ~2.1s per row with Go Live Target; may take several minutes for large sheets.
    """
    get_client_config()
    sheet = get_sheet()
    token, _ = get_client_config()
    numeric_sheet_id = sheet["id"]
    columns = sheet.get("columns", [])
    name_col_id = target_col_id = None
    for c in columns:
        t = (c.get("title") or "").strip()
        if t == "Account Name":
            name_col_id = c["id"]
        if t == "Baseline Go Live Target":
            target_col_id = c["id"]
    if not target_col_id:
        return []
    rows_to_check = []
    for row in sheet.get("rows", []):
        target_val = cell_val(row, target_col_id)
        if target_val is None or str(target_val).strip() == "":
            continue
        name = cell_val(row, name_col_id)
        rows_to_check.append((row["id"], str(name) if name else "", target_val))
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    result = []
    for i, (row_id, account_name, target_val) in enumerate(rows_to_check):
        if i > 0:
            time.sleep(2.1)
        try:
            hist = get_cell_history(
                numeric_sheet_id, row_id, target_col_id, token, page=1, page_size=1
            )
        except Exception:
            continue
        data = hist.get("data") or []
        if not data:
            continue
        mod_at = data[0].get("modifiedAt")
        dt = parse_dt(mod_at)
        if dt and dt >= cutoff:
            by = data[0].get("modifiedBy") or {}
            modifier = by.get("name") or by.get("email") or "Unknown"
            modifier_email = by.get("email", "")
            who = f"{modifier} ({modifier_email})" if modifier_email else modifier
            result.append({
                "Account Name": account_name,
                "Go Live Target": str(target_val),
                "Modified": dt.strftime("%Y-%m-%d %H:%M"),
                "Modified by": who,
            })
    return sorted(result, key=lambda x: x["Modified"], reverse=True)


def main():
    days = 7
    if "--days" in sys.argv:
        i = sys.argv.index("--days")
        if i + 1 < len(sys.argv):
            try:
                days = int(sys.argv[i + 1])
            except ValueError:
                pass

    result = get_go_live_modified_report(days)
    for row in result:
        print(f"{row['Account Name']} | Go Live Target: {row['Go Live Target']} | Modified: {row['Modified']} | By: {row['Modified by']}")
    print()
    unique_accounts = len(set(r["Account Name"] for r in result))
    print(f"Rows where Go Live Target was modified in the last {days} day(s): {len(result)} ({unique_accounts} unique accounts)")


if __name__ == "__main__":
    main()
