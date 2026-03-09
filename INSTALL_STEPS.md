# Step 1: Install dependencies (before running the web app)

You only need to do this **once** (or after you add new packages to `requirements.txt`).

## Option A: Using Command Prompt

1. **Open Command Prompt**
   - Press **Win + R**, type `cmd`, press Enter  
   - Or search for "Command Prompt" in the Start menu and open it.

2. **Go to your project folder**
   - Type this (adjust the path if your Demo folder is elsewhere):
   ```text
   cd "c:\Users\amit.das1\OneDrive - JLL\Documents\Personal\Demo"
   ```
   - Press Enter.

3. **Install the required packages**
   - Type:
   ```text
   pip install -r requirements.txt
   ```
   - Press Enter.
   - Wait until it finishes (you should see "Successfully installed ..." for packages like streamlit, requests, etc.).

4. **Done.** You can close the window. Next time, just double‑click `run_web_app.bat` to start the app.

---

## Option B: Using PowerShell

1. **Open PowerShell**
   - Press **Win + X**, then choose **Windows PowerShell** or **Terminal**  
   - Or search for "PowerShell" in the Start menu.

2. **Go to your project folder**
   ```powershell
   Set-Location "c:\Users\amit.das1\OneDrive - JLL\Documents\Personal\Demo"
   ```

3. **Install the required packages**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Done.** You can close the window and use `run_web_app.bat` to start the app.

---

## Option C: From the folder in File Explorer

1. **Open your Demo folder** in File Explorer:  
   `c:\Users\amit.das1\OneDrive - JLL\Documents\Personal\Demo`

2. **Click the address bar** at the top (where the path is shown), type `cmd`, and press Enter.  
   A Command Prompt opens **already in that folder**.

3. **Type and press Enter:**
   ```text
   pip install -r requirements.txt
   ```

4. **Done.** Close the window; use `run_web_app.bat` to start the app.

---

## If you get an error

- **"pip is not recognized"**  
  Python may not be on your PATH. Try:
  ```text
  py -m pip install -r requirements.txt
  ```
  If that works, we can later change the batch file to use `py -m streamlit` instead of `python -m streamlit`.

- **"No module named streamlit"** after running the batch file  
  The `python` used when you double‑click the batch file might be different. Run the same install command in the same way you opened the app (e.g. open CMD, `cd` to the Demo folder, then `pip install -r requirements.txt`), then run `run_web_app.bat` again.
