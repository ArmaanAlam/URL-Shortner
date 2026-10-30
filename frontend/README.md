# URL Shortener Web Interface (Frontend)

A lightweight, minimal web client created to interact with the **First-Principles URL Shortener Backend** without having to use the terminal or `curl` commands.

---

## 📁 Why is this in a Separate Folder?

This project maintains **clean architectural separation**:
- **`app/` and root `main.py`**: Pure Python Backend Engineering code (FastAPI, SQLite WAL, Base62 algorithm, in-memory cache, repository pattern).
- **`frontend/`**: Pure client-side static assets (HTML, CSS, JavaScript).

Keeping this code completely isolated ensures that you can focus on reading and learning backend engineering patterns without getting distracted or confused by UI templates, frontend dependencies, or bundle tools.

---

## 🚀 How to Run and Use

### Step 1: Ensure Your Backend is Running
In your terminal, start the FastAPI server:
```powershell
python main.py
```
*(The backend runs on `http://localhost:8000`)*

### Step 2: Open the Webpage
You can open the webpage in any of these simple ways:
1. **Directly in File Explorer**: Double-click [`index.html`](file:///d:/Practice/Backend%20Engineering/frontend/index.html).
2. **From PowerShell**:
   ```powershell
   Start-Process "d:\Practice\Backend Engineering\frontend\index.html"
   ```
3. **VS Code Live Server**: If you use VS Code's Live Server extension, right-click `index.html` -> *Open with Live Server*.

---

## ✨ Features Included

1. **Live Backend Health Monitor**:
   - Pings `GET /` to show if your backend is currently running and healthy.
   - Shows cache capacity and live connection latency.
2. **Shorten URL Form**:
   - Paste long URLs with protocol validation (`http://` or `https://`).
   - Optional **Custom Short Key / Alias** field (3-30 chars).
   - Generates Base62 keys automatically if no custom alias is provided.
   - One-click copy with instant feedback.
   - One-click "Visit (Test 302)" button to test browser redirect behavior.
3. **Analytics & Stats Inspector**:
   - Query `GET /api/stats/{key}` to see total clicks and async audit records.
   - Shows timestamp, referrer, and user-agent for redirect clicks.
4. **Local Link History**:
   - Automatically saves links created during your testing in your browser's local storage so you don't lose track of your shortened links.
5. **Configurable Host**:
   - By default connects to `http://localhost:8000`. If you run FastAPI on a different port, click the gear icon to change it instantly.

