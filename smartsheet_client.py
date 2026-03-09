"""
Smartsheet API client. Fetches sheet metadata and rows.
Requires: SMARTSHEET_ACCESS_TOKEN and SMARTSHEET_SHEET_ID (env or .env).
"""

import os
from typing import Any

# .env is loaded by smartsheet_app.py from the project folder (with override).
# Do not load_dotenv() here, or a .env in the shell cwd could override project .env.

import requests

API_BASE = "https://api.smartsheet.com/2.0"


def _strip_quotes(s: str) -> str:
    """Remove optional surrounding quotes from env value."""
    s = s.strip()
    if (len(s) >= 2 and s[0] == s[-1] and s[0] in '"\''):
        return s[1:-1].strip()
    return s


def get_client_config() -> tuple[str, str]:
    """Get access token and sheet ID from environment."""
    token = _strip_quotes(os.environ.get("SMARTSHEET_ACCESS_TOKEN", ""))
    sheet_id = _strip_quotes(os.environ.get("SMARTSHEET_SHEET_ID", ""))
    if not token:
        raise ValueError(
            "SMARTSHEET_ACCESS_TOKEN is not set. "
            "Add it to your environment or a .env file in the project folder."
        )
    if not sheet_id:
        raise ValueError(
            "SMARTSHEET_SHEET_ID is not set. "
            "Add it to your environment or a .env file in the project folder."
        )
    # Catch common placeholder so we give a clear error
    if sheet_id.lower() in ("your_sheet_id", "your sheet id", "<sheet_id>"):
        raise ValueError(
            "SMARTSHEET_SHEET_ID is still the placeholder 'your_sheet_id'. "
            "Replace it with your real sheet ID from the sheet URL: "
            "https://app.smartsheet.com/sheets/XXXXXXXX  → use the XXXXXXXXX part. "
            "Edit the .env file in this project folder: same folder as smartsheet_app.py"
        )
    return token, sheet_id


def get_sheet(sheet_id: str | None = None, access_token: str | None = None) -> dict[str, Any]:
    """
    Fetch a sheet with all columns and rows (including cell values).
    Uses env SMARTSHEET_SHEET_ID and SMARTSHEET_ACCESS_TOKEN if not passed.
    """
    if access_token is None or sheet_id is None:
        token, sid = get_client_config()
        access_token = access_token or token
        sheet_id = sheet_id or sid

    url = f"{API_BASE}/sheets/{sheet_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


def sheet_to_table(sheet: dict[str, Any]) -> tuple[list[str], list[dict[str, Any]]]:
    """
    Convert Smartsheet sheet response to a simple table: (column_names, list of row dicts).
    Column names are taken from the first row if it looks like a header, else from column titles.
    """
    columns = sheet.get("columns", [])
    col_id_to_title = {c["id"]: (c.get("title") or f"Column_{c['id']}") for c in columns}
    col_order = [c["id"] for c in columns]
    column_names = [col_id_to_title[cid] for cid in col_order]

    rows = []
    for row in sheet.get("rows", []):
        cell_map = {c["columnId"]: c.get("value") for c in row.get("cells", [])}
        row_dict = {col_id_to_title[cid]: cell_map.get(cid) for cid in col_order}
        rows.append(row_dict)

    return column_names, rows


def get_sheet_with_mod_dates(sheet_id: str | None = None, access_token: str | None = None) -> dict[str, Any]:
    """
    Same as get_sheet(); the raw API response includes rows[].modifiedAt (ISO 8601 string).
    Use this when you need to filter by when a row was last modified.
    """
    return get_sheet(sheet_id=sheet_id, access_token=access_token)


def get_cell_history(
    sheet_id: int | str,
    row_id: int,
    column_id: int,
    access_token: str,
    page: int = 1,
    page_size: int = 1,
) -> dict[str, Any]:
    """
    Get modification history for a single cell.
    Cell History API requires numeric IDs. Pass sheet_id from sheet["id"] (numeric)
    in the GET sheet response, not the URL token. Row and column IDs from the
    sheet response are already numeric.
    Rate limit: 30 requests/minute per token. Use page_size=1, page=1 for latest change.
    """
    # Ensure numeric for path (Cell History endpoint requires numeric sheet/row/column IDs)
    sid = int(sheet_id) if isinstance(sheet_id, str) and sheet_id.isdigit() else sheet_id
    url = f"{API_BASE}/sheets/{sid}/rows/{row_id}/columns/{column_id}/history"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    params = {"page": page, "pageSize": page_size}
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()
