"""
Run the project summary email once every week (e.g. Monday 9:00 AM).

Usage:
  python run_weekly_summary.py              # Default: every Monday at 09:00
  python run_weekly_summary.py --day fri --time 8:30   # Every Friday at 08:30
  python run_weekly_summary.py --once                  # Send once and exit (for testing)

Keep this script running (e.g. in a dedicated terminal or as a background service).
Alternatively, use Windows Task Scheduler to run send_summary_email.py weekly (see README).
"""

import argparse
import sys
from pathlib import Path

_project_dir = Path(__file__).resolve().parent
_env_file = _project_dir / ".env"
try:
    from dotenv import load_dotenv
    load_dotenv(_env_file, override=True)
except ImportError:
    pass

try:
    import schedule
except ImportError:
    print("Install schedule: pip install schedule", file=sys.stderr)
    sys.exit(1)


def job():
    from send_summary_email import send_summary_email
    send_summary_email(dry_run=False)


def main():
    parser = argparse.ArgumentParser(description="Send weekly project summary email.")
    parser.add_argument("--once", action="store_true", help="Send once and exit")
    parser.add_argument("--day", default="mon", help="Day: mon, tue, wed, thu, fri, sat, sun (default: mon)")
    parser.add_argument("--time", default="09:00", help="Time HH:MM (default: 09:00)")
    args = parser.parse_args()

    if args.once:
        job()
        return

    day = args.day.lower()[:3]
    if day not in ("mon", "tue", "wed", "thu", "fri", "sat", "sun"):
        print("--day must be mon, tue, wed, thu, fri, sat, or sun", file=sys.stderr)
        sys.exit(1)

    getattr(schedule.every(), day).at(args.time).do(job)
    print(f"Scheduled: every {day} at {args.time}. Waiting... (Ctrl+C to stop)")
    while True:
        schedule.run_pending()
        import time
        time.sleep(60)


if __name__ == "__main__":
    main()
