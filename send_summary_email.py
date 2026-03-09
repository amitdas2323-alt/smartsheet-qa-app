"""
Send the Smartsheet executive summary to a list of emails.

Usage:
  python send_summary_email.py              # Send once now
  python send_summary_email.py --dry-run    # Build summary and print, do not send

Requires in .env (in addition to Smartsheet vars):
  SMTP_HOST              e.g. smtp.office365.com or smtp.gmail.com
  SMTP_PORT              e.g. 587
  SMTP_USER              your email / username
  SMTP_PASSWORD          your password or app password
  SUMMARY_RECIPIENTS     comma-separated emails (e.g. a@jll.com, b@jll.com)
  SUMMARY_FROM_EMAIL     (optional) From address; defaults to SMTP_USER
"""

import os
import sys
from pathlib import Path

_project_dir = Path(__file__).resolve().parent
_env_file = _project_dir / ".env"
try:
    from dotenv import load_dotenv
    load_dotenv(_env_file, override=True)
except ImportError:
    pass

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import Counter

from smartsheet_client import get_sheet, sheet_to_table, get_client_config
from summary import build_executive_summary


def get_email_config():
    """Read SMTP and recipient settings from environment."""
    host = os.environ.get("SMTP_HOST", "").strip()
    port_str = os.environ.get("SMTP_PORT", "587").strip()
    user = os.environ.get("SMTP_USER", "").strip()
    password = os.environ.get("SMTP_PASSWORD", "").strip()
    recipients_str = os.environ.get("SUMMARY_RECIPIENTS", "").strip()
    from_email = os.environ.get("SUMMARY_FROM_EMAIL", "").strip() or user

    if not host or not user or not password:
        raise ValueError(
            "Set SMTP_HOST, SMTP_USER, and SMTP_PASSWORD in .env to send email. "
            "See .env.example."
        )
    recipients = [r.strip() for r in recipients_str.split(",") if r.strip()]
    if not recipients:
        raise ValueError("Set SUMMARY_RECIPIENTS in .env (comma-separated emails).")

    try:
        port = int(port_str)
    except ValueError:
        port = 587

    return {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "from_email": from_email,
        "recipients": recipients,
    }


def build_summary_with_status(column_names, rows, sheet_name):
    """Executive summary text plus a short status snapshot for the email."""
    full = build_executive_summary(column_names, rows, sheet_name=sheet_name)
    status_col = "Baseline: Overall Status"
    if status_col in column_names:
        counts = Counter(str(r.get(status_col, "")).strip() for r in rows if r.get(status_col))
        lines = ["\n## Status snapshot (Baseline: Overall Status)\n"]
        for status, count in counts.most_common():
            if status:
                lines.append(f"  • {status}: {count}")
        snapshot = "\n".join(lines)
        # Insert snapshot after "Total rows" / "Columns" and before "## Column overview"
        if "## Column overview" in full:
            full = full.replace(
                "## Column overview",
                snapshot + "\n\n## Column overview",
                1,
            )
    return full


def send_summary_email(dry_run: bool = False) -> None:
    """Fetch sheet, build summary, and send to SUMMARY_RECIPIENTS (or dry-run print)."""
    get_client_config()
    sheet = get_sheet()
    column_names, rows = sheet_to_table(sheet)
    sheet_name = sheet.get("name", "Smartsheet")

    body = build_summary_with_status(column_names, rows, sheet_name)
    subject = f"Weekly project summary — {sheet_name}"

    if dry_run:
        print("=== DRY RUN: would send the following ===\n")
        print(f"Subject: {subject}\n")
        print(body)
        return

    cfg = get_email_config()
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = cfg["from_email"]
    msg["To"] = ", ".join(cfg["recipients"])
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP(cfg["host"], cfg["port"]) as server:
            server.starttls()
            server.login(cfg["user"], cfg["password"])
            server.sendmail(cfg["from_email"], cfg["recipients"], msg.as_string())
        print(f"Summary email sent to {len(cfg['recipients'])} recipient(s).")
    except Exception as e:
        print(f"Failed to send email: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    send_summary_email(dry_run=dry_run)
