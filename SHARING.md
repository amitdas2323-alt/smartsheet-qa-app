# Sharing the Smartsheet summary & prompt with other users

Other users can prompt on the same Smartsheet data in two ways.

---

## Option 1: Each user runs the app (recommended)

**Best for:** Teams where everyone has (or can get) access to the sheet and is okay using a terminal or PyCharm.

### What to share

- **The project folder** (or a repo): all the `.py` files, `requirements.txt`, `.env.example`.  
- **Do not share your `.env`** (it contains your secret API token).

### What each user does

1. **Get access to the sheet**  
   You share the Smartsheet with them (or they’re already in the same workspace), so they can open it in Smartsheet.

2. **Create their own API token**  
   In Smartsheet: **Account (profile) → Personal settings → API Access → Generate new access token.**  
   Each person uses their own token (no need to share yours).

3. **Get the sheet ID**  
   Same for everyone: open the sheet in the browser; the URL is  
   `https://app.smartsheet.com/sheets/XXXXXXXX`  
   The `XXXXXXXX` part is the sheet ID (e.g. you can put it in a team doc or in `.env.example` as a hint).

4. **Set up the project**  
   - Copy the project to their machine (or clone the repo).  
   - Copy `.env.example` to `.env`.  
   - In `.env`, set:  
     - `SMARTSHEET_ACCESS_TOKEN` = their own token  
     - `SMARTSHEET_SHEET_ID` = the shared sheet ID  
   - Optional: `OPENAI_API_KEY` for natural-language answers.

5. **Install and run**  
   ```bash
   pip install -r requirements.txt
   python smartsheet_app.py summary
   python smartsheet_app.py prompt "How many accounts are on track?"
   ```

**Summary:** Same code, same sheet ID; each user has their own token and runs the app on their machine.

---

## Option 2: One shared web app (browser only)

**Best for:** Users who shouldn’t install Python or see tokens; one person or team hosts the app.

You run a small web UI (e.g. Streamlit) on a server or your PC. You put the token and sheet ID in `.env` on that machine only. Others open a URL in the browser and type questions—no Python or token on their side.

### Steps (host side)

1. On the machine that will run the app: ensure `.env` has `SMARTSHEET_ACCESS_TOKEN`, `SMARTSHEET_SHEET_ID`, and optionally `OPENAI_API_KEY`.  
2. Install and run:  
   ```bash
   pip install -r requirements.txt
   streamlit run app_streamlit.py
   ```  
3. Share the URL with others (e.g. `http://localhost:8501`, or your server URL if you deploy it). They can type questions in the browser—no Python or token on their side.

**Security:** Only use on a trusted network or add authentication if you expose it beyond your team.

---

## Quick reference for Option 1

| Item | Who sets it | Notes |
|------|-------------|--------|
| Code / project | You share (repo or folder) | Don’t share `.env` |
| Sheet access | You (or admin) share sheet in Smartsheet | So they can open the sheet |
| Sheet ID | Same for everyone | From sheet URL |
| `SMARTSHEET_ACCESS_TOKEN` | Each user | Their own token from Smartsheet → API Access |
| `OPENAI_API_KEY` | Optional, per user | For better prompt answers |

The project includes `app_streamlit.py` for Option 2.
