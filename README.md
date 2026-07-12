# AI-Productivity-Assistant
Full-stack productivity assistant that syncs Gmail &amp; Calendar, auto-extracts tasks via AI, and includes a real tool-calling chat agent — FastAPI, PostgreSQL, React, Gemini.

Flowspace

A full-stack productivity assistant that syncs Gmail and Google Calendar, then layers AI on top of a working, tested, rule-based core — emails and meetings get automatically turned into tasks, email priority/category gets classified, and a genuine tool-calling chat agent can query and act on your data through natural language.

Most of the "AI" here is deliberately simple: single-shot structured LLM calls for classification and generation. The chat agent is the one place real agentic tool-calling is used — and that split is intentional, not accidental. See AI Architecture below for why.


Tech stack

LayerChoiceBackendFastAPI, SQLAlchemy, AlembicDatabasePostgreSQLFrontendReact (Vite), Tailwind CSS, React QueryAuthGoogle OAuth2 + JWTAIGoogle Gemini, langchain-core + langchain-google-genai (no LangGraph)Testingpytest (backend), Vitest + React Testing Library (frontend)


Features


Google OAuth login — Gmail + Calendar read access
Gmail sync — parses multipart MIME, dedupes by message ID, categorizes emails
Calendar sync — handles all-day vs. timed events, infers meeting type
Task management — full CRUD, priority/category/status, source tracking (manual, email, calendar, or AI)
Meeting scheduling — conflict detection, free-slot finding, focus-window recommendation
Dashboard — productivity score, recommendations, morning brief
AI task extraction — reads newly-synced emails/meetings, creates real tasks with a foreign-key link back to their source
Email intelligence — AI-predicted category, priority (HIGH/MEDIUM/LOW), and summary
Smart reply — tone-selectable draft generation (formal/friendly/short/detailed)
AI-enhanced recommendations — rule-based logic decides what, AI rewrites how it's phrased
Chat agent — natural-language interface with 10 tools spanning tasks, meetings, emails, and recommendations


Every AI feature fails safe: with no GEMINI_API_KEY configured, the entire app still works end-to-end — AI-only endpoints return a clean 503 instead of crashing, and features like the dashboard fall back to their rule-based output.


Architecture

Browser → axios (attaches JWT) → FastAPI route (auth + delegate only)
  → service function (the actual logic) → SQLAlchemy model → PostgreSQL
  → Pydantic schema (shapes response) → React → React Query hook → UI

Routers are deliberately thin — almost no logic lives in app/api/*.py, just Depends(get_current_user) plus a call into app/services/*.py. Service functions can be unit-tested with a plain DB session, no HTTP layer involved.

Database

5 tables: users (hub), google_accounts (1:1), emails, meetings, tasks — each owned by a user. tasks additionally has nullable source_email_id/source_meeting_id foreign keys (with a database-level CHECK constraint preventing both being set at once), so an AI-extracted task always links back to exactly the email or meeting it came from.

Schema changes are tracked with Alembic, not create_all() — see backend/alembic/versions/ for the real migration history (baseline → task-source foreign keys → email AI fields).

AI architecture

FeatureShapeGenuinely agentic?Task extraction, email intelligence, smart reply, recommendation enhancement, morning brief narrationOne structured LLM call in, one parsed response outNo — classification/generationChat agentModel picks a tool → tool runs against the real DB → result fed back → model decides the next step, up to 5 roundsYes

The chat agent's loop is hand-written with LangChain's bind_tools() — not create_agent() or AgentExecutor, both of which pull in LangGraph as a dependency even when unused directly. Verified in a clean venv: langchain-core + langchain-google-genai alone have zero LangGraph anywhere in the dependency tree.


Getting started

Prerequisites


Python 3.11+
Node.js 18+
PostgreSQL, running locally
A Google Cloud OAuth client (Client ID + Secret)
A Gemini API key (optional — the app works fully without one)


Database

bashpsql -U postgres -c "CREATE DATABASE productivity;"

Backend

bashcd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

Create backend/.env:

GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
SESSION_SECRET=any_random_string
JWT_SECRET=any_random_string
FRONTEND_URL=http://localhost:5173
DATABASE_URL=postgresql://postgres:your_password@localhost/productivity
GEMINI_API_KEY=your_gemini_key_here

In Google Cloud Console, add http://127.0.0.1:8000/auth/callback as an authorized redirect URI.

Run migrations:

bash# fresh empty database:
alembic upgrade head

# database already has tables from a previous run:
alembic stamp 0001_baseline
alembic upgrade head

Start the server:

bashuvicorn main:app --reload

API docs at http://127.0.0.1:8000/docs.

Frontend

bashcd frontend
npm install
npm run dev

App at http://localhost:5173.


Testing

bash# backend — 80 tests, all Gemini calls mocked, no live network needed
cd backend
pip install -r requirements-dev.txt
pytest

# frontend — 25 tests
cd frontend
npm run test:run

Backend tests run against an isolated in-memory SQLite database per test, never the real Postgres instance.