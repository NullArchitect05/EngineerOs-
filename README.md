<div align="center">
  <img src="https://img.shields.io/badge/version-1.1.0-0ea5e9?style=for-the-badge" alt="Version"/>
  <img src="https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react" alt="React"/>
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python" alt="Python"/>
  <img src="https://img.shields.io/badge/Vite-8-646CFF?style=for-the-badge&logo=vite" alt="Vite"/>
  <img src="https://img.shields.io/badge/Tailwind-4-06B6D4?style=for-the-badge&logo=tailwindcss" alt="Tailwind"/>
  <br/><br/>
  <h1>EngineerOS</h1>
  <h3>AI-Powered Repository Engineering Health Analyzer</h3>
  <p><em>Upload a repository or connect a GitHub URL &mdash; get an instant engineering audit with code quality metrics, architecture analysis, AI-powered insights, and actionable recommendations.</em></p>
  <br/>
  <a href="#features">Features</a> ·
  <a href="#architecture">Architecture</a> ·
  <a href="#tech-stack">Tech Stack</a> ·
  <a href="#screenshots">Screenshots</a> ·
  <a href="#getting-started">Getting Started</a> ·
  <a href="#api-endpoints">API</a>
  <br/><br/>
</div>

## 📖 About

**EngineerOS** is a full-stack engineering intelligence platform that audits codebases the way a senior engineer would. Point it at a ZIP archive or a public GitHub repository and it produces a comprehensive health report: quantitative quality metrics, detected code smells, architectural patterns, framework identification, and AI-generated improvement recommendations powered by LLMs.

It also supports **side-by-side repository comparison**, **downloadable reports**, and a built-in **freemium pricing module** (free scan quota with an upgrade path).

## ✨ Features

- 📦 **Flexible input** — analyze a repository via ZIP upload (drag & drop) or a public GitHub URL
- 📊 **Code quality metrics** — lines of code, comment density, function lengths, file size distribution, and more
- 🧹 **Code smell detection** — flags long functions, god classes, duplicated logic, dead code, and other maintainability hazards
- 🏛️ **Architecture analysis** — infers layering, module coupling, and project structure patterns
- 🔍 **Framework & language detection** — automatically identifies stacks, frameworks, and language composition
- 🤖 **AI-powered insights** — LLM-generated summaries, risk assessments, and prioritized recommendations (via OpenRouter)
- ⚖️ **Repository comparison** — diff the engineering health of two repos (ZIP or GitHub)
- 📄 **Report generation** — export analysis results as a shareable report
- 🎛️ **Freemium pricing module** — configurable free scan limit with usage tracking and a Pro tier
- ⚡ **Async task pipeline** — background analysis with polling-based results and caching for repeat scans

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      Frontend (React 19)                     │
│    Dashboard ─── Compare ─── Pricing                         │
│    UploadZone · HealthGauge · LanguageChart · ReportCard     │
└─────────────────────────────┬────────────────────────────────┘
                              │  REST (Axios)
┌─────────────────────────────▼────────────────────────────────┐
│                     Backend API (FastAPI)                    │
│   /upload  /analyze  /analyze/github  /analyze/ai            │
│   /compare /results  /report          /pricing               │
├──────────────────────────────────────────────────────────────┤
│                      Analysis Engine                         │
│   scanner → parser → metrics → smells → architecture → report│
│   framework_detector · ast_utils                             │
├──────────────────────────────────────────────────────────────┤
│                     Services & Utils                         │
│   ai_analysis (OpenRouter) · analysis_service · tasks        │
│   pricing · cache (diskcache) · zip_utils · file_utils       │
└──────────────────────────────────────────────────────────────┘
```

### Project structure

```
engineeros/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── router.py          # API route registration
│   │   │   └── routes/            # upload, analyze, github, compare,
│   │   │                          # ai_analysis, results, report, pricing
│   │   ├── engine/                # Core analysis engine: scanner, parser,
│   │   │                          # metrics, smells, architecture,
│   │   │                          # framework_detector, report
│   │   ├── models/
│   │   │   └── schemas.py         # Pydantic models
│   │   ├── services/              # ai_analysis, analysis_service,
│   │   │                          # tasks, pricing
│   │   ├── utils/                 # ast_utils, cache, file_utils, zip_utils
│   │   └── main.py                # FastAPI application entrypoint
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/                   # Axios client
│   │   ├── components/            # UploadZone, HealthGauge, LanguageChart…
│   │   ├── pages/                 # Dashboard, ComparePage, PricingPage
│   │   └── App.jsx
│   └── package.json
├── docs/
├── screenshots/
└── README.md
```

## 🛠️ Tech Stack

### Backend

| Technology | Purpose |
|------------|---------|
| [FastAPI](https://fastapi.tiangolo.com/) | High-performance async REST API |
| [Pydantic](https://docs.pydantic.dev/) | Request/response validation & schemas |
| [Python AST](https://docs.python.org/3/library/ast.html) | Static code parsing & analysis |
| [GitPython](https://gitpython.readthedocs.io/) | GitHub repository cloning |
| [httpx](https://www.python-httpx.org/) | Async LLM API communication |
| [diskcache](http://www.grantjenks.com/docs/diskcache/) | Persistent analysis caching |
| [Uvicorn](https://www.uvicorn.org/) | ASGI server |
| [OpenRouter](https://openrouter.ai/) | LLM access (DeepSeek, Claude, GPT, …) |

### Frontend

| Technology | Purpose |
|------------|---------|
| [React 19](https://react.dev/) | UI framework |
| [Vite](https://vite.dev/) | Build tool & dev server |
| [Tailwind CSS 4](https://tailwindcss.com/) | Styling |
| [Recharts](https://recharts.org/) | Data visualization (charts, gauges) |
| [Framer Motion](https://www.framer.com/motion/) | Animations |
| [react-dropzone](https://react-dropzone.js.org/) | Drag & drop ZIP uploads |
| [React Router](https://reactrouter.com/) | Client-side routing |
| [Lucide](https://lucide.dev/) | Icon library |

## 📸 Screenshots

> 🚧 Screenshots coming soon — add images to the `screenshots/` folder and they will appear here.

<!-- <p align="center">
  <img src="screenshots/dashboard.png" alt="Dashboard" width="800"/>
</p> -->

## 🚀 Getting Started

### Prerequisites

- **Python 3.13+**
- **Node.js 18+** and npm
- A free [OpenRouter API key](https://openrouter.ai/keys) *(optional — required only for AI insights)*

### 1. Clone the repository

```bash
git clone https://github.com/NullArchitect05/EngineerOs-.git
cd engineeros
```

### 2. Set up the backend

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# Install dependencies
pip install -r requirements.txt
```

Create a `backend/.env` file (see [Configuration](#configuration) for all options):

```env
LLM_API_KEY=your-openrouter-api-key
LLM_MODEL=deepseek/deepseek-chat-v3
LLM_BASE_URL=https://openrouter.ai/api/v1

FREE_SCAN_LIMIT=3
PRICE_PER_MONTH=5.99
MAX_UPLOAD_SIZE_MB=100
```

Start the API server:

```bash
uvicorn app.main:app --reload
```

The API is now live at **http://127.0.0.1:8000** — interactive docs at **http://127.0.0.1:8000/docs**.

### 3. Set up the frontend

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

Open **http://localhost:5173** in your browser and analyze your first repository! 🎉

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/upload/` | Upload a repository as a ZIP archive → returns a `file_id` |
| `POST` | `/analyze/` | Run a full engineering analysis on an uploaded repository |
| `POST` | `/analyze/github/` | Analyze a public GitHub repository by URL |
| `POST` | `/analyze/ai/{task_id}` | Enhance a completed analysis with AI insights |
| `GET`  | `/results/{task_id}` | Poll / fetch analysis results for a task |
| `POST` | `/compare/zip` | Compare two previously uploaded repositories |
| `POST` | `/compare/github` | Compare two GitHub repositories by URL |
| `GET`  | `/report/{task_id}` | Download the generated analysis report |
| `GET`  | `/pricing/status` | Get current client usage status and pricing info |
| `GET`  | `/pricing/check` | Check whether the client can perform another scan |
| `POST` | `/pricing/increment` | Increment the client's scan counter |

> All analysis-heavy endpoints run as **background tasks** — kick one off, then poll `/results/{task_id}` until completion.

## ⚙️ Configuration

Configure via `backend/.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_API_KEY` | OpenRouter API key for AI insights | — (AI features disabled if unset) |
| `LLM_MODEL` | LLM model identifier | `deepseek/deepseek-chat-v3` |
| `LLM_BASE_URL` | OpenAI-compatible base URL | `https://openrouter.ai/api/v1` |
| `FREE_SCAN_LIMIT` | Number of free scans per client | `3` |
| `PRICE_PER_MONTH` | Pro tier monthly price (USD) | `5.99` |
| `MAX_UPLOAD_SIZE_MB` | Maximum accepted ZIP upload size | `100` |

## 🧪 Running Tests

```bash
cd backend
pytest
```

## 🗺️ Roadmap

- [ ] User accounts & persisted scan history
- [ ] PDF export for reports
- [ ] Support for more languages beyond Python-centric analysis
- [ ] CI/CD health checks (lint config, test coverage detection)
- [ ] Team dashboards & trend tracking over time

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <sub>Built with ⚡ by <a href="https://github.com/NullArchitect05">NullArchitect05</a></sub>
</div>
