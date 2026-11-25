# chatbot

## Modular Chatbot

A modular full-stack chatbot built with React, FastAPI, and PostgreSQL.

## Structure

```text
modular-chatbot/
  backend/          FastAPI API
  frontend/         React + Vite UI
  docker-compose.yml
```

## Run with Docker

```bash
docker compose up --build
```

- Frontend: http://localhost:5173
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs

## Run locally

To turn off the assistant launcher, set `VITE_ASSISTANT_FEATURE_FLAG=false` in `frontend/.env`.
The member-home demo assumes its page is protected by the host application's sign-in flow.
The React `App` also accepts an `isAuthenticated` prop so a host can hide the assistant on signed-out routes.
Local backend runs use SQLite by default; Docker Compose uses PostgreSQL.

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

In another terminal:

```bash
cd frontend
npm install
npm run dev
```
