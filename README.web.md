This project now includes a minimal web frontend and Flask backend.

How to run locally:

1. Install Python dependencies (use venv if desired):

```powershell
python -m pip install -r requirements.txt
```

2. Start the backend (serves the web UI and API):

```powershell
python src\backend.py
```

3. Open http://127.0.0.1:5000 in your browser.

Notes:
- The web UI is in `/web` and served as static files by the Flask app.
- The backend exposes `/api/map` and `/api/path` endpoints.
