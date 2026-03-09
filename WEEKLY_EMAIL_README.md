# Weekly project summary email

The summary of your Smartsheet (executive summary + status snapshot) can be sent to a list of emails once every week.

## 1. Configure email in `.env`

Add these variables (copy from `.env.example` if needed):

```env
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USER=your_email@jll.com
SMTP_PASSWORD=your_password_or_app_password
SUMMARY_RECIPIENTS=manager1@jll.com,manager2@jll.com
```

- **Office 365 / Outlook:** `SMTP_HOST=smtp.office365.com`, `SMTP_PORT=587`. Use your normal password or an app password if you have MFA.
- **Gmail:** `SMTP_HOST=smtp.gmail.com`, `SMTP_PORT=587`, and use an [App Password](https://support.google.com/accounts/answer/185833) for `SMTP_PASSWORD`.

Optional: `SUMMARY_FROM_EMAIL` if you want the "From" address to differ from `SMTP_USER`.

## 2. Send once (test)

```bash
python send_summary_email.py --dry-run   # Build and print only, no send
python send_summary_email.py             # Send now
```

## 3. Run every week

**Option A – Python scheduler (script stays running)**

```bash
pip install schedule
python run_weekly_summary.py             # Every Monday 09:00
python run_weekly_summary.py --day fri --time 8:30   # Every Friday 08:30
```

Keep the terminal or process running (e.g. on a server or VM).

**Option B – Windows Task Scheduler (recommended on a single PC)**

1. Open **Task Scheduler** → Create Basic Task.
2. **Trigger:** Weekly, choose day and time (e.g. Monday 9:00 AM).
3. **Action:** Start a program.
   - **Program:** `python` (or full path to your Python executable).
   - **Arguments:** `"C:\...\Demo\send_summary_email.py"` (full path to the script).
   - **Start in:** `C:\...\Demo` (folder containing `.env` and the script).
4. Finish and test by right‑clicking the task → Run.

Replace `C:\...\Demo` with your actual project path, e.g.  
`C:\Users\amit.das1\OneDrive - JLL\Documents\Personal\Demo`.
