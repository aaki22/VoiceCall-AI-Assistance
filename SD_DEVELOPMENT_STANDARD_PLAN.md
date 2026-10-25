# VoiceCall AI Assistance Standardization SD Plan

## Updated Folder Structure

```text
VoiceCall-AI-Assistance/
|-- design/
|   |-- architecture/overview.md
|   |-- api/webhook-contract.md
|   `-- diagrams/
|       |-- er-diagram.md
|       `-- sequence/phone-call-flow.md
|-- src/
|   |-- main.py
|   |-- routes/voice_webhook.py
|   |-- service/
|   |   |-- conversation_service.py
|   |   |-- audio_service.py
|   |   |-- news_service.py
|   |   `-- traffic_service.py
|   |-- agents/
|   |   |-- phone_assistant_graph.py
|   |   `-- phone_assistant_nodes.py
|   |-- tools/
|   |   |-- news_tool.py
|   |   `-- traffic_tool.py
|   |-- prompts/
|   |   |-- intent_prompts.py
|   |   `-- assistant_prompts.py
|   |-- dependencies/
|   |   |-- database.py
|   |   |-- clients.py
|   |   |-- repositories.py
|   |   `-- services.py
|   |-- models/
|   |   |-- response.py
|   |   |-- intent.py
|   |   |-- graph_state.py
|   |   `-- call.py
|   |-- repository/call_repository.py
|   |-- schema/call.py
|   |-- database/
|   |   |-- session.py
|   |   `-- init_db.py
|   |-- client/
|   |   |-- llm_client.py
|   |   |-- gemini_client.py
|   |   |-- inworld_tts_client.py
|   |   |-- geocoding_client.py
|   |   |-- traffic_client.py
|   |   |-- recording_client.py
|   |   `-- speech_recognition_client.py
|   |-- settings/settings.py
|   |-- constants/
|   |   |-- audio.py
|   |   |-- providers.py
|   |   `-- routes.py
|   |-- logging/
|   |   `-- config.py
|   |-- utils/file_paths.py
|   `-- exception/
|       |-- exceptions.py
|       `-- handlers.py
|-- tests/
|   |-- routes/test_voice_webhook.py
|   |-- service/
|   |-- agents/
|   |   |-- test_phone_assistant_graph.py
|   |   `-- test_phone_assistant_nodes.py
|   |-- tools/
|   |-- prompts/
|   |-- dependencies/
|   |-- models/
|   |-- repository/
|   |-- schema/
|   |-- database/
|   |-- client/
|   |-- settings/
|   |-- constants/
|   |-- utils/
|   `-- exception/
|-- audio/
|-- songs/
|-- .env
|-- .env.example
|-- .gitignore
|-- README.md
|-- pyproject.toml
`-- uv.lock
```

## List Of Requirements

1. Convert the project into the standard `src/` folder structure.
2. Move FastAPI app assembly into `src/main.py`.
3. Move webhook endpoints into `src/routes/voice_webhook.py`.
4. Move assistant orchestration into LangGraph files under `src/agents/`.
5. Move reusable application behavior into `src/service/`.
6. Move focused executable capabilities into `src/tools/`.
7. Move LLM prompt text into `src/prompts/`.
8. Move external provider integrations into `src/client/`.
9. Move database engine/session setup into `src/database/`.
10. Move ORM table definitions into `src/schema/`.
11. Move persistence operations into `src/repository/`.
12. Move Pydantic DTOs into `src/models/`.
13. Move dependency wiring into `src/dependencies/`.
14. Move environment configuration into `src/settings/`.
15. Move fixed application values into `src/constants/`.
16. Add application exceptions under `src/exception/`.
17. Add generic helpers under `src/utils/`.
18. Remove hardcoded secrets from source code.
19. Add `.env.example` with all required configuration.
20. Add `.gitignore` for private and generated files.
21. Restore and standardize missing database model support.
22. Add reproducible dependency management with `pyproject.toml`.
23. Validate structured LLM outputs with DTOs.
24. Use LangGraph for current assistant workflow orchestration.
25. Use LangChain for prompt templates, Gemini model calls, and structured output parsing.
26. Add external request timeouts and controlled provider failures.
27. Preserve current phone webhook XML behavior.
28. Add architecture, API, ER, sequence, and graph-flow documentation.
29. Add tests mirroring the new `src/` structure.
30. Document manual credential rotation.
31. Defer unrelated product/provider changes and future-only feature nodes.
32. Add centralized application logging.

## Detailed Overview

This SD converts the current FastAPI voice-call assistant into the provided FastAPI Agent Development Standard. The present codebase keeps routes, prompts, provider calls, audio handling, agent-like orchestration, database access, and configuration mostly in root-level files. The target standard separates those responsibilities into source folders with clear ownership.

The converted application must keep the same functional behavior. It must receive inbound calls, play a greeting, record caller audio, download the recording, transcribe speech, classify user intent, answer traffic/news/general questions, generate TTS audio, persist call sessions and turns, and continue the call loop until the caller exits.

The most important conversion is structural and orchestration-focused. The codebase should become a `src/` application with routes, services, agents, tools, prompts, clients, repositories, schemas, models, settings, constants, utilities, and exceptions. The assistant workflow should be represented with LangGraph using only the features already present in the current codebase. LangChain should be used for prompt templates, Gemini model calls, and structured output parsing. Tests should mirror the new structure. Documentation should describe the architecture, graph flow, and phone webhook contract.

The telephony routes must continue returning XML because that is the external provider contract. The standard JSON response envelope can be added for future JSON endpoints, but it must not replace XML webhook responses.

## Planned File Changes

### Files To Add

- `src/main.py`: FastAPI app assembly, router registration, static audio mount, exception handler registration.
- `src/routes/voice_webhook.py`: inbound and recording webhook route handlers.
- `src/agents/phone_assistant_graph.py`: LangGraph graph definition for the current phone assistant workflow.
- `src/agents/phone_assistant_nodes.py`: graph node functions for the current implemented workflow.
- `src/service/conversation_service.py`: call session lifecycle and per-turn processing.
- `src/service/audio_service.py`: audio conversion, generated audio paths, STT/TTS coordination.
- `src/service/news_service.py`: news workflow.
- `src/service/traffic_service.py`: traffic workflow.
- `src/tools/news_tool.py`: focused news headline capability.
- `src/tools/traffic_tool.py`: focused traffic lookup capability.
- `src/prompts/intent_prompts.py`: traffic/news intent prompts.
- `src/prompts/assistant_prompts.py`: general assistant response prompts.
- `src/dependencies/*.py`: database, client, repository, service, and agent dependency providers.
- `src/models/*.py`: Pydantic DTOs for calls, intents, and response envelopes.
- `src/models/graph_state.py`: LangGraph state model for the current call turn workflow.
- `src/repository/call_repository.py`: database operations for call sessions and turns.
- `src/schema/call.py`: SQLAlchemy ORM schema.
- `src/database/session.py`: SQLAlchemy engine, sessionmaker, and base.
- `src/database/init_db.py`: local table creation helper.
- `src/client/*.py`: wrappers for Gemini, Inworld TTS, geocoding, traffic, recording download, and speech recognition.
- `src/client/llm_client.py`: LangChain-compatible LLM abstraction over the configured Gemini model.
- `src/settings/settings.py`: typed environment-driven settings.
- `src/constants/*.py`: fixed route, audio, and provider constants.
- `src/logging/config.py`: centralized logging configuration.
- `src/utils/file_paths.py`: reusable file path helpers.
- `src/exception/*.py`: custom exceptions and handlers.
- `tests/`: mirrored test structure.
- `design/`: architecture, API contract, ER, and sequence documentation.
- `.env.example`: safe configuration template.
- `.gitignore`: private/generated/cache ignore rules.
- `README.md`: setup and run guide.
- `pyproject.toml`: dependencies and test/tooling configuration.

### Files To Move Or Replace

- `main.py`: move logic into `src/`; optionally leave a temporary compatibility launcher.
- `database.py`: replace with `src/database/session.py` and `src/dependencies/database.py`.
- `db_ops.py`: replace with `src/repository/call_repository.py`.
- `create_tables.py`: replace with `src/database/init_db.py`.
- `models.py`: split into `src/schema/` for ORM and `src/models/` for DTOs.

### Root Folders To Keep

- `audio/`: runtime-generated audio served by FastAPI.
- `songs/`: static media assets.

## Overall In Scope

- Full conversion into the given standard folder structure.
- Stable behavior for the existing voice-call assistant.
- Separation of routes, services, agents, tools, prompts, clients, repositories, schema, models, settings, constants, utilities, and exceptions.
- LangGraph orchestration for the current implemented call-processing flow.
- LangChain prompt templates and structured output parsing for current LLM usage.
- Environment-based configuration and secret removal.
- ORM schema restoration and persistence cleanup.
- Structured output validation for LLM JSON.
- Provider timeout and error handling improvements.
- Tests and documentation aligned to the new structure.
- Centralized logging with safe module-level logger usage.

## Overall Out Of Scope

- Changing the assistant product purpose.
- Changing the telephony XML provider contract.
- Replacing Gemini, Inworld TTS, Google Speech Recognition, OpenRouteService, Nominatim, or RSS providers.
- Adding MCP integration.
- Adding unrelated user-facing features.
- Adding graph nodes for future features such as realtime news updates, radio, music, or cricket before those features are implemented.
- Deleting existing generated audio files unless explicitly approved.
- Rotating credentials in external dashboards.

## Requirement 1: Convert To Standard Source Layout

### What It Is

This means the codebase must follow the standard `src/` structure instead of keeping production modules at the repository root.

### What To Do

Create the full `src/` folder tree shown above. Move each current responsibility into the matching standard folder. Keep runtime assets such as `audio/` and `songs/` at the root.

### What Not To Do

Do not leave the active application spread across root-level files. Do not keep duplicate active implementations in both root and `src/`.

### Acceptance Criteria

- The project contains the target `src/` folders listed in the updated folder structure.
- Active production imports use `src` modules.
- Root-level source files are removed or converted into documented compatibility entrypoints.

## Requirement 2: FastAPI Application Assembly

### What It Is

Application assembly is the creation of the FastAPI app, static mounts, route registration, and exception handler registration.

### What To Do

Place application assembly in `src/main.py`. Register the voice webhook router. Mount the `audio/` directory. Register custom exception handlers.

### What Not To Do

Do not place business logic, prompt text, database queries, or provider calls in `src/main.py`.

### Acceptance Criteria

- `src/main.py` creates the FastAPI app.
- `src/main.py` registers routers, static mounts, and exception handlers.
- `src/main.py` does not contain assistant decision logic, raw provider calls, or SQLAlchemy queries.

## Requirement 3: Route Layer

### What It Is

Routes handle HTTP details and delegate application behavior.

### What To Do

Move `/inbound` and `/process-recording` into `src/routes/voice_webhook.py`. Extract request form data, call the conversation service, and return telephony XML.

### What Not To Do

Do not perform AI decisions, raw database operations, or provider HTTP calls inside route handlers.

### Acceptance Criteria

- `/inbound` and `/process-recording` are defined in `src/routes/voice_webhook.py`.
- Route handlers delegate processing to injected services.
- Route handlers return XML responses with the expected telephony tags.

## Requirement 4: Agent Layer With LangGraph

### What It Is

The agent layer decides how the assistant responds to a caller. In the standardized version, this decision flow must be represented as a LangGraph workflow.

### What To Do

Create `src/agents/phone_assistant_graph.py` and `src/agents/phone_assistant_nodes.py`. Move the current assistant flow into graph nodes and conditional graph routing. The current graph must include only the features already present in the codebase:

- recording download coordination
- speech-to-text transcription
- traffic intent detection
- Tamil Nadu news intent detection
- traffic response handling
- Tamil Nadu news response handling
- general chat response handling
- text-to-speech generation
- call turn persistence
- end-call check

The graph must route between traffic, news, general chat, and end-call behavior based on current intent logic.

### What Not To Do

Do not let the agent create database sessions, read secrets directly, or build webhook XML. Do not add graph nodes for future-only features such as radio, music, cricket, or realtime news updates in this phase.

### Acceptance Criteria

- The assistant workflow is defined in `src/agents/phone_assistant_graph.py`.
- Current workflow nodes are defined in `src/agents/phone_assistant_nodes.py`.
- The graph routes only between current features: traffic, Tamil Nadu news, general chat, TTS, persistence, and end-call.
- No radio, music, cricket, or future-only feature nodes exist in the current graph.

## Requirement 5: Service Layer

### What It Is

Services hold reusable application workflows.

### What To Do

Create conversation, audio, news, and traffic services. The conversation service should own call lifecycle flow. The audio service should own audio conversion and STT/TTS coordination.

### What Not To Do

Do not initialize provider SDKs in services when a client wrapper should own that provider detail.

### Acceptance Criteria

- Conversation flow is handled by `conversation_service.py`.
- Audio conversion/STT/TTS coordination is handled by `audio_service.py`.
- News and traffic workflows are handled by their service modules.
- Services depend on clients, repositories, tools, or agents instead of hardcoded provider setup.

## Requirement 6: Tool Layer

### What It Is

Tools are focused capabilities used by the assistant.

### What To Do

Create a news tool for fetching headlines and a traffic tool for travel-time lookup. Keep tool inputs and outputs clear and independently testable.

### What Not To Do

Do not make tools handle FastAPI requests or telephony XML.

### Acceptance Criteria

- News lookup behavior is available through `src/tools/news_tool.py`.
- Traffic lookup behavior is available through `src/tools/traffic_tool.py`.
- Tool modules can be tested without FastAPI route calls.

## Requirement 7: Prompt Layer

### What It Is

Prompts are reusable LLM instructions.

### What To Do

Move traffic intent prompts, news intent prompts, and assistant response prompts into `src/prompts/`.

### What Not To Do

Do not leave large prompt literals inside route, service, or agent logic.

### Acceptance Criteria

- Intent prompts are stored in `src/prompts/intent_prompts.py`.
- General assistant prompts are stored in `src/prompts/assistant_prompts.py`.
- Route, service, and graph files reference prompt modules instead of embedding large prompt strings.

## Requirement 8: Client Layer

### What It Is

Clients wrap external systems and provider-specific APIs.

### What To Do

Create clients for Gemini, Inworld TTS, Nominatim geocoding, OpenRouteService traffic, telephony recording download, and speech recognition. Add timeouts to HTTP clients.

### What Not To Do

Do not call external providers directly from routes, agents, tools, or repositories.

### Acceptance Criteria

- Gemini calls are wrapped by a client module.
- Inworld TTS calls are wrapped by a client module.
- Nominatim, OpenRouteService, recording download, and speech recognition are wrapped by client modules.
- Raw provider SDK or HTTP usage is isolated to `src/client/`.

## Requirement 9: Database Layer

### What It Is

The database layer owns engine creation, session creation, ORM base, and initialization.

### What To Do

Move SQLAlchemy setup into `src/database/session.py`. Move table creation into `src/database/init_db.py`. Read the database URL from settings.

### What Not To Do

Do not hardcode database credentials in source code.

### Acceptance Criteria

- SQLAlchemy engine and sessionmaker live in `src/database/session.py`.
- Database URL is read from settings.
- `src/database/init_db.py` can initialize tables using the standardized schema modules.

## Requirement 10: Schema Layer

### What It Is

Schema contains SQLAlchemy ORM table definitions.

### What To Do

Create `src/schema/call.py` with call session and call turn tables.

### Reference Shape

```sql
call_sessions(session_id unique not null, started_at not null, ended_at nullable, total_turns default 0)
call_turns(session_id foreign key, user_text nullable, ai_text nullable, user_audio nullable, ai_audio nullable, created_at not null)
```

### What Not To Do

Do not mix ORM schema with Pydantic DTOs.

### Acceptance Criteria

- `CallSession` and `CallTurn` ORM models live in `src/schema/call.py`.
- Pydantic models do not inherit from SQLAlchemy ORM classes.
- The schema supports creating call sessions and call turns with the current persistence behavior.

## Requirement 11: Repository Layer

### What It Is

Repositories hide persistence details from services and agents.

### What To Do

Move call session creation, call turn insertion, and call ending into `src/repository/call_repository.py`.

### What Not To Do

Do not put SQLAlchemy queries in route handlers or agent orchestration.

### Acceptance Criteria

- Call persistence queries live in `src/repository/call_repository.py`.
- Services call repository methods for persistence.
- Routes and graph nodes do not directly query SQLAlchemy models.

## Requirement 12: DTO Model Layer

### What It Is

DTO models define structured application contracts.

### What To Do

Add Pydantic models for intent outputs, call data, and standard JSON responses for future non-webhook APIs.

### What Not To Do

Do not rely on unvalidated dictionaries for structured LLM output.

### Acceptance Criteria

- Intent output DTOs exist under `src/models/intent.py`.
- Graph state DTO exists under `src/models/graph_state.py`.
- Invalid or missing LLM output fields produce controlled fallback behavior.

## Requirement 13: Dependency Layer

### What It Is

Dependencies wire database sessions, clients, repositories, services, tools, and agents.

### What To Do

Create dependency providers in `src/dependencies/` and use FastAPI dependency injection from routes.

### What Not To Do

Do not instantiate major infrastructure directly inside request handlers.

### Acceptance Criteria

- Database, client, repository, service, tool, and graph dependencies have provider functions under `src/dependencies/`.
- Routes use FastAPI dependency injection.
- Dependency construction is centralized enough to mock in tests.

## Requirement 14: Settings Layer

### What It Is

Settings are environment-specific values such as credentials, URLs, model names, and timeouts.

### What To Do

Create `src/settings/settings.py` with typed environment settings and secret-aware fields.

### What Not To Do

Do not hardcode API keys, auth tokens, database passwords, or public tunnel URLs.

### Acceptance Criteria

- Runtime configuration is loaded from `src/settings/settings.py`.
- Sensitive values use secret-aware fields.
- Source files do not contain real API keys, auth tokens, database passwords, or ngrok/public tunnel URLs.

## Requirement 15: Constants Layer

### What It Is

Constants are fixed reusable application values.

### What To Do

Create constants for routes, audio settings, static mount names, file extensions, and provider labels.

### What Not To Do

Do not store secrets or environment-specific values in constants.

### Acceptance Criteria

- Route paths, static mount names, audio extensions, and fixed labels live in `src/constants/`.
- Provider credentials and deployment URLs are absent from constants.
- Constants are imported where repeated fixed values are needed.

## Requirement 16: Exception Layer

### What It Is

Exceptions provide controlled failure behavior.

### What To Do

Add custom exceptions for provider failures, validation failures, audio failures, and persistence failures. Add handlers that produce appropriate responses.

### What Not To Do

Do not leak raw provider exceptions to callers.

### Acceptance Criteria

- Custom exception classes exist for provider, validation, audio, and persistence failures.
- Exception handlers are registered with the FastAPI app.
- Failure responses are controlled and do not expose secrets or stack traces.

## Requirement 17: Utility Layer

### What It Is

Utilities are generic helpers shared across modules.

### What To Do

Add file path helpers for generated audio filenames and asset paths.

### What Not To Do

Do not place business workflow decisions in utilities.

### Acceptance Criteria

- Shared filename/path helpers live in `src/utils/file_paths.py`.
- Utility functions are generic and independently testable.
- Utilities do not call providers, repositories, or graph nodes.

## Requirement 17A: Logging Layer

### What It Is

Logging is cross-cutting application infrastructure used to observe route flow, graph routing, provider failures, audio processing, and persistence events.

### What To Do

Create a dedicated logging module under `src/logging/`. Configure logging once during FastAPI app creation. Add module-level loggers with `logging.getLogger(__name__)` in routes, graph nodes, clients, services, repositories, and exception handlers. Log safe metadata such as session IDs, selected intent, branch decisions, filenames, and failure categories.

### What Not To Do

Do not place logging setup in `src/utils/`. Do not log API keys, auth tokens, full request headers, audio bytes, base64 payloads, or full user transcripts at info level.

### Acceptance Criteria

- `src/logging/config.py` exists and configures application logging.
- `src/main.py` configures logging once during app creation.
- Operational modules use module-level loggers.
- Logs avoid secrets, auth headers, audio payloads, and full transcript content.

## Requirement 18: Secrets And Environment Template

### What It Is

Secrets must be removed from committed source and documented through a safe template.

### What To Do

Add `.env.example` with all required keys. Keep real values in local `.env`.

### What Not To Do

Do not commit real credentials.

### Acceptance Criteria

- `.env.example` exists and includes every required configuration key.
- `.env.example` contains no real secrets.
- `.env` is ignored by `.gitignore`.

## Requirement 19: Dependency Management

### What It Is

Dependencies must be reproducible.

### What To Do

Add `pyproject.toml` with runtime and test dependencies.

### What Not To Do

Do not depend on undocumented local environment packages.

### Acceptance Criteria

- `pyproject.toml` exists with runtime dependencies.
- Test dependencies are declared.
- README run instructions use the declared dependency manager and entrypoint.

## Requirement 20: Generated Artifact Hygiene

### What It Is

Runtime-generated files should not be treated as source.

### What To Do

Ignore generated audio and Python cache/test artifacts.

### What Not To Do

Do not delete existing generated files without approval.

### Acceptance Criteria

- `.gitignore` ignores generated audio output.
- The application still creates `audio/` when needed.
- Existing audio files are left untouched unless deletion is separately approved.

## Requirement 21: Structured LLM Output Validation

### What It Is

LLM JSON output must be validated before use.

### What To Do

Validate traffic and general intent outputs through DTOs with safe fallbacks.

### What Not To Do

Do not trust arbitrary JSON text from the model.

### Acceptance Criteria

- Traffic intent output is parsed into a DTO.
- News/general intent output is parsed into a DTO.
- Malformed LLM output falls back to safe general-chat behavior or a controlled assistant response.

## Requirement 22: LangGraph Workflow

### What It Is

LangGraph is the orchestration layer for the phone assistant workflow. It makes the call-processing flow explicit as state, nodes, and conditional routing.

### What To Do

Create a graph for the current codebase behavior only. The graph should model one recorded caller turn from recording download through response generation and persistence. It should contain nodes for transcription, intent detection, traffic handling, Tamil Nadu news handling, general chat handling, TTS generation, persistence, and end-call decision. The graph state should be represented by a DTO in `src/models/graph_state.py`.

### What Not To Do

Do not create LangGraph nodes for future features that are not currently implemented. Do not put provider-specific API details inside graph node functions. Do not use the graph as a replacement for routes, repositories, or settings.

### Acceptance Criteria

- LangGraph dependency is declared.
- The graph compiles successfully.
- Tests verify at least traffic, news, general chat, and end-call routing.
- Graph state contains the fields needed for the current call turn only.

## Requirement 23: LangChain Usage

### What It Is

LangChain is the LLM interaction layer for prompts, model calls, and structured output parsing.

### What To Do

Use LangChain prompt templates for the current traffic intent, news intent, and general assistant prompts. Use LangChain structured output parsing or Pydantic output validation for model responses that must be JSON. Keep Gemini as the underlying model provider through a dedicated client abstraction.

### What Not To Do

Do not use a broad LangChain agent executor when LangGraph owns orchestration. Do not define tools only inside LangChain if they belong as application modules under `src/tools/`. Do not add unnecessary memory or retrieval components in this phase.

### Acceptance Criteria

- LangChain dependency is declared.
- Current prompts use LangChain prompt templates or equivalent LangChain prompt primitives.
- Structured model outputs are validated through LangChain/Pydantic flow.
- No LangChain agent executor is introduced for this phase.

## Requirement 24: External Call Safety

### What It Is

Provider calls must be bounded and failure-aware.

### What To Do

Add request timeouts and validate required provider response fields before use.

### What Not To Do

Do not use unbounded HTTP calls or assume provider payload shape.

### Acceptance Criteria

- All external HTTP calls include configured timeouts.
- Provider clients validate required response fields before use.
- Provider failure paths return controlled errors or safe assistant fallback text.

## Requirement 25: Preserve Phone XML Contract

### What It Is

The phone provider expects XML instructions.

### What To Do

Keep XML response behavior for call play, record, and hangup flows.

### What Not To Do

Do not replace webhook XML with JSON response envelopes.

### Acceptance Criteria

- `/inbound` returns XML containing greeting playback and recording instructions.
- `/process-recording` returns XML containing AI audio playback and either recording instructions or hangup.
- Existing route paths remain unchanged.

## Requirement 26: Documentation

### What It Is

Documentation must match the standardized architecture.

### What To Do

Add README setup instructions, architecture overview, webhook contract, ER notes, sequence flow, and a graph flow description for the current nodes.

### What Not To Do

Do not document the old root-level structure as the target architecture.

### Acceptance Criteria

- README explains setup, configuration, database initialization, and app startup.
- `design/architecture/overview.md` describes the standardized architecture.
- `design/api/webhook-contract.md` documents the XML webhook contract.
- ER and phone-call sequence documentation exist under `design/diagrams/`.

## Requirement 27: Testing

### What It Is

Tests must mirror the new source structure and avoid live providers.

### What To Do

Add tests for DTO validation, repository behavior, route XML shape, prompt rendering, provider-client failure handling, LangGraph node behavior, graph routing, and service behavior with mocks.

Test support doubles must use class names that start with `Test`, such as `TestAudioService` or `TestLLMClient`, and should set `__test__ = False` when the class is a helper rather than a pytest test class.

### What Not To Do

Do not require live external API credentials for normal tests.

### Acceptance Criteria

- Tests mirror the `src/` structure.
- Tests mock Gemini, Inworld, OpenRouteService, Nominatim, telephony recording download, and speech recognition.
- Tests cover DTO validation, graph routing, route XML shape, repository behavior, and provider failure handling.
- Test helper classes do not use `Fake` naming and instead follow the `Test...` naming convention.

## Requirement 28: Credential Rotation Follow-Up

### What It Is

Credentials previously committed or present in source should be treated as exposed.

### What To Do

Document that credentials must be rotated manually in provider dashboards.

### What Not To Do

Do not assume code cleanup invalidates exposed credentials.

### Acceptance Criteria

- README or design documentation notes that previously exposed credentials must be rotated manually.
- No replacement credential values are committed.
- `.env.example` remains safe to publish.

## Requirement 29: Migration Compatibility

### What It Is

The migration must leave the app runnable from the new structure.

### What To Do

Update imports, run commands, and documentation to point to `src.main:app`.

### What Not To Do

Do not leave stale root files that conflict with new modules.

### Acceptance Criteria

- The documented run command uses `src.main:app`.
- Imports resolve from the standardized structure.
- Root compatibility files, if any, are minimal and do not duplicate business logic.

## Requirement 30: Deferred Work

### What It Is

Some standard items are unrelated to this app today.

### What To Do

Defer MCP integration, provider replacement, unrelated feature changes, credential rotation execution, and graph nodes for future-only features.

### What Not To Do

Do not expand scope beyond converting the current app into the given standard.

### Acceptance Criteria

- Future-only features are listed as future work, not implemented nodes.
- No MCP, provider replacement, user account system, or unrelated feature code is added in this phase.
- The implemented scope maps back to the current codebase behavior.
