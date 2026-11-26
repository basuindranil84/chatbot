# chatbot

## Modular Chatbot

A modular full-stack chatbot built with React, FastAPI, and PostgreSQL.

## Sample profile data

The backend uses `backend/app/data/profiles.json` as its master dataset. It contains
500 synthetic profiles across Indian regions and communities, split between male and
female profiles aged 21–45. Chat searches filter this data and return up to five
structured profile cards by gender, age, location, community, profession,
religion, language, and interests; no external AI service is used. First-message
suggestions use a profile's interests. Favorites are not stored in this demo.
The synthetic records also include height, diet, caste/gotra labels, smoking and
social-drinking preferences, and a small set of lifestyle values for search
testing. Caste and gotra values are deliberately generic synthetic labels.
Optional profile fields are searchable only when the corresponding field is
enabled in that profile's `visibility` map. A vague height request such as
"tall" asks for a minimum height in centimeters rather than assuming a cutoff.

Regenerate the deterministic sample dataset with:

```bash
python backend/scripts/generate_profiles.py
```

Run the profile search tests from `backend/`:

```bash
python -m unittest discover -s tests
```

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
