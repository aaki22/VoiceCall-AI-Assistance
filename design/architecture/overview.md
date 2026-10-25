# Architecture Overview

The application follows the FastAPI Agent Development Standard with a `src/` package layout.

Flow:

```text
FastAPI route
-> conversation service
-> LangGraph phone assistant graph
-> current feature nodes
-> tools/services/clients
-> repository
-> XML webhook response
```

Current graph nodes cover only existing behavior: recording download, transcription, intent detection, traffic handling, Tamil Nadu news handling, general chat, TTS generation, persistence, and end-call handling.

Future feature nodes such as radio, music, cricket, and realtime news updates should be added only when those features are implemented.
