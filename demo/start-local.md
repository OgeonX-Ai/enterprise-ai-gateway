# Start the local demo

1. **Install dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r backend/requirements.txt
   ```

2. **Run the backend**
   ```bash
   uvicorn app.main:app --app-dir backend --reload
   ```

3. **Open the frontend**
   - Launch `web/index.html` in your browser.
   - Select providers, send a message, and review the debug drawer for routing decisions.

4. **Capture screenshots**
   Save any captures to `demo/screenshots/` for easy sharing.
