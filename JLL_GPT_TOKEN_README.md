# JLL GPT token (OPENAI_API_KEY) and refresh

If you use the **JLL GPT JWT** as `OPENAI_API_KEY`, it expires in about **59 minutes**. The app will then fall back to keyword search until you provide a new token or set up refresh.

---

## Option 1: Update the token manually

- When the LLM stops working, get a new JWT from [JLL GPT](https://ai-uat.jll.com/developer-sandbox) (“Get your JWT”) and update:
  - **Locally:** `.env` → `OPENAI_API_KEY=new_jwt`
  - **Streamlit Cloud:** App → **Settings** → **Secrets** → update `OPENAI_API_KEY`
- No code changes; you just refresh the secret every hour.

---

## Option 2: Automatic token refresh (recommended)

The app supports **automatic refresh** so you don’t have to update secrets every hour.

1. **Get refresh details from JLL**
   - Open the [JLL GPT developer sandbox](https://ai-uat.jll.com/developer-sandbox).
   - Log in and find the **“Long-running code with token refresh”** section (or equivalent) in the code samples/docs.
   - Note:
     - **Token URL** (endpoint to get/refresh the access token)
     - Either **client ID + client secret** (client_credentials), or a **refresh token** (refresh_token grant).

2. **Configure the app**
   - **Locally:** add to `.env`.
   - **Streamlit Cloud:** add to **Settings** → **Secrets** (same names, one per line in TOML).

   **If using client credentials:**
   ```env
   JLL_GPT_TOKEN_URL=https://...   # URL from JLL docs
   JLL_GPT_CLIENT_ID=...
   JLL_GPT_CLIENT_SECRET=...
   ```
   (Keep `OPENAI_API_KEY` as the current JWT; the app will replace it with a refreshed token when it expires.)

   **If using a refresh token:**
   ```env
   JLL_GPT_TOKEN_URL=https://...
   JLL_GPT_REFRESH_TOKEN=...
   ```

3. **Behaviour**
   - The app decodes the JWT and checks expiry.
   - If the token is expired or expiring within 5 minutes, it calls `JLL_GPT_TOKEN_URL` to get a new token (using client credentials or refresh token).
   - If refresh succeeds, the LLM keeps working without you updating secrets.

If the JLL sandbox uses different parameter names or a different flow, adapt the env vars to match (e.g. different URL or extra fields); the app uses `access_token` / `accessToken` / `token` from the JSON response.

---

## How it’s implemented

- **`jll_gpt_token.py`** – reads JWT `exp`, detects expiry, and (if configured) calls the token URL to refresh.
- **`prompt_on_data.py`** – uses `get_effective_openai_key()` so the LLM gets a valid key or the app falls back to keyword search.

No need to update secrets every hour if refresh is configured; only if you switch to a different key or JLL changes the refresh flow.
