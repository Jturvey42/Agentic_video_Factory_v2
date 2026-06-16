# Agentic Video Factory (v2)

An asynchronous, asset-driven data video automation engine built to programmatically compile analytics-focused content. The system completely decouples audio synthesis, data visualization engineering, and video timeline composition into a deterministic pipeline, eliminating manual editing overhead.

Built by a Data Analyst specializing in Python automation, pipeline reliability, and robust system design.

---

## 🛠️ Key Architectural Highlights

* **Dynamic Timeline Math:** Completely abandons brittle, hardcoded frame durations. Audio tracks are synthesized dynamically, and video layer timelines are calculated programmatically to ensure perfect alignment without voice cutoff.
* **Decoupled Asset-Driven Design:** Video layouts, text overlays, and audio cues are defined via a strict data contract (`video_manifest_ep2.json`), separating content configuration from execution logic.
* **Hardened Subprocess Lifecycle Patches:** Custom process handling safely manages and isolates local resource execution on Windows environments, ensuring stable rendering without memory leaks or dropped frames.
* **Local AI Inference Stack:** Leverages a local `Kokoro ONNX` model for high-fidelity voice-over generation, eliminating external API costs, rate limits, and network latency.

---

## 📁 Repository Architecture

```text
Agentic_Video_Factory_v2/
├── main.py                  # Unified pipeline entry point
├── run_content_assembly.py  # Orchestrator handling dynamic timeline math
├── video_manifest_ep2.json  # JSON data contract defining the video state
├── src/                     # Core operational modules
│   ├── chart_overlay_engine.py # Programmatic data visualization layer
│   ├── timeline_compiler.py    # Hardened relative layout & scale composition
│   └── tools.py                # Local Kokoro ONNX voice synthesis engine
├── data/                    # Source analytics and telemetry CSVs
└── music/                   # Production audio assets (pre-cleared)