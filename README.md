# Theodore — Grounded Multilingual Telephony AI Assistant & Streaming Control System

**Project ID:** PROJ-VOICE-001  
**Story ID:** ST-101  
**Architecture:** Python FastAPI Modular Monolith (Clean Architecture)  
**Carrier Gateway:** Vobiz.ai (8kHz Mono Linear PCM / μ-law WebSockets)  
**Observability:** LangSmith Distributed Tracing (`TheodoreVoiceSessionTurn`)  
**Persistence:** PostgreSQL 16 (Async SQLAlchemy 2.0 + asyncpg)  

---

## 1. Overview

**Theodore** is an enterprise-grade voice AI assistant designed to handle live telephone calls over carrier telecommunications networks via Vobiz.ai. It manages bidirectional 8kHz linear PCM audio streams, performs sub-600ms Voice Activity Detection (VAD) turn-taking, routes caller requests through a LangGraph `StateGraph` engine, executes real-time grounded tool lookups (Google Search and Google Maps), strictly enforces Indian Railways (IRCTC) booking guardrails (`CRIT-TRANSIT-01`), schedules automated outbound reminder calls, streams zero-disk YouTube audio, and executes instant sub-300ms voice barge-in stream termination with an immediate conversational reset.

---

## 2. Directory Structure

```text
.
├── design/
│   ├── diagrams/
│   │   ├── er-diagram.mmd
│   │   ├── infra_aws_deployment.mmd
│   │   └── sequence/
│   │       └── seq_voice_telephony_flow.mmd
│   └── api/
│       └── openapi.yaml
│
├── src/
│   ├── main.py                    # FastAPI application factory, lifespan, CORS, and routers
│   ├── settings/
│   │   └── settings.py            # Pydantic BaseSettings loading all secrets and environment configs
│   ├── constants/
│   │   ├── agents.py              # Agent node and tool identifiers
│   │   ├── api.py                 # Endpoint prefixes and pagination constants
│   │   └── errors.py              # UPPER_SNAKE_CASE error code constants
│   ├── exception/
│   │   └── exceptions.py          # Custom domain exceptions and standard JSON error handlers
│   ├── utils/
│   │   ├── logger.py              # Centralized JSON structured logger
│   │   └── vad.py                 # 8kHz PCM Voice Activity Detection & barge-in state machine
│   ├── database/
│   │   └── database.py            # AsyncEngine, async_sessionmaker, and transaction scope
│   ├── schema/
│   │   ├── base.py                # Base declarative entity with soft-delete TimestampMixin
│   │   ├── call_session.py        # CallSession table mapped entity
│   │   ├── conversation_turn.py   # ConversationTurn table with JSONB grounding & latencies
│   │   ├── reminder.py            # VoiceReminder table for scheduled outbound calls
│   │   └── audit.py               # AuditLog table for operational tracking
│   ├── models/
│   │   ├── dtos/
│   │   │   ├── call_models.py     # Turn, session, and barge-in DTOs
│   │   │   └── reminder_models.py # Reminder input and output DTOs
│   │   └── responses/
│   │       └── response_models.py # Standard API envelope ResponseBuilder[T]
│   ├── repository/
│   │   ├── call_session_repository.py # Call session & turns data access
│   │   ├── reminder_repository.py     # Voice reminder persistence & due query
│   │   └── audit_repository.py        # Audit record logging
│   ├── client/
│   │   ├── gemini_client.py       # Gemini 3.8 Flash SDK wrapper with Search & Maps grounding
│   │   ├── inworld_tts_client.py  # Inworld AI TTS-2 Flash WebSocket streaming client
│   │   ├── vobiz_adapter.py       # Vobiz REST client & VobizXML stream generator
│   │   ├── ytdlp_client.py        # yt-dlp audio stream URL extraction wrapper
│   │   └── ffmpeg_manager.py      # ffmpeg subprocess streaming & process group manager
│   ├── prompts/
│   │   ├── system/
│   │   │   └── theodore_persona.py# Core voice assistant persona & CRIT-VOICE-01 contract
│   │   └── tools/
│   │       └── transit_rules.py   # Public transport & IRCTC capability boundary (CRIT-TRANSIT-01)
│   ├── tools/
│   │   ├── search_tool.py         # Google Search pricing & e-commerce comparison tool
│   │   ├── maps_tool.py           # Google Maps local place lookup tool
│   │   ├── transit_tool.py        # Transit guidance tool enforcing booking boundaries
│   │   ├── youtube_tool.py        # YouTube audio streaming trigger
│   │   └── reminder_tool.py       # Conversational voice reminder parser & tool
│   ├── agents/
│   │   └── call_orchestrator_graph.py # LangGraph StateGraph engine (Theodore core)
│   ├── service/
│   │   ├── call_session_service.py# Audio VAD coordinator, turn dispatcher, and barge-in cutoff
│   │   ├── reminder_service.py    # Reminder business logic & due outbound evaluator
│   │   ├── audit_service.py       # Centralized audit recording service
│   │   └── audio_stream_pipeline.py# Subprocess youtube/ffmpeg audio pipe supervisor
│   ├── dependencies/
│   │   └── dependencies.py        # Composition wiring for FastAPI Depends()
│   └── routes/
│       ├── default.py             # HealthCheck, ready, and docs endpoints
│       ├── call_stream_routes.py  # Vobiz webhook, bidirectional WebSocket, and sessions API
│       ├── reminder_routes.py     # Voice reminder scheduling CRUD & trigger
│       ├── agent_test_routes.py   # Headless turn testing & guardrail evaluation
│       └── audit_routes.py        # Structured audit query & LangSmith trace links
│
├── test/                          # Unit and integration test suite
│   ├── test_vad.py
│   ├── test_transit_tool.py
│   ├── test_barge_in.py
│   ├── test_call_orchestrator_graph.py
│   └── test_routes.py
│
├── .env.example
├── Makefile
├── pyproject.toml
└── README.md
```

---

## 3. How to Make It Work Locally (Step-by-Step)

### Step 1: System Prerequisites
- **Python 3.12+**
- **`ffmpeg`** installed and available in `$PATH`:
  - macOS: `brew install ffmpeg`
  - Linux (Ubuntu/Debian): `sudo apt update && sudo apt install -y ffmpeg`
  - Windows: `winget install Gyan.FFmpeg`
- **Docker** (for local PostgreSQL instance)

### Step 2: Start PostgreSQL 16
Run a local PostgreSQL container using Docker:
```bash
docker run -d \
  --name theodore-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=theodore_telephony \
  -p 5432:5432 \
  postgres:16-alpine
```

### Step 3: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Fill in your credentials in `.env`:
- `DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/theodore_telephony"`
- `GEMINI_API_KEY="AIzaSy..."`
- `VOBIZ_ACCOUNT_SID="AC_YOUR_VOBIZ_ACCOUNT_SID"`
- `VOBIZ_AUTH_TOKEN="YOUR_VOBIZ_AUTH_TOKEN"`
- `VOBIZ_PHONE_NUMBER="+1XXXXXXXXXX"` (Your virtual DID in Vobiz console)
- `INWORLD_API_KEY="YOUR_INWORLD_API_KEY"` (or keep default for simulated PCM testing)
- `LANGCHAIN_API_KEY="lsv2_pt_..."` (Optional, for LangSmith run tree tracing)

### Step 4: Install Dependencies & Run Server
Using `uv` (recommended) or `pip`:
```bash
# Install with uv
make setup
# Or via pip
pip install -e ".[dev]"

# Start the server
make run
# Server will start on http://0.0.0.0:8000
```

### Step 5: Expose Localhost to Telephony Carrier (Ngrok Tunnel)
Because carrier phone calls come through Vobiz cloud infrastructure on the public internet, tunnel your local FastAPI port:
```bash
ngrok http 8000
# Output example: https://d19a-2405-201.ngrok-free.app
```
Update `PUBLIC_APP_URL` in `.env`:
```bash
PUBLIC_APP_URL="https://d19a-2405-201.ngrok-free.app"
```

### Step 6: Configure Vobiz Webhook
1. Log in to your [Vobiz.ai Console](https://vobiz.ai).
2. Go to **Phone Numbers** > Select your purchased virtual DID number.
3. In the **Voice Configuration** section:
   - Set **Webhook URL** to: `https://d19a-2405-201.ngrok-free.app/api/v1/telephony/webhook`
   - Set **HTTP Method** to: `POST`.
4. Click **Save**.

### Step 7: Test with a Real Phone Call!
- Call your virtual DID phone number from any normal mobile phone.
- Vobiz hits your local webhook, receives the VobizXML with the WebSocket `<Stream>` directive, and establishes an active 8kHz PCM socket with your local machine.
- Speak in English, Tamil, or Tanglish:
  - *"Chennai to Coimbatore train timings sollunga"* (Triggers transit tool under IRCTC guardrail).
  - *"Play classical instrumental song"* (Triggers YouTube zero-disk streaming).
  - **Test Barge-In**: While the song is playing, talk over it (*"Stop music, what is the weather?"*). Within <300ms, the song stops, buffers flush, and Theodore smoothly answers the new question!

---

## 4. Running Automated Tests

Run the test suite with coverage:
```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run ruff code quality checks
make check
```

---

## 5. API Documentation

Interactive OpenAPI / Swagger documentation is available at:
`http://localhost:8000/docs`
The raw OpenAPI 3.0.0 specification file is located at `design/api/openapi.yaml`.
