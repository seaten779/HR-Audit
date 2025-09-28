# HR Audit Backend

## Run locally

```bash
# From project root
cd backend

# (Optional) create venv
# python -m venv .venv
# .\.venv\Scripts\activate  # Windows PowerShell

pip install -r requirements.txt

# Copy env example and adjust if needed
# cp .env.example .env  (Windows: copy .env.example .env)

# Start API (auto-reload)
python main.py
```

- API docs: http://localhost:8000/docs
- WS endpoint: ws://localhost:8000/ws

## Structure
- `app/core`: settings/config
- `app/api`: REST endpoints
- `app/services`: simulator, anomaly detector, explanation engine
- `app/models`: pydantic models

## Notes
- Demo mode emits simulated transactions continuously.
- Set `NEXT_PUBLIC_BACKEND_WS` in frontend to point at the WS URL.
- Nessie API integration is optional and disabled by default.
