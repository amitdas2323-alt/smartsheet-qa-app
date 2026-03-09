# GitHub steps — elaborate guide

This guide walks you through putting your Demo project on GitHub so you can deploy it to Streamlit Cloud (or just keep a backup and share code). Everything is step-by-step with explanations.

---

## Prerequisites

- **Git** installed on your PC. To check, open PowerShell and run:
  ```powershell
  git --version
  ```
  If you see a version number (e.g. `git version 2.43.0`), you’re good. If not, install from [git-scm.com](https://git-scm.com/download/win).

- **A GitHub account.** If you don’t have one, go to [github.com](https://github.com) and sign up (free).

---

## Part 1: Create a new repository on GitHub (in the browser)

You first create an **empty** repo on GitHub. You will push your local folder into it in Part 2.

### Step 1.1 — Log in and start creating a repo

1. Go to **[github.com](https://github.com)** and sign in.
2. In the top-right, click the **+** (plus) and choose **“New repository”**.

### Step 1.2 — Fill in the repository details

1. **Repository name**  
   Choose a short name, e.g. `smartsheet-qa-app` or `demo-streamlit`.  
   - Use letters, numbers, and hyphens.  
   - This will be part of the URL: `https://github.com/YOUR_USERNAME/REPO_NAME`.

2. **Description (optional)**  
   e.g. “Smartsheet Q&A web app with Streamlit”.

3. **Public**  
   Leave it as **Public** so Streamlit Cloud can read the repo. (You can make the *app* private in Streamlit later.)

4. **Do NOT add anything else**  
   - **Do not** check “Add a README file”.  
   - **Do not** add a .gitignore or license.  
   You already have a .gitignore and other files locally; adding these on GitHub would create a different starting history and complicate the first push.

5. Click **“Create repository”**.

### Step 1.3 — Copy the repo URL

After the repo is created, GitHub shows a page with setup instructions. You’ll see a URL like:

- **HTTPS:** `https://github.com/YOUR_USERNAME/YOUR_REPO.git`  
  Example: `https://github.com/johndoe/smartsheet-qa-app.git`

Copy that **HTTPS** URL (you’ll use it in Part 2). Replace `YOUR_USERNAME` and `YOUR_REPO` in the commands below with your actual username and repository name.

---

## Part 2: Put your local project on GitHub (in PowerShell)

You’ll do this from the folder that contains your app (`app_streamlit.py`, `summary.py`, `.env`, etc.).

### Step 2.1 — Open PowerShell in your project folder

1. Open **PowerShell** (or Windows Terminal).
2. Go to your project folder. For example:
   ```powershell
   cd "c:\Users\amit.das1\OneDrive - JLL\Documents\Personal\Demo"
   ```
   If your path is different, use your actual path in quotes.

### Step 2.2 — Check if Git is already initialized

Run:

```powershell
git status
```

- If you see **“not a git repository”** (or similar), go to **Step 2.3**.
- If you see a list of files or “nothing to commit”, Git is already set up; skip Step 2.3 and go to **Step 2.4**.

### Step 2.3 — Initialize a new Git repository (only if needed)

Run:

```powershell
git init
```

**What this does:** Creates a hidden `.git` folder in your project. Git will now track changes in this folder. Your files are not on GitHub yet; they’re only tracked locally.

### Step 2.4 — Make sure .env is ignored

Run:

```powershell
git add .
git status
```

**What this does:**  
- `git add .` stages all files that are **not** in `.gitignore`.  
- `git status` shows what will be included in the next commit.

**Check the list:**  
- You should **see** files like `app_streamlit.py`, `summary.py`, `requirements.txt`, `.gitignore`, etc.  
- You must **not** see `.env` in the list.  
  If `.env` appears, it would be pushed to GitHub and your secrets would be exposed. In that case:
  1. Open `.gitignore` and ensure it contains a line: `.env`
  2. Run: `git add .` and `git status` again.  
  `.env` should no longer appear.

### Step 2.5 — Create the first commit

Run:

```powershell
git commit -m "Add Smartsheet Q&A Streamlit app"
```

**What this does:** Saves a snapshot of all staged files as one “commit” in your local repo. The message in quotes is just a label for this snapshot. Nothing has been sent to GitHub yet.

If Git asks you to set your name and email (first time only), run:

```powershell
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

Then run the `git commit` command again.

### Step 2.6 — Rename the branch to `main` (if needed)

Git sometimes names the default branch `master`. Streamlit Cloud usually expects `main`. Run:

```powershell
git branch -M main
```

**What this does:** Renames your current branch to `main`. You only need to do this once.

### Step 2.7 — Connect your local repo to GitHub

Run (replace `YOUR_USERNAME` and `YOUR_REPO` with the repo you created in Part 1):

```powershell
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
```

**Example:**  
If your username is `johndoe` and repo is `smartsheet-qa-app`:

```powershell
git remote add origin https://github.com/johndoe/smartsheet-qa-app.git
```

**What this does:** Registers the GitHub repo URL under the name `origin`. When you push, Git will send your commits to this URL.

If you get **“remote origin already exists”**, you already added it. You can check with:

```powershell
git remote -v
```

If the URL is wrong, remove and re-add:

```powershell
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
```

### Step 2.8 — Push your code to GitHub

Run:

```powershell
git push -u origin main
```

**What this does:**  
- Sends your local `main` branch (and its commits) to GitHub.  
- `-u origin main` sets `origin main` as the default upstream, so later you can just use `git push`.

**First time:**  
- A browser or a popup may open and ask you to **log in to GitHub** (or use a **Personal Access Token**).  
- If GitHub asks for a **password**, use a **Personal Access Token**, not your account password. To create one: GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)** → **Generate new token**. Give it at least the `repo` scope and paste it when Git asks for a password.

When the push succeeds, you’ll see something like:

```
Enumerating objects: 25, done.
...
To https://github.com/YOUR_USERNAME/YOUR_REPO.git
 * [new branch]      main -> main
```

### Step 2.9 — Verify on GitHub

1. Open your repo in the browser: `https://github.com/YOUR_USERNAME/YOUR_REPO`
2. You should see all your project files (e.g. `app_streamlit.py`, `summary.py`, `requirements.txt`, `.gitignore`).
3. Confirm that **`.env`** is **not** there. If it is, remove it from the repo and add `.env` to `.gitignore`, then commit and push again.

---

## Part 3: After the first push — making future updates

When you change code and want to update GitHub:

```powershell
cd "c:\Users\amit.das1\OneDrive - JLL\Documents\Personal\Demo"
git add .
git status
git commit -m "Short description of what you changed"
git push
```

- **`git add .`** — stage all changes (respecting `.gitignore`).  
- **`git status`** — double-check that `.env` is not staged.  
- **`git commit -m "..."`** — create a new snapshot.  
- **`git push`** — send the new commit(s) to GitHub.

---

## Quick reference — copy-paste block

Replace `YOUR_USERNAME` and `YOUR_REPO`, then run in order (only run `git init` if the folder is not yet a Git repo):

```powershell
cd "c:\Users\amit.das1\OneDrive - JLL\Documents\Personal\Demo"
git init
git add .
git status
git commit -m "Add Smartsheet Q&A Streamlit app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

---

## Next step

Once the repo is on GitHub, follow **STREAMLIT_CLOUD.md** to deploy the app: connect the repo at [share.streamlit.io](https://share.streamlit.io), set the main file to `app_streamlit.py`, and add your secrets.
