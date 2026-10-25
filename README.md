# VoiceCall AI Assistance

FastAPI voice-call assistant that handles inbound phone calls, records caller audio, transcribes speech, routes the request through a LangGraph workflow, generates a TTS response, stores call turns, and returns telephony-compatible XML.

## Current Features

- Inbound call greeting.
- Caller recording processing.
- Tamil speech-to-text transcription.
- Traffic request handling.
- Tamil Nadu news headline handling.
- General chat response handling.
- Text-to-speech audio generation.
- Call session and turn persistence.

Future features such as radio, music, cricket, and realtime news updates are planned expansion points, but they are not implemented as graph nodes yet.

## Setup

1. Create a virtual environment.
2. Install dependencies from `pyproject.toml` or `requirements.txt`.
3. Copy `.env.example` to `.env` and fill in real local values.
4. Install `ffmpeg` and make sure it is available on `PATH`.
5. Create the database tables.

```bash
python create_tables.py
```

## Run

```bash
uvicorn src.main:app --reload
```

You can also run the compatibility entrypoint directly:

```bash
python main.py
```

The standardized app entrypoint remains `src.main:app`.

## Configuration

Runtime configuration is loaded from environment variables through `src/settings/settings.py`.

Real credentials must stay in `.env` or deployment secrets, not in committed source files. Credentials that were previously present in source should be rotated manually in the related provider dashboards.

## Webhook Endpoints

- `POST /inbound`
- `POST /process-recording`
- `GET /health`
- `GET /health/db`

The phone webhook endpoints return XML because the telephony provider expects XML.
