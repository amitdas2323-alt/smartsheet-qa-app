# Run the shared Smartsheet web app

One person runs the app; everyone else opens the URL in a browser to prompt on the same sheet (no Python or token needed for them).

**More ways to share (same network, Streamlit Cloud, server, ngrok):** see **[SHARE_APP.md](SHARE_APP.md)**.

## 1. On the machine that will host the app

- Ensure **`.env`** is in this folder with:
  - `SMARTSHEET_ACCESS_TOKEN`
  - `SMARTSHEET_SHEET_ID`
  - (Optional) `OPENAI_API_KEY` for better answers

## 2. Install and start

```bash
cd "c:\Users\amit.das1\OneDrive - JLL\Documents\Personal\Demo"
pip install -r requirements.txt
streamlit run app_streamlit.py --server.address 0.0.0.0
```

- **`--server.address 0.0.0.0`** lets other computers on your network open the app (not only localhost).

## 3. Share the URL with others

- **On the same PC:** open **http://localhost:8501**
- **From another PC/phone on the same network:** open **http://YOUR_IP:8501**  
  Replace `YOUR_IP` with this machine’s IP (e.g. in PowerShell: `ipconfig` → IPv4 Address).

They can type questions in the box and use the “Executive summary” section—no install or token on their side.

## 4. Stop the app

In the terminal where it’s running, press **Ctrl+C**.
