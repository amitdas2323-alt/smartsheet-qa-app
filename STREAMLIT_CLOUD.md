# Deploy to Streamlit Community Cloud

Follow these steps to run your Smartsheet Q&A app on Streamlit Cloud so anyone with the link can prompt (no Python or tokens on their side).

---

## 1. Prepare the repo (one-time)

**Detailed GitHub steps (first-time setup, creating repo, push):** see **[GITHUB_STEPS.md](GITHUB_STEPS.md)**.

Your project already has:
- **`.gitignore`** – so `.env` is never committed
- **Secrets support** – the app reads from Streamlit Secrets when deployed

If this folder is not yet a Git repo:

```powershell
cd "c:\Users\amit.das1\OneDrive - JLL\Documents\Personal\Demo"
git init
git add .
git status
```

Confirm that **`.env`** does **not** appear under "Changes to be committed". If it does, fix `.gitignore` and run `git add .` again.

---

## 2. Push to GitHub

1. Create a **new repository** on [github.com](https://github.com) (e.g. `smartsheet-qa-app`). Do **not** add a README or .gitignore there if you already have them locally.

2. Add the remote and push (replace `YOUR_USERNAME` and `YOUR_REPO` with your repo):

   ```powershell
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git branch -M main
   git add .
   git commit -m "Add Smartsheet Q&A Streamlit app"
   git push -u origin main
   ```

---

## 3. Deploy on Streamlit Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)** and sign in with GitHub.

2. Click **"New app"**.

3. Choose:
   - **Repository:** `YOUR_USERNAME/YOUR_REPO`
   - **Branch:** `main`
   - **Main file path:** `app_streamlit.py`

4. Click **"Advanced settings"** and add your **Secrets** (one per line, no quotes). Use the same values as in your local `.env`:

   ```
   SMARTSHEET_ACCESS_TOKEN = "your_actual_smartsheet_token"
   SMARTSHEET_SHEET_ID = "your_sheet_id"
   OPENAI_API_KEY = "your_openai_api_key"
   ```

   Optional: `OPENAI_MODEL = "gpt-4o-mini"` (or another model).

5. Click **"Deploy"**.

Streamlit will build and run the app. When it’s ready, you’ll get a URL like:

`https://your-repo-name-xxxxx.streamlit.app`

Share that link; others can open it and ask questions.

---

## 4. After deployment

- **Update secrets:** In the app’s Streamlit Cloud page → **Settings** → **Secrets**, edit and save. The app will redeploy.
- **Update code:** Push to the same branch; Streamlit will redeploy automatically.
- **Privacy:** In **Settings** you can make the app **private** so only people you invite can access it (they need a Streamlit account).

---

## Troubleshooting

| Issue | What to do |
|-------|------------|
| "SMARTSHEET_ACCESS_TOKEN is not set" | Add the token in **Settings → Secrets** (and redeploy if needed). |
| Build fails on missing package | Add the package to `requirements.txt` and push. |
| App loads but "Cannot load sheet" | Check that `SMARTSHEET_SHEET_ID` in Secrets is the numeric ID from the sheet URL (e.g. `https://app.smartsheet.com/sheets/123456789` → use `123456789`). |
