# Sharing the Streamlit app with other users

Other users only need a browser; they don’t need Python, Smartsheet tokens, or API keys. You choose how to expose the app.

---

## Option 1: Same network (quick, no account)

**Best for:** Colleagues on the same Wi‑Fi or office network.

1. On your PC, start the app so it listens on all interfaces:
   ```bash
   cd "c:\Users\amit.das1\OneDrive - JLL\Documents\Personal\Demo"
   python -m streamlit run app_streamlit.py --server.address 0.0.0.0
   ```
   Or double‑click **`run_web_app.bat`** (it already uses `--server.address 0.0.0.0`).

2. Find your PC’s IP (PowerShell: `ipconfig` → **IPv4 Address**).

3. Share this URL with others: **`http://YOUR_IP:8501`**  
   Example: `http://192.168.1.50:8501`

4. They open that URL in a browser and can type questions.  
   **Note:** Your PC must stay on and the app running; firewall may need to allow port 8501.

---

## Option 2: Streamlit Community Cloud (free, public or private)

**Best for:** Sharing over the internet without maintaining a server.

1. **Push your app to GitHub** (create a repo, push this folder; **do not commit `.env`**).

2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub, and click **“New app”**.

3. Choose your repo, branch, and file: **`app_streamlit.py`**.

4. **Add secrets** (replaces your `.env` on Streamlit’s servers):
   - In the app page: **Settings → Secrets**
   - Paste (one per line, no quotes):
     ```
     SMARTSHEET_ACCESS_TOKEN=your_actual_token
     SMARTSHEET_SHEET_ID=your_sheet_id
     OPENAI_API_KEY=your_openai_key
     ```

5. Deploy. Streamlit gives you a URL like `https://your-app-name.streamlit.app`. Share that link; users open it and can prompt.

6. **Privacy:** You can set the app to **private** so only people you invite can see it (Streamlit account required for them).

---

## Option 3: Company server or VM (intranet/VPN)

**Best for:** Internal use on a shared machine (e.g. Windows Server, Linux VM).

1. Copy the project (including `.env`) to the server. **Do not commit `.env` to Git.**

2. Install Python and dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run Streamlit so it’s reachable (e.g. on port 8501):
   ```bash
   python -m streamlit run app_streamlit.py --server.address 0.0.0.0 --server.port 8501
   ```

4. Optionally run it as a service (Windows: NSSM / Task Scheduler; Linux: systemd) so it restarts after reboot.

5. Share the URL: **`http://SERVER_HOSTNAME:8501`** (or whatever port). Users on the same VPN/intranet can open it and prompt.

---

## Option 4: Temporary public URL (e.g. ngrok) for demos

**Best for:** Quick demos to people outside your network without deploying to the cloud.

1. Install [ngrok](https://ngrok.com) and create a free account.

2. Start your app locally:
   ```bash
   python -m streamlit run app_streamlit.py
   ```

3. In another terminal:
   ```bash
   ngrok http 8501
   ```

4. ngrok shows a public URL (e.g. `https://abc123.ngrok.io`). Share that; when you stop ngrok, the URL stops working.

---

## Summary

| Option              | Who can use it              | Needs                    |
|---------------------|-----------------------------|--------------------------|
| Same network        | Same Wi‑Fi/LAN              | Your PC on, port 8501    |
| Streamlit Cloud     | Anyone with the link        | GitHub repo + secrets    |
| Company server      | Intranet/VPN users          | Server + .env            |
| ngrok               | Anyone (temporary)          | ngrok account, app running |

**Security:** Never commit `.env` or paste tokens into public repos. Use Streamlit’s Secrets (Option 2) or env vars on the server (Option 3).
