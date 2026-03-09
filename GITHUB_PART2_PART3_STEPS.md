# Step-by-step: Part 2 & Part 3 (GitHub push & future updates)

Use this as a checklist. Do Part 2 once to get your code on GitHub; use Part 3 whenever you change code and want to update GitHub.

**Before Part 2:** You must have already created an **empty** repo on GitHub (Part 1) and have its URL, e.g. `https://github.com/YOUR_USERNAME/YOUR_REPO.git`.

---

## Part 2: Put your project on GitHub (first time only)

Do these steps in order in **PowerShell**. Replace `YOUR_USERNAME` and `YOUR_REPO` with your real GitHub username and repository name.

---

### Step 1 — Open PowerShell in your project folder

1. Press **Win + X** and choose **Windows PowerShell** (or **Terminal**), or search for “PowerShell” and open it.
2. Type this and press **Enter** (use your actual path if different):

   ```
   cd "c:\Users\amit.das1\OneDrive - JLL\Documents\Personal\Demo"
   ```

---

### Step 2 — Check if Git is set up

3. Type and press **Enter**:

   ```
   git status
   ```

4. Look at the result:
   - If it says **“not a git repository”** → go to **Step 3**.
   - If it lists files or says “nothing to commit” → skip Step 3 and go to **Step 4**.

---

### Step 3 — Turn this folder into a Git repo (only if Step 2 said “not a git repository”)

5. Type and press **Enter**:

   ```
   git init
   ```

   You should see: “Initialized empty Git repository in …”

---

### Step 4 — Stage all files (and check .env is not included)

6. Type and press **Enter**:

   ```
   git add .
   ```

7. Type and press **Enter**:

   ```
   git status
   ```

8. Look at the list under “Changes to be committed”:
   - You **should** see: `app_streamlit.py`, `summary.py`, `requirements.txt`, `.gitignore`, etc.
   - You must **not** see: `.env`
   - If you **do** see `.env**, stop. Open `.gitignore`, add a new line with just `.env`, save. Then run `git add .` and `git status` again until `.env` is no longer in the list.

---

### Step 5 — Create the first commit

9. Type and press **Enter** (you can change the message in quotes):

   ```
   git commit -m "Add Smartsheet Q&A Streamlit app"
   ```

10. If Git says **“Please tell me who you are”**:
    - Run these two lines (use your real name and email):

      ```
      git config --global user.name "Your Name"
      git config --global user.email "your.email@example.com"
      ```

    - Then run the `git commit` command from Step 9 again.

11. You should see something like “X files changed” and “1 file changed” — that’s correct.

---

### Step 6 — Name the branch `main`

12. Type and press **Enter**:

    ```
    git branch -M main
    ```

    (Nothing will print; that’s normal.)

---

### Step 7 — Connect this folder to your GitHub repo

13. Type and press **Enter** — **replace YOUR_USERNAME and YOUR_REPO** with your GitHub username and repo name:

    ```
    git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
    ```

    Example: if username is `johndoe` and repo is `smartsheet-qa-app`:

    ```
    git remote add origin https://github.com/johndoe/smartsheet-qa-app.git
    ```

14. If it says **“remote origin already exists”** and the URL is wrong, run:

    ```
    git remote remove origin
    ```

    Then run the `git remote add origin ...` line again with the correct URL.

---

### Step 8 — Push your code to GitHub

15. Type and press **Enter**:

    ```
    git push -u origin main
    ```

16. If a browser or window opens asking you to **sign in to GitHub**:
    - Sign in with your GitHub account, or
    - If it asks for a **password**, use a **Personal Access Token** (not your GitHub password).  
      To create one: GitHub.com → your profile picture → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)** → **Generate new token** → tick **repo** → Generate → copy the token and paste it when Git asks for a password.

17. Wait until you see something like:

    ```
    To https://github.com/YOUR_USERNAME/YOUR_REPO.git
     * [new branch]      main -> main
    ```

    Part 2 is done.

---

### Step 9 — Check on GitHub

18. Open your browser and go to: `https://github.com/YOUR_USERNAME/YOUR_REPO` (use your username and repo name).
19. You should see your files: `app_streamlit.py`, `summary.py`, `requirements.txt`, etc.
20. Confirm **`.env`** is **not** in the list. If it is, add `.env` to `.gitignore`, then run: `git add .` → `git commit -m "Remove .env from tracking"` → `git push`.

---

## Part 3: Update GitHub after you change code (every time you want to push changes)

Do this whenever you’ve edited files and want to update the repo on GitHub. Run these in **PowerShell** from your project folder.

---

### Step 1 — Go to your project folder

1. Open **PowerShell**.
2. Run:

   ```
   cd "c:\Users\amit.das1\OneDrive - JLL\Documents\Personal\Demo"
   ```

   (Use your actual path if different.)

---

### Step 2 — Stage your changes

3. Run:

   ```
   git add .
   ```

4. Run:

   ```
   git status
   ```

5. Check the list:
   - You should see the files you changed (e.g. `summary.py`, `app_streamlit.py`).
   - You must **not** see `.env`. If you do, fix `.gitignore` and run `git add .` again.

---

### Step 3 — Create a commit with a short description

6. Run (change the message to describe what you did):

   ```
   git commit -m "Short description of what you changed"
   ```

   Examples:
   - `git commit -m "Update summary logic"`
   - `git commit -m "Fix region filter in prompt"`
   - `git commit -m "Add new script for weekly email"`

7. You should see “X files changed” — that’s correct.

---

### Step 4 — Push to GitHub

8. Run:

   ```
   git push
   ```

9. If asked, sign in or use your Personal Access Token (same as in Part 2).
10. When it finishes, your changes are on GitHub. If you use Streamlit Cloud, it will redeploy from the updated repo.

---

## Quick copy-paste (Part 2 — first time)

Replace `YOUR_USERNAME` and `YOUR_REPO`, then run **one block at a time** in PowerShell (from your project folder). Skip `git init` if `git status` already shows a repo.

```powershell
cd "c:\Users\amit.das1\OneDrive - JLL\Documents\Personal\Demo"
```

```powershell
git init
```

```powershell
git add .
git status
```

```powershell
git commit -m "Add Smartsheet Q&A Streamlit app"
```

```powershell
git branch -M main
```

```powershell
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
```

```powershell
git push -u origin main
```

---

## Quick copy-paste (Part 3 — every update)

Run from your project folder after you’ve made changes:

```powershell
cd "c:\Users\amit.das1\OneDrive - JLL\Documents\Personal\Demo"
git add .
git status
git commit -m "Short description of what you changed"
git push
```

Replace `"Short description of what you changed"` with your own message each time.
