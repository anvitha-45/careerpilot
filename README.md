# CareerPilot AI 🧭
### *Agentic Job-Readiness & Application Copilot for Graduating Engineers*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React%2018%20%2B%20Vite-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![Tailwind CSS](https://img.shields.io/badge/Styles-Tailwind%20CSS-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Playwright](https://img.shields.io/badge/RPA-Playwright-2EAD33.svg?logo=playwright&logoColor=white)](https://playwright.dev)
[![Responsible AI](https://img.shields.io/badge/Design-Human--in--the--Loop-amber.svg)](#human-in-the-loop-hitl-architecture)
[![Documentation](https://img.shields.io/badge/Full%20Docs-DOCUMENTATION.md-purple.svg)](docs/DOCUMENTATION.md)
[![Video Walkthrough](https://img.shields.io/badge/Video-Live%20Demo-red.svg)](docs/videos/careerpilot_walkthrough.webm)

---

## 🎥 Live Video Walkthrough & Full Documentation

* 📖 **Comprehensive Project Documentation**: Check out [`docs/DOCUMENTATION.md`](docs/DOCUMENTATION.md) for full architectural specs, mathematical formulas, and viva defense notes.
* 🧭 **Beginner's Guided Tour Guide**: Check out [`APP_TOUR.md`](APP_TOUR.md).
* 📹 **Recorded Video Demo**: Watch the continuous live screen walkthrough at [`docs/videos/careerpilot_walkthrough.webm`](docs/videos/careerpilot_walkthrough.webm).

---

## 📸 Live Application Screenshots

| 🧭 Onboarding Tour Offer | 👤 Executive Dashboard |
| :---: | :---: |
| ![Onboarding Tour Offer](docs/screenshots/01_onboarding_tour_offer.png) | ![Dashboard Overview](docs/screenshots/04_dashboard_overview.png) |
| *Auto-offers interactive product tour on app launch* | *Readiness Gauge, Multi-Agent Flow & Target Roles* |

| ✍️ Tailoring Agent & ATS PDF Export | 🛡️ Mandatory Human Review Gate |
| :---: | :---: |
| ![Tailoring Agent](docs/screenshots/08_tailoring_agent_star_bullets.png) | ![Human Review Modal](docs/screenshots/10_human_review_checkpoint_modal.png) |
| *CAR/STAR Bullet Rewrites & 1-Click ATS PDF Export* | *Playwright browser staging stops at review checkpoint* |

| 🎓 Empirical Market Gap Analysis | 🎙️ JD-Tuned Mock Interview Simulator |
| :---: | :---: |
| ![Market Gap Analysis](docs/screenshots/07_market_gap_upskilling.png) | ![Interview Prep Simulator](docs/screenshots/11_interview_prep_simulator.png) |
| *Frequency-ranked gaps + free NPTEL / YouTube links* | *Company-targeted technical & behavioral evaluation* |

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
                            │                   │ ──> ATS Resume PDF Export Engine
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
| **04** | **Tailoring Agent & ATS PDF** | Rewrites resume bullets using the Context-Action-Result (**CAR/STAR**) framework and generates single-column ATS PDF resumes. | Free-tier LLM inference (Groq/Gemini), ReportLab Platypus, zero-hallucination diffing. |
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
   * In a real hiring workflow, submitting unreviewed applications leads to awkward interview failures when an applicant is questioned about unverified claims.
   * CareerPilot stages the form, uploads the tailored resume, pre-fills all inputs, and halts at the final **Human Review Gate**, ensuring 100% ethical and platform-safe operation.

---

## 💰 Zero-Cost Student Infrastructure

Built specifically so that any graduating student can clone, run, and deploy CareerPilot with **$0.00 cloud spend**:

* **Dual-Mode Database**:
  - **Primary**: MongoDB (via `pymongo` / `motor`).
  - **Zero-Dependency Fallback**: Asynchronous local JSON document store (`server/data/careerpilot_store.json`). If local `mongod` is not running, the system boots immediately in embedded store mode with 100% feature parity.
* **Three-Tier Free AI Provider Abstraction**:
  - **Tier 1**: Google Gemini 1.5 Flash (Free Tier API Key).
  - **Tier 2**: Groq LLaMA-3.3-70B (Free Ultra-Fast Inference).
  - **Tier 3**: Deterministic Offline Heuristic Engine (zero external API calls required).

---

## 🚀 Quickstart & Installation

### Option 1: One-Click Startup Script (Recommended)

#### Windows PowerShell:
```powershell
.\run_dev.ps1
```

#### Windows Command Prompt:
```cmd
run_dev.bat
```

### Option 2: Manual Step-by-Step Startup

#### 1. Backend Server:
```bash
python -m pip install -r server/requirements.txt
python -m uvicorn server.main:app --reload --port 8000
```

#### 2. Frontend Application:
```bash
cd client
npm.cmd install
npm.cmd run dev
```

Visit the application at: **`http://localhost:5173`**  
Explore the interactive API Docs at: **`http://localhost:8000/docs`**

---

## 📂 Repository Structure

```text
careerpilot-ai/
├── client/                     # React 18 + Vite + Tailwind CSS Frontend
│   ├── src/
│   │   ├── api/                # Axios client with JWT interceptors
│   │   ├── components/         # Navbar, MultiAgentFlow, HumanReviewModal, AppTourModal, etc.
│   │   ├── context/            # AuthContext & TourContext
│   │   ├── pages/              # Dashboard, Profile, Assessment, Jobs, Learning, Tailoring, etc.
│   │   ├── App.jsx             # React Router v6 navigation
│   │   └── main.jsx
│   └── package.json
├── server/                     # FastAPI + Multi-Agent Backend
│   ├── agents/                 # Assessment, GapLearning, Tailoring, Application, Interview
│   ├── models/                 # Pydantic Schemas (Profile, Job, SkillGap, Application, etc.)
│   ├── routers/                # Auth, Profile, Assessment, Jobs, Learning, Tailoring, etc.
│   ├── services/               # AI Service, Resume Parser, PDF Export, GitHub, LeetCode, Playwright
│   ├── seeds/                  # Real Tech Jobs & Curated NPTEL/YouTube Resources
│   ├── config.py               # Pydantic Settings & Environment
│   ├── database.py             # Hybrid MongoDB + Embedded Local Store Fallback
│   ├── main.py                 # FastAPI Application Entrypoint
│   └── requirements.txt
├── docs/                       # Comprehensive Documentation, Screenshots & Videos
│   ├── DOCUMENTATION.md        # Full Architectural & Academic Viva Guide
│   ├── screenshots/            # 12 Live High-Resolution Screen Captures
│   └── videos/                 # Recorded Video Walkthrough (careerpilot_walkthrough.webm)
├── APP_TOUR.md                 # Interactive 8-Step App Tour Guide
├── spec.md                     # Comprehensive Architectural Specification (2,860+ lines)
├── run_dev.bat                 # One-click Windows CMD startup
├── run_dev.ps1                 # One-click PowerShell startup
├── .gitignore
├── .env.example
├── LICENSE                     # MIT License
└── README.md
```

---

## 📜 License
Distributed under the MIT License. See [`LICENSE`](LICENSE) for more information.
