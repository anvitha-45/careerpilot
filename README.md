# CareerPilot AI 🧭
### *Agentic Job-Readiness & Application Copilot for Graduating Engineers*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React%2018%20%2B%20Vite-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![Tailwind CSS](https://img.shields.io/badge/Styles-Tailwind%20CSS-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Playwright](https://img.shields.io/badge/RPA-Playwright-2EAD33.svg?logo=playwright&logoColor=white)](https://playwright.dev)
[![Responsible AI](https://img.shields.io/badge/Design-Human--in--the--Loop-amber.svg)](#human-in-the-loop-hitl-architecture)
[![Cost](https://img.shields.io/badge/Operational%20Cost-%240.00%20(Free%20Tier)-brightgreen.svg)](#zero-cost-student-infrastructure)

---

## 💡 The Emotional Core: Combating "AI Anxiety"
In today's recruitment landscape, graduating engineering students face unprecedented anxiety regarding generative AI replacing entry-level software engineering roles. **CareerPilot AI inverts this dynamic: transforming *"AI is taking my job"* into *"here is an orchestrated multi-agent copilot using AI to fight for your job."*** 

Instead of leaving applicants helpless in front of automated ATS rejection filters or risking platform bans with blind auto-apply bots, CareerPilot puts state-of-the-art agentic AI directly in the student's corner.

---

## 🏛️ System Architecture

```text
                                CAREERPILOT AI
                                      │
                                      ▼
                             Upload Resume (PDF)
                                      │
                                      ▼
                            ┌───────────────────┐
                            │ Assessment Agent  │ <── GitHub & LeetCode APIs
                            └─────────┬─────────┘
                                      │
                             Empirical Skill Vector
                                      │
                                      ▼
                            ┌───────────────────┐
                            │ Job Match Engine  │ <── Ingested JDs (Naukri, LinkedIn, ATS)
                            └─────────┬─────────┘
                                      │
                             Ranked Target Jobs
                                      │
                                      ▼
                            ┌───────────────────┐
                            │  Gap & Learning   │ ──> Frequency Gaps (e.g. 73% of JDs)
                            │       Agent       │ ──> Free Resources (NPTEL, YouTube, Docs)
                            └─────────┬─────────┘
                                      │
                              Shortlisted Job
                                      │
                                      ▼
                            ┌───────────────────┐
                            │  Tailoring Agent  │ ──> CAR/STAR Bullet Transformations
                            │ (0% Hallucination)│ ──> Bespoke Cover Letter
                            └─────────┬─────────┘
                                      │
                                      ▼
                            ┌───────────────────┐
                            │ Application Agent │ ──> Playwright Browser Staging
                            │    (RPA Engine)   │ ──> DOM Field Pre-filling
                            └─────────┬─────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │ MANDATORY APPROVAL GATE  │  ◄── [STOP: No Auto-Submit]
                         │  (Human-in-the-Loop)     │  ◄── ToS & Anti-Bot Safe
                         └────────────┬─────────────┘
                                      │
                                      ▼ (Candidate reviews & manually confirms)
                            ┌───────────────────┐
                            │  Interview Agent  │ ──> Role-Specific Technical/Behavioral Q&A
                            │  (Mock Simulator) │ ──> Senior Evaluation & Rubric Feedback
                            └───────────────────┘
```

---

## 🤖 The 5 Specialized Multi-Agent Modules

| # | Agent Module | Primary Responsibility | Technical Core |
| :-: | :--- | :--- | :--- |
| **01** | **Assessment Agent** | Ingests PDF resume, GitHub repositories, and LeetCode solve counts to construct a multi-dimensional Skill Vector. | PDF text extraction (`pypdf`), skill taxonomy NER, public REST/GraphQL APIs. |
| **02** | **Job Discovery & Matching** | Computes cosine vector similarity between candidate skills and real postings across Indian & global tech hubs. | Vector embeddings, 4-factor scoring rubric, deterministic explainability. |
| **03** | **Gap & Learning Agent** | Discovers missing skills ranked strictly by empirical market frequency across target postings (not generic checklists). | Mathematical frequency weighting, NPTEL (IIT) & developer YouTube curation. |
| **04** | **Tailoring Agent** | Rewrites resume bullets using the Context-Action-Result (**CAR/STAR**) framework and crafts job-tuned cover letters. | Free-tier LLM inference (Groq/Gemini), programmatic zero-hallucination diffing. |
| **05** | **Application Agent (HITL)** | Launches browser automation to stage form fields on Naukri, LinkedIn, and ATS platforms; pauses at human review gate. | Playwright Chromium automation, DOM selector healing, session preservation. |
| **06** | **Interview Prep Agent** | Generates role-specific questions and simulates interactive mock interviews with instant evaluative scoring. | JD competency extraction, few-shot prompting, hiring manager rubrics. |

---

## 🛡️ Human-in-the-Loop (HITL) Architecture: A Strategic Virtue

> **Key Architectural Decision**: The Application Agent **STOPS** at a review-and-confirm step rather than fully auto-submitting.

### Why Fully Autonomous Applying Bots are an Anti-Pattern:
1. **Platform Terms of Service (ToS) Compliance**:
   * **LinkedIn User Agreement (Section 8.2)** explicitly bans automated applying bots, scrapers, and extensions.
   * **Naukri.com** actively blocks automated submission scripts and enforces IP/profile blacklisting.
   * Autonomous bots trigger bot tripwires (Cloudflare, Datadome, honeypots) that get the applicant's email permanently banned.
2. **Responsible AI Agent Design**:
   * Job applications include legally binding representations regarding citizenship, visa status, disability disclosures, and salary expectations. An AI agent cannot ethically sign legal representations on behalf of a human.
3. **The 95/5 Principle**:
   * CareerPilot automates **95%** of the cognitive overhead (market benchmarking, gap discovery, STAR bullet refinement, DOM locator pre-filling), while leaving the final **5%** approval click in the hands of the human candidate.

---

## 🎓 Academic & Research Merit: The 5 CS Pillars

This project bridges five core sub-disciplines of modern Computer Science:
1. **Natural Language Processing (NLP)**: Multi-format document text extraction, section identification, Named Entity Recognition (NER).
2. **Semantic Search & Vector Embeddings**: Cosine distance benchmarking of skill vectors against real-time job descriptions in vector space.
3. **Stateful Multi-Agent Orchestration**: Coordinating autonomous, specialized agents via LangGraph-inspired state graphs with typed state and checkpoints.
4. **Browser Automation & RPA**: Resilient DOM navigation, form-field heuristic mapping, and staged application pre-filling using Playwright.
5. **Generative LLM Prompt Engineering**: Few-shot CAR/STAR bullet generation, zero-hallucination verification diffing, and structured output formatting.

---

## 💰 Zero-Cost Student Infrastructure ($0.00 Cloud Spend)

Designed so that any engineering student can run CareerPilot completely free of cost:
* **LLM Inference**: Powered by Google Gemini 1.5 Flash (15 RPM free) or Groq Llama 3.3 70B (free tier).
* **Deterministic Fallback**: Built-in rule-based NLP engine guarantees 100% functionality even without API keys!
* **Database**: Resilient dual-mode database layer — connects to MongoDB when available, and automatically operates an embedded local document store (`careerpilot_store.json`) when offline.
* **Vector Search**: In-memory cosine similarity and vector matching (zero cloud vector DB hosting fees).
* **Browser Automation**: Local Chromium instance powered by Playwright.

---

## 🚀 Quickstart & Local Setup

### Prerequisites
* **Python 3.11+**
* **Node.js 18+** & `npm`

### 1. Clone & Setup Environment
```bash
git clone https://github.com/your-username/careerpilot-ai.git
cd careerpilot-ai
cp .env.example .env
```

### 2. Launch with One Click
#### On Windows (Command Prompt):
```cmd
run_dev.bat
```
#### On Windows (PowerShell):
```powershell
.\run_dev.ps1
```

#### Manual Startup:
```bash
# Terminal 1 — Backend
python -m pip install -r server/requirements.txt
python -m uvicorn server.main:app --reload --port 8000

# Terminal 2 — Frontend
cd client
npm install
npm run dev
```

Visit the application at: **`http://localhost:5173`**  
Explore the interactive API Docs at: **`http://localhost:8000/docs`**

---

## 📂 Project Structure

```text
careerpilot-ai/
├── client/                     # React 18 + Vite + Tailwind CSS Frontend
│   ├── src/
│   │   ├── api/                # Axios client with JWT interceptors
│   │   ├── components/         # Navbar, Sidebar, MultiAgentFlow, HumanReviewModal, etc.
│   │   ├── context/            # AuthContext & Candidate Profile State
│   │   ├── pages/              # Dashboard, Profile, Assessment, Jobs, Learning, Tailoring, etc.
│   │   ├── App.jsx             # React Router v6 navigation
│   │   └── main.jsx
│   └── package.json
├── server/                     # FastAPI + Multi-Agent Backend
│   ├── agents/                 # Assessment, GapLearning, Tailoring, Application, Interview
│   ├── models/                 # Pydantic Schemas (Profile, Job, SkillGap, Application, etc.)
│   ├── routers/                # Auth, Profile, Assessment, Jobs, Learning, Tailoring, etc.
│   ├── services/               # AI Service, Resume Parser, GitHub, LeetCode, Playwright
│   ├── seeds/                  # Real Tech Jobs & Curated NPTEL/YouTube Resources
│   ├── config.py               # Pydantic Settings & Environment
│   ├── database.py             # Hybrid MongoDB + Embedded Local Store Fallback
│   ├── main.py                 # FastAPI Application Entrypoint
│   └── requirements.txt
├── .gitignore
├── .env.example
├── LICENSE
├── README.md
├── spec.md                     # Comprehensive Architectural Specification (2,860+ lines)
├── run_dev.bat
└── run_dev.ps1
```

---

## 📜 License
Distributed under the MIT License. See [`LICENSE`](LICENSE) for more information.

