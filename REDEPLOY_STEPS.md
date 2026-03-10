# Step-by-step: Redeploy the Streamlit app (after code changes)

After you change code (e.g. in `prompt_on_data.py`, `app_streamlit.py`), push to the repo that Streamlit Cloud uses. Streamlit will **automatically redeploy** the app. Same URL, updated app.

---

## Step 1 — Open PowerShell in your project folder

1. Open **PowerShell** (or Windows Terminal).
2. Go to your project folder:

   ```powershell
   cd "c:\Users\amit.das1\OneDrive - JLL\Documents\Personal\Demo"
   ```

   (Use your actual path if different.)

---

## Step 2 — Stage your changes

3. Run:

   ```powershell
   git add .
   ```

4. Run:

   ```powershell
   git status
   ```

5. Check the list:
   - You should see the files you changed (e.g. `prompt_on_data.py`).
   - You must **not** see `.env`. If you do, don’t commit it; fix `.gitignore` and run `git add .` again.

---

## Step 3 — Commit

6. Run (change the message if you like):

   ```powershell
   git commit -m "Question-aware columns and 15-column table for prompts"
   ```

   Or any short description of what you changed, e.g.:
   - `git commit -m "Fix column selection for divisional president question"`
   - `git commit -m "Redeploy with latest prompt logic"`

---

## Step 4 — Push to the repo Streamlit uses

7. Push to your **personal** remote (the one connected to Streamlit Cloud):

   ```powershell
   git push personal main
   ```

   If you only have one remote (`origin`) and that’s the one Streamlit uses, use instead:

   ```powershell
   git push origin main
   ```

8. Wait for the command to finish. You should see something like:
   ```text
   To https://github.com/amitdas2323-alt/smartsheet-qa-app.git
      abc1234..def5678  main -> main
   ```

---

## Step 5 — Wait for Streamlit to redeploy

9. Streamlit Cloud detects the new push and **redeploys automatically** (usually 1–3 minutes).
10. Open your app URL (same as before):
    ```text
    https://smartsheet-app-app-tcrf5nmzmi8exvne9e2vzx.streamlit.app
    ```
11. Refresh the page and test (e.g. ask “who is the divisional president for ABB robotics”). You should see the updated behavior.

---

## Quick copy-paste (all steps)

Run these in order in PowerShell from your project folder:

```powershell
cd "c:\Users\amit.das1\OneDrive - JLL\Documents\Personal\Demo"
git add .
git status
git commit -m "Redeploy with latest changes"
git push personal main
```

Then wait 1–3 minutes and refresh your Streamlit app URL.

---

## If something goes wrong

| Issue | What to do |
|-------|------------|
| `git push personal main` says "remote not found" or "repository not found" | Check the remote: `git remote -v`. If you never added `personal`, add it: `git remote add personal https://github.com/amitdas2323-alt/smartsheet-qa-app.git` then push again. |
| Push asks for username/password | Use your GitHub username and a **Personal Access Token** (not your GitHub password). Create one at GitHub → Settings → Developer settings → Personal access tokens. |
| App URL still shows old behavior | Wait a bit longer; redeploy can take a few minutes. Hard-refresh the page (Ctrl+F5) or try in an incognito window. |
| Build failed on Streamlit Cloud | On [share.streamlit.io](https://share.streamlit.io), open your app → check the **Build logs** for the error (e.g. missing dependency). Fix the code or `requirements.txt`, commit, and push again. |
