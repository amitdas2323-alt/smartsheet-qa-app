"""
Executive summary generator for Smartsheet data.
Produces a concise summary suitable for managers.
"""

from typing import Any


def _safe_str(v: Any) -> str:
    if v is None:
        return ""
    return str(v).strip()


def _column_summary(column_name: str, values: list[Any]) -> dict[str, Any]:
    """Basic stats for a column (non-null count, sample of unique values)."""
    non_empty = [_safe_str(v) for v in values if v is not None and str(v).strip()]
    unique = list(dict.fromkeys(non_empty))[:10]
    return {
        "column": column_name,
        "non_empty_count": len(non_empty),
        "sample_values": unique,
    }


def build_executive_summary(
    column_names: list[str],
    rows: list[dict[str, Any]],
    sheet_name: str = "Smartsheet",
    max_highlights: int = 5,
) -> str:
    """
    Build a text executive summary from sheet columns and rows.
    """
    lines = [
        f"# Executive Summary — {sheet_name}",
        "",
        f"**Total rows:** {len(rows)}",
        f"**Columns:** {len(column_names)}",
        "",
        "## Column overview",
        "",
    ]

    for col in column_names:
        values = [r.get(col) for r in rows]
        stats = _column_summary(col, values)
        lines.append(f"- **{stats['column']}**: {stats['non_empty_count']} non-empty values")
        if stats["sample_values"]:
            sample = ", ".join(stats["sample_values"][:5])
            if len(sample) > 80:
                sample = sample[:77] + "..."
            lines.append(f"  Sample: {sample}")
        lines.append("")

    # Numeric-like columns: show min/max/avg if applicable
    numeric_highlights = []
    for col in column_names:
        values = []
        for r in rows:
            v = r.get(col)
            if v is None:
                continue
            try:
                values.append(float(v))
            except (TypeError, ValueError):
                pass
        if values:
            numeric_highlights.append(
                (col, min(values), max(values), sum(values) / len(values), len(values))
            )

    if numeric_highlights:
        lines.append("## Key metrics")
        lines.append("")
        for col, mn, mx, avg, n in numeric_highlights[:max_highlights]:
            lines.append(f"- **{col}**: min={mn}, max={mx}, avg={avg:.2f} (n={n})")
        lines.append("")

    lines.append("---")
    lines.append("*Summary generated from live Smartsheet data.*")
    return "\n".join(lines)


def summary_to_console(column_names: list[str], rows: list[dict[str, Any]], sheet_name: str = "Smartsheet") -> None:
    """Print executive summary to console."""
    text = build_executive_summary(column_names, rows, sheet_name=sheet_name)
    print(text)
