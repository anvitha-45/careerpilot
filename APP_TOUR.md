# CareerPilot AI — Interactive App Tour & Beginner's Guide 🧭

Welcome to **CareerPilot AI**, an agentic career copilot designed for graduating computer science and engineering students.

Unlike simple form-fillers or chatbots, CareerPilot coordinates **5 specialized autonomous AI agents** that guide you step-by-step from raw resume parsing to real-market skill gap upskilling, resume tailoring, staged browser applications, and JD-specific mock interviews.

---

## ⚡ 10-Second Quickstart & Automatic Tour Offer

1. Launch both backend and frontend with a single command:
   * **Windows Command Prompt**: `run_dev.bat`
   * **Windows PowerShell**: `.\run_dev.ps1`
2. Open your browser at **`http://localhost:5173`**.
3. **Automatic Product Tour Offer**:
   * As soon as you open the app, CareerPilot automatically presents a friendly onboarding modal: *"Would you like a quick product tour?"*
   * Click **"Start Product Tour (2 min)"** to take the guided 8-step walkthrough of the product and how the 5 agents work—even before signing in!
   * Or click **"One-Click Instant Demo Login"** on the login screen to enter the app immediately with pre-loaded demo telemetry.
   * You can re-open the tour at any time by clicking the **"Product Tour"** button in the top navigation bar or the Dashboard banner.

---

## 🗺️ Visual Architecture of the 7-Step User Journey

```text
 ┌────────────────┐       ┌─────────────────┐       ┌─────────────────┐
 │ 1. Upload      │ ────> │ 2. Assessment   │ ────> │ 3. Job Match    │
 │    Resume PDF  │       │    Agent        │       │    Engine       │
 └────────────────┘       └─────────────────┘       └────────┬────────┘
                                                             │
 ┌────────────────┐       ┌─────────────────┐                │
 │ 6. Mock        │ <──── │ 5. Staging &    │ <──────────────┘
 │    Interview   │       │    HITL Gate    │       ┌─────────────────┐
 │    Prep Agent  │       │    (Playwright) │ <──── │ 4. Tailoring    │
 └────────────────┘       └─────────────────┘       │    Agent (STAR) │
                                                    └─────────────────┘
```

---

## 📍 Screen-by-Screen Guided Tour

### Screen 1: Overview Dashboard (`/`)
* **Core Purpose**: Central command center giving you an instantaneous pulse on your career readiness.
* **What You See**:
  * **Empirical Readiness Score Meter**: Circular score (0–100%) showing your market competitiveness tier (e.g., *Top 20% of 2026 Batch*).
  * **Multi-Agent Execution Graph**: Live interactive status of all 5 autonomous modules.
  * **Top Recommended Roles**: Scored and ranked by vector cosine similarity against real engineering roles in Bangalore, Hyderabad, Pune, and Remote.
  * **Market Skill Gap Alert**: Immediate notification of the highest-frequency missing technologies across your target companies.

---

### Screen 2: Candidate Profile & Ground Truth (`/profile`)
* **Core Purpose**: Establishes your verified factual dataset.
* **What You Do**:
  * Drag-and-drop your resume PDF into the upload area.
  * Connect your public **GitHub** username (e.g., `torvalds`) and **LeetCode** username (e.g., `neetcode`).
  * Customize target engineering roles (*SDE-1, Backend Developer, Full Stack Engineer*) and geographic preferences.
* **What AI Does Under the Hood**:
  * Runs the **Resume NLP Parser (`pypdf`)** to extract contact information, education, and technical skills across 5 categories without hallucinating.
  * Queries public GitHub REST endpoints for repository languages and LeetCode GraphQL for solved problem distributions (Easy/Medium/Hard).
* **Why It Matters**:
  * **Strict Zero-Hallucination Anchor**: This establishes your immutable ground-truth skill set. Downstream agents are programmatically forbidden from inventing fake degrees or technologies you've never used.

---

### Screen 3: Agent 01 — Skill Assessment (`/assessment`)
* **Core Purpose**: Transparent verification of your technical profile.
* **What You See**:
  * **Categorized Skill Vector**: Pill matrix displaying Core Languages, Frameworks, Databases, DevOps & Cloud, and CS Foundations.
  * **GitHub Signal Card**: Real-time stats on public repositories, stars, and language distribution.
  * **LeetCode Signal Card**: Problem-solving breakdown across Easy, Medium, and Hard tiers, plus global contest ranking.
  * **Market Alignment Benchmark**: Shows the percentage overlap between your current skills and active job descriptions in your region.

---

### Screen 4: Agent 02 — Job Explorer & Semantic Matching (`/jobs`)
* **Core Purpose**: Real-time job discovery with explainable AI scoring.
* **What You See**:
  * Real job postings ingested from **LinkedIn**, **Naukri**, and **Greenhouse ATS** (e.g., Swiggy, Razorpay, PhonePe, Postman).
  * **Match Score Badge**: Calculated via vector cosine similarity and 4-factor weighting (Required Skills, Preferred Skills, Role Title Alignment, Location Compatibility).
  * **Green / Red Skill Tags**: Instantly see which required skills you already have (green) and which you are missing (red).
  * **Semantic Match Reason**: Plain-English explanation detailing why you received that score and how to improve it.
* **Interactive Tool**: Click **"Import Custom JD"** to paste any job description from the internet. The NLP agent parses it and benchmarks your profile in real-time.

---

### Screen 5: Agent 03 — Market-Driven Upskilling (`/learning`)
* **Core Purpose**: Practical, high-yield learning recommendations (anti-generic).
* **The Problem It Solves**: Unlike traditional career advice that spits out generic checklists, CareerPilot computes:
  $$\text{Market Demand Frequency} = \frac{\text{Postings requiring skill } s}{\text{Total active target postings}} \times 100\%$$
* **What You See**:
  * **Empirical Ranking**: Gaps tagged as **CRITICAL** ($\ge 50\%$ of JDs) or **HIGH** ($30\text{–}49\%$ of JDs).
  * **100% Free Curated Resources**:
    * **NPTEL / SWAYAM**: Academic courses from IIT professors for core computer science fundamentals.
    * **Developer YouTube Playlists**: Hands-on practical video series (Striver TakeUForward for DSA, freeCodeCamp, NeetCode).
    * **Official Documentation**: Authoritative tutorials (Spring.io, FastAPI docs, MDN).
  * **Personalized 4-Week Study Roadmap**: Week-by-week actionable plan to build portfolio projects that permanently close your skill gaps.

---

### Screen 6: Agent 04 — Resume Tailoring & CAR/STAR Generator (`/tailoring`)
* **Core Purpose**: Contextual bullet point rewrites and job-tuned cover letters with zero hallucination.
* **What You Do**: Select any target job (e.g., *Swiggy SDE-1*) and click "Tailor Resume".
* **What AI Does Under the Hood**:
  * Rephrases your resume bullets using the **Context-Action-Result (CAR/STAR)** formula, adding strong action verbs and quantifiable impact.
  * Synthesizes a bespoke cover letter directly connecting your actual GitHub projects to the company's tech stack.
  * **Programmatic Zero-Hallucination Verification**: Deterministic verification function scans generated text to ensure every single technical term exists in your verified ground truth.
* **Result**: A bullet-by-bullet side-by-side diff showing the original vs. tailored bullet point and the reasoning behind each enhancement.

---

### Screen 7: Agent 05 — Application Staging & Human Review Gate (`/applications`)
* **Core Purpose**: The innovative core combining browser automation with responsible AI safety.
* **The Design Decision**:
  * Blind auto-submit bots violate **LinkedIn User Agreement Section 8.2** and **Naukri Terms of Use**, resulting in applicant account bans and recruiter blacklisting.
  * CareerPilot solves this through **Responsible AI Agent Design**:
    1. Click **"Launch Browser Staging"**.
    2. **Playwright RPA Engine** opens the browser and pre-fills form fields (Name, Email, Phone, GitHub, attaches tailored resume PDF).
    3. **The system intentionally HALTS** and triggers the **Mandatory Human Review Gate Modal**.
    4. The candidate inspects the pre-filled fields, solves any CAPTCHAs, and **manually confirms submission**.
* **Result**: 95% of tedious form filling is automated, while the applicant remains 100% compliant, unbanned, and legally accountable.

---

### Screen 8: Agent 06 — JD-Specific Mock Interview Simulator (`/interview`)
* **Core Purpose**: Realistic placement interview practice tailored to the target role.
* **What You Do**:
  * Select a target job to generate 4 role-specific questions across **Technical Architecture, Project Deep Dive, CS Foundations, and Behavioral**.
  * Type your structured answers into the practice interface.
* **What AI Does Under the Hood**:
  * Evaluates your responses against a **Senior Hiring Manager Rubric**.
  * Assigns numerical scores (0–10 per question, 0–100 overall) and a readiness level (`READY`, `PROMISING`, `NEEDS_PREPARATION`).
  * Highlights your strengths, critical gaps, and provides **Senior Benchmark Model Answers** for each question.

---

### Screen 9: Career Analytics & Telemetry (`/analytics`)
* **Core Purpose**: Quantitative progress tracking over time.
* **What You See**:
  * **Application Funnel Conversion**: Tracks applications transitioning through `Shortlisted` ➔ `Staged (Review)` ➔ `User Submitted` ➔ `Interview` ➔ `Offer`.
  * **Multi-Agent Coordination Telemetry**: Confirms LangGraph state checkpoints and agent health.
  * **Cohort Benchmark**: Shows where you stand relative to the 2026 engineering graduate cohort.

---

## 🎓 Viva & Project Presentation Cheat Sheet

| Question | Winning Defense / Answer |
| :--- | :--- |
| **Why not just use a simple ChatGPT prompt or form filler?** | "A single prompt suffers from context pollution, compounding hallucinations, and monolithic failure. CareerPilot is a stateful multi-agent system (LangGraph) with 5 decoupled agents, persistent checkpoints, and independent failure isolation." |
| **Why doesn't the system automatically click the final Submit button?** | "Fully autonomous submission violates LinkedIn Section 8.2 and Naukri ToS, triggering bot detection and banning student accounts. In compliance with **Responsible AI Agent Design**, CareerPilot automates 95% of the preparation while enforcing a mandatory Human-in-the-Loop review gate for the final binding action." |
| **How do you guarantee zero hallucination in resume tailoring?** | "We implement a **Strict Grounded Verification Diff**. The candidate's resume and verified GitHub/LeetCode data form an immutable ground truth. Before tailored outputs are saved, a deterministic scanner verifies that no unearned technologies or fake metrics were introduced." |
| **How does this run at zero operational cost?** | "Engineered for $0.00 cloud spend using Google Gemini 1.5 Flash and Groq free tiers, local in-memory cosine vector matching, local Playwright browser automation, and a hybrid database that works offline without cloud hosting." |

