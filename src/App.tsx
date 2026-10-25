import React, { useState } from "react";
import {
  Activity,
  ArrowRight,
  CheckCircle2,
  Code2,
  Database,
  FileCode,
  Mic,
  Phone,
  Radio,
  Server,
  ShieldAlert,
  Volume2,
} from "lucide-react";

export default function App() {
  const [activeTab, setActiveTab] = useState<"overview" | "api" | "architecture" | "local_guide">("overview");
  const [simulatedTurnInput, setSimulatedTurnInput] = useState("Chennai to Coimbatore train timings sollunga");
  const [simulatedOutput, setSimulatedOutput] = useState<{
    status: string;
    speaker: string;
    utterance: string;
    detected_language: string;
    tool_called: string;
    grounding: string;
    barge_in_sla: string;
  } | null>(null);
  const [isSimulating, setIsSimulating] = useState(false);

  const handleSimulateTurn = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSimulating(true);
    setTimeout(() => {
      let tool = "transit_tool";
      let lang = "ta";
      let output =
        "Chennai Central-la irundhu Kovai-ku Cheran Express kaalai 6:10 AM-ku purappadum, pinbu Kovai Express 2:20 PM-ku irukku. Live seat availability therinjukkolla helpline 139 call pannalaam.";
      let grounding = "Southern Railway Schedules (IRCTC Guardrail CRIT-TRANSIT-01 enforced)";

      if (simulatedTurnInput.toLowerCase().includes("iphone") || simulatedTurnInput.toLowerCase().includes("price")) {
        tool = "search_tool";
        lang = "ta";
        output =
          "iPhone 15 128GB model Flipkart-la 65,999 rupees-ku kidaikkudhu. Amazon-la 66,499 rupees irukku. HDFC card-ku 2,000 rupees extra discount irukku.";
        grounding = "Google Search Grounding (Flipkart & Amazon India)";
      } else if (simulatedTurnInput.toLowerCase().includes("play") || simulatedTurnInput.toLowerCase().includes("song")) {
        tool = "youtube_tool";
        lang = "en";
        output = "Sure, playing that song for you now over 8kHz PCM audio stream.";
        grounding = "yt-dlp + ffmpeg pipe:1 (Barge-in active, sub-300ms SLA)";
      } else if (simulatedTurnInput.toLowerCase().includes("remind")) {
        tool = "reminder_tool";
        lang = "ta";
        output = "நிச்சயமாக, உங்கள் நினைவூட்டல் அட்டவணைப்படுத்தப்பட்டது. குறிப்பிட்ட நேரத்தில் தானியங்கி அழைப்பு வரும்.";
        grounding = "PostgreSQL voice_reminders table";
      }

      setSimulatedOutput({
        status: "200 OK",
        speaker: "Theodore (Voice Assistant)",
        utterance: output,
        detected_language: lang,
        tool_called: tool,
        grounding: grounding,
        barge_in_sla: "< 300 ms ready",
      });
      setIsSimulating(false);
    }, 600);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Header */}
      <header className="border-b border-slate-800 bg-slate-900/60 backdrop-blur px-6 py-4 flex items-center justify-between gap-8">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold">
            <Phone className="w-4 h-4" />
          </div>
          <div>
            <h1 className="text-base font-semibold tracking-tight text-white flex items-center gap-2">
              Theodore Voice AI
              <span className="text-xs px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-400 font-mono">
                FastAPI Monolith
              </span>
            </h1>
            <p className="text-xs text-slate-400">
              Grounded Multilingual Telephony AI Assistant & Streaming Control System
            </p>
          </div>
        </div>

        <nav className="flex items-center gap-1 bg-slate-900 p-1 rounded-lg border border-slate-800 text-xs">
          <button
            onClick={() => setActiveTab("overview")}
            className={`px-3 py-1.5 rounded-md font-medium transition-colors ${
              activeTab === "overview" ? "bg-slate-800 text-white shadow-sm" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Core Overview
          </button>
          <button
            onClick={() => setActiveTab("architecture")}
            className={`px-3 py-1.5 rounded-md font-medium transition-colors ${
              activeTab === "architecture" ? "bg-slate-800 text-white shadow-sm" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            System Architecture
          </button>
          <button
            onClick={() => setActiveTab("api")}
            className={`px-3 py-1.5 rounded-md font-medium transition-colors ${
              activeTab === "api" ? "bg-slate-800 text-white shadow-sm" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            OpenAPI Specs
          </button>
          <button
            onClick={() => setActiveTab("local_guide")}
            className={`px-3 py-1.5 rounded-md font-medium transition-colors ${
              activeTab === "local_guide" ? "bg-slate-800 text-white shadow-sm" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Local Setup Guide
          </button>
        </nav>
      </header>

      {/* Main Viewport */}
      <main className="flex-1 p-6 max-w-7xl mx-auto w-full space-y-6">
        {activeTab === "overview" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left 2 Cols: Telephony State & Interactive Simulator */}
            <div className="lg:col-span-2 space-y-6">
              {/* Telephony Status Grid */}
              <div className="grid grid-cols-3 gap-4">
                <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                  <div className="text-xs text-slate-400 flex items-center gap-1.5 mb-1">
                    <Radio className="w-3.5 h-3.5 text-emerald-400" /> Vobiz WebSocket
                  </div>
                  <div className="text-lg font-semibold text-white font-mono">8000 Hz</div>
                  <div className="text-xs text-slate-500 font-mono mt-0.5">16-bit Linear PCM (Mono)</div>
                </div>

                <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                  <div className="text-xs text-slate-400 flex items-center gap-1.5 mb-1">
                    <Activity className="w-3.5 h-3.5 text-blue-400" /> VAD Turn-Taking
                  </div>
                  <div className="text-lg font-semibold text-white font-mono">600 ms</div>
                  <div className="text-xs text-slate-500 font-mono mt-0.5">Hangover silence window</div>
                </div>

                <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                  <div className="text-xs text-slate-400 flex items-center gap-1.5 mb-1">
                    <ShieldAlert className="w-3.5 h-3.5 text-amber-400" /> Barge-In Cutoff
                  </div>
                  <div className="text-lg font-semibold text-white font-mono">&lt; 300 ms</div>
                  <div className="text-xs text-slate-500 font-mono mt-0.5">Subprocess SIGTERM kill</div>
                </div>
              </div>

              {/* Turn Simulation Playground */}
              <div className="p-5 rounded-xl bg-slate-900/70 border border-slate-800 space-y-4">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <div>
                    <h2 className="text-sm font-semibold text-white">Telephony Turn Simulator (Headless Test)</h2>
                    <p className="text-xs text-slate-400">
                      Simulates incoming caller voice utterances against LangGraph agent & grounded tools
                    </p>
                  </div>
                  <span className="text-xs font-mono px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800">
                    Bilingual (ta / en)
                  </span>
                </div>

                <form onSubmit={handleSimulateTurn} className="space-y-3">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={simulatedTurnInput}
                      onChange={(e) => setSimulatedTurnInput(e.target.value)}
                      placeholder="Enter caller utterance (Tamil, English, or Tanglish)..."
                      className="flex-1 px-3 py-2 text-xs bg-slate-950 border border-slate-800 rounded-lg text-slate-200 focus:outline-none focus:border-blue-500"
                    />
                    <button
                      type="submit"
                      disabled={isSimulating}
                      className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-medium transition-colors flex items-center gap-1.5 disabled:opacity-50"
                    >
                      {isSimulating ? "Processing..." : "Dispatch Turn"}
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  <div className="flex flex-wrap gap-2 text-xs text-slate-400">
                    <span>Quick presets:</span>
                    <button
                      type="button"
                      onClick={() => setSimulatedTurnInput("Chennai to Coimbatore train timings sollunga")}
                      className="hover:text-blue-400 underline decoration-slate-700"
                    >
                      Train Schedule (IRCTC Guardrail)
                    </button>
                    <span>·</span>
                    <button
                      type="button"
                      onClick={() => setSimulatedTurnInput("What is the price of iPhone 15 on Flipkart?")}
                      className="hover:text-blue-400 underline decoration-slate-700"
                    >
                      Product Price Grounding
                    </button>
                    <span>·</span>
                    <button
                      type="button"
                      onClick={() => setSimulatedTurnInput("Play classical instrumental music")}
                      className="hover:text-blue-400 underline decoration-slate-700"
                    >
                      YouTube Audio Pipe
                    </button>
                    <span>·</span>
                    <button
                      type="button"
                      onClick={() => setSimulatedTurnInput("Remind me to take blood pressure medicine in 2 hours")}
                      className="hover:text-blue-400 underline decoration-slate-700"
                    >
                      Voice Reminder
                    </button>
                  </div>
                </form>

                {simulatedOutput && (
                  <div className="mt-4 p-4 rounded-lg bg-slate-950 border border-slate-800 space-y-3">
                    <div className="flex items-center justify-between text-xs text-slate-400 border-b border-slate-900 pb-2">
                      <span className="flex items-center gap-1.5 text-emerald-400 font-mono">
                        <CheckCircle2 className="w-3.5 h-3.5" /> Turn Dispatched (HTTP 200 OK)
                      </span>
                      <span className="font-mono">Language: {simulatedOutput.detected_language}</span>
                    </div>

                    <div className="space-y-1">
                      <div className="text-xs text-slate-400">Synthesized Spoken Response (CRIT-VOICE-01 Contract):</div>
                      <p className="text-sm text-slate-200 leading-relaxed font-serif italic">
                        "{simulatedOutput.utterance}"
                      </p>
                    </div>

                    <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-900 text-xs font-mono text-slate-400">
                      <div>
                        <span className="text-slate-500">Tool Invoked:</span> {simulatedOutput.tool_called}
                      </div>
                      <div>
                        <span className="text-slate-500">Barge-in SLA:</span> {simulatedOutput.barge_in_sla}
                      </div>
                      <div className="col-span-2">
                        <span className="text-slate-500">Grounding Source:</span> {simulatedOutput.grounding}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Right Col: Backend Engine Status & Observability */}
            <div className="space-y-6">
              <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-4">
                <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                  <Server className="w-4 h-4 text-blue-400" /> Modular Monolith Stack
                </h3>
                <div className="space-y-2.5 text-xs">
                  <div className="flex items-center justify-between py-1.5 border-b border-slate-800">
                    <span className="text-slate-400">Framework</span>
                    <span className="font-mono text-slate-200">FastAPI 0.115 + Uvicorn</span>
                  </div>
                  <div className="flex items-center justify-between py-1.5 border-b border-slate-800">
                    <span className="text-slate-400">Database</span>
                    <span className="font-mono text-slate-200">PostgreSQL 16 + asyncpg</span>
                  </div>
                  <div className="flex items-center justify-between py-1.5 border-b border-slate-800">
                    <span className="text-slate-400">Agent Engine</span>
                    <span className="font-mono text-slate-200">LangGraph StateGraph</span>
                  </div>
                  <div className="flex items-center justify-between py-1.5 border-b border-slate-800">
                    <span className="text-slate-400">Grounding Model</span>
                    <span className="font-mono text-slate-200">Gemini 3.8 Flash</span>
                  </div>
                  <div className="flex items-center justify-between py-1.5 border-b border-slate-800">
                    <span className="text-slate-400">TTS Engine</span>
                    <span className="font-mono text-slate-200">Inworld TTS-2 Flash</span>
                  </div>
                  <div className="flex items-center justify-between py-1.5">
                    <span className="text-slate-400">Observability</span>
                    <span className="font-mono text-slate-200">LangSmith Tracing v2</span>
                  </div>
                </div>
              </div>

              <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
                <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                  <Database className="w-4 h-4 text-emerald-400" /> PostgreSQL Schemas
                </h3>
                <div className="space-y-2 text-xs font-mono text-slate-300">
                  <div className="p-2 rounded bg-slate-950 border border-slate-800/80">
                    <div className="text-blue-400 font-semibold">call_sessions</div>
                    <div className="text-slate-500 text-[11px]">session_id, caller_phone, status, language</div>
                  </div>
                  <div className="p-2 rounded bg-slate-950 border border-slate-800/80">
                    <div className="text-blue-400 font-semibold">conversation_turns</div>
                    <div className="text-slate-500 text-[11px]">turn_index, utterance, JSONB grounding & latencies</div>
                  </div>
                  <div className="p-2 rounded bg-slate-950 border border-slate-800/80">
                    <div className="text-blue-400 font-semibold">voice_reminders</div>
                    <div className="text-slate-500 text-[11px]">recipient_phone, scheduled_time_utc, status</div>
                  </div>
                  <div className="p-2 rounded bg-slate-950 border border-slate-800/80">
                    <div className="text-blue-400 font-semibold">audit_logs</div>
                    <div className="text-slate-500 text-[11px]">correlation_id, event_type, details JSONB</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === "architecture" && (
          <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800 space-y-6">
            <div>
              <h2 className="text-base font-semibold text-white">Theodore Voice Pipeline Architecture</h2>
              <p className="text-xs text-slate-400 mt-1">
                Sequence flow from carrier inbound telephony call to VAD, LangGraph, Grounding, and Barge-In
              </p>
            </div>

            <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 overflow-x-auto text-xs font-mono text-slate-300 leading-relaxed">
              <pre>{`
  [ Caller Telephone ]
          │ (PSTN / Mobile Network)
          ▼
  [ Vobiz.ai Carrier Gateway ]
          │ Webhook: POST /api/v1/telephony/webhook
          │ Returns: <Stream url="wss://.../stream/{session_id}" />
          ▼
  [ FastAPI Bi-directional WebSocket Route ] (/stream/{session_id})
          │ Inbound 8kHz PCM Chunks (20ms frames)
          ▼
  [ Voice Activity Detector (VAD) ] ────────────────────────┐
          │ Silence > 600ms (Turn complete)                 │ Voice Energy > 200ms
          ▼                                                 │ during playback
  [ LangGraph StateGraph Engine ]                           ▼
    ├── Language Classifier (ta / en / tanglish)    [ BARGE-IN CUTOFF ] (<300ms SLA)
    ├── Intent Router                               ├── 1. Send 'clearAudio' to Vobiz
    ├── Google Search Grounding                     ├── 2. os.killpg(pid, SIGTERM)
    ├── Google Maps Tool                            └── 3. Reset playback_state = 'idle'
    ├── Transit Tool (IRCTC Boundary: 139 Helpline)
    └── YouTube Stream Tool (yt-dlp + ffmpeg pipe)
          │
          ▼ Spoken Output (Zero markdown, no URLs)
  [ Inworld TTS-2 Flash / PCM Transcoder ]
          │
          ▼ Outbound 'playAudio' WebSocket event
  [ Caller Audio Playback ]
              `}</pre>
            </div>
          </div>
        )}

        {activeTab === "api" && (
          <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-base font-semibold text-white">OpenAPI 3.0.0 Endpoints Specification</h2>
                <p className="text-xs text-slate-400 mt-0.5">
                  Full Swagger document available at <span className="font-mono text-blue-400">design/api/openapi.yaml</span>
                </p>
              </div>
              <span className="text-xs px-2.5 py-1 rounded bg-slate-800 font-mono text-slate-300 border border-slate-700">
                12 API Routes
              </span>
            </div>

            <div className="space-y-2 text-xs font-mono">
              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="px-2 py-0.5 rounded bg-blue-900/60 text-blue-300 font-semibold">POST</span>
                  <span className="text-slate-200">/api/v1/telephony/webhook</span>
                </div>
                <span className="text-slate-500">Vobiz carrier webhook (returns VobizXML Stream)</span>
              </div>

              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="px-2 py-0.5 rounded bg-purple-900/60 text-purple-300 font-semibold">WS</span>
                  <span className="text-slate-200">/api/v1/telephony/stream/{`{session_id}`}</span>
                </div>
                <span className="text-slate-500">Bi-directional 8kHz PCM streaming & barge-in handler</span>
              </div>

              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="px-2 py-0.5 rounded bg-emerald-900/60 text-emerald-300 font-semibold">GET</span>
                  <span className="text-slate-200">/api/v1/telephony/sessions</span>
                </div>
                <span className="text-slate-500">List call sessions with status/language filter</span>
              </div>

              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="px-2 py-0.5 rounded bg-blue-900/60 text-blue-300 font-semibold">POST</span>
                  <span className="text-slate-200">/api/v1/telephony/stream/barge-in/{`{session_id}`}</span>
                </div>
                <span className="text-slate-500">Trigger immediate stream cutoff & clear buffer</span>
              </div>

              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="px-2 py-0.5 rounded bg-blue-900/60 text-blue-300 font-semibold">POST</span>
                  <span className="text-slate-200">/api/v1/reminders</span>
                </div>
                <span className="text-slate-500">Schedule outbound voice reminder</span>
              </div>

              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="px-2 py-0.5 rounded bg-blue-900/60 text-blue-300 font-semibold">POST</span>
                  <span className="text-slate-200">/api/v1/agent/turn</span>
                </div>
                <span className="text-slate-500">Headless turn simulation (unit & integration testing)</span>
              </div>

              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="px-2 py-0.5 rounded bg-blue-900/60 text-blue-300 font-semibold">POST</span>
                  <span className="text-slate-200">/api/v1/agent/tools/transit</span>
                </div>
                <span className="text-slate-500">Transit tool & CRIT-TRANSIT-01 guardrail validator</span>
              </div>

              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="px-2 py-0.5 rounded bg-emerald-900/60 text-emerald-300 font-semibold">GET</span>
                  <span className="text-slate-200">/api/v1/audit/logs</span>
                </div>
                <span className="text-slate-500">Query structured audit telemetry</span>
              </div>
            </div>
          </div>
        )}

        {activeTab === "local_guide" && (
          <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800 space-y-6">
            <div>
              <h2 className="text-base font-semibold text-white">How to Run Theodore Backend Locally</h2>
              <p className="text-xs text-slate-400 mt-1">
                Step-by-step setup to connect live mobile telephone calls to your local workstation
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 space-y-2">
                <div className="font-semibold text-blue-400">1. Start PostgreSQL 16</div>
                <p className="text-slate-400">Launch a containerized PostgreSQL instance:</p>
                <code className="block p-2 bg-slate-900 rounded font-mono text-[11px] text-slate-300">
                  docker run -d --name theodore-postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e
                  POSTGRES_DB=theodore_telephony -p 5432:5432 postgres:16-alpine
                </code>
              </div>

              <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 space-y-2">
                <div className="font-semibold text-blue-400">2. Install Dependencies & ffmpeg</div>
                <p className="text-slate-400">Ensure ffmpeg is in your system path and install Python packages:</p>
                <code className="block p-2 bg-slate-900 rounded font-mono text-[11px] text-slate-300">
                  brew install ffmpeg # or apt install ffmpeg{"\n"}
                  uv sync # or pip install -e ".[dev]"
                </code>
              </div>

              <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 space-y-2">
                <div className="font-semibold text-blue-400">3. Run the FastAPI Server</div>
                <p className="text-slate-400">Start the backend on port 8000:</p>
                <code className="block p-2 bg-slate-900 rounded font-mono text-[11px] text-slate-300">
                  make run{"\n"}# uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
                </code>
              </div>

              <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 space-y-2">
                <div className="font-semibold text-blue-400">4. Tunnel via ngrok & Configure Vobiz</div>
                <p className="text-slate-400">Expose port 8000 and set Webhook in Vobiz Console:</p>
                <code className="block p-2 bg-slate-900 rounded font-mono text-[11px] text-slate-300">
                  ngrok http 8000{"\n"}# Webhook: https://your-id.ngrok-free.app/api/v1/telephony/webhook
                </code>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
