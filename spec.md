# PROJECT SPECIFICATION FOR A CODING AGENT

## Project Name

**CareerPilot AI — Agentic Job-Readiness & Application Copilot**

---

## PURPOSE OF THIS DOCUMENT

Hand this specification to a coding agent and it should be able to build CareerPilot AI from scratch with the functionality defined below.

CareerPilot AI is an **agentic job-readiness and application copilot for graduating engineers**.

### The Emotional Core: Combating "AI Anxiety" in Engineering Students
In today's recruitment landscape, graduating computer science and engineering students face unprecedented anxiety regarding generative AI replacing entry-level software engineering roles. CareerPilot AI inverts this narrative: **transforming "AI is taking my job" into "here is an orchestrated multi-agent copilot using AI to fight for your job."** Rather than leaving students helpless in front of automated ATS rejection filters, CareerPilot puts state-of-the-art agentic AI directly in their corner.

### Academic & Technical Merit: The 5 Computer Science Pillars
CareerPilot is designed not merely as a practical utility, but as a rigorous capstone / final-year engineering system that bridges five foundational sub-disciplines of modern Computer Science:
1. **Natural Language Processing (NLP) & Information Extraction**: Multi-format unstructured resume parsing (PDF/DOCX), named entity recognition (NER) for skill/experience taxonomy extraction.
2. **Semantic Search & Vector Embeddings**: Cosine similarity benchmarking of candidate skill vectors against real-time job descriptions embedded in high-dimensional vector spaces.
3. **Stateful Multi-Agent Orchestration**: Coordinating autonomous, specialized agents via graph workflows (LangGraph / CrewAI) with persistent state management, conditional branching, and checkpointing.
4. **Browser Automation & Robotic Process Automation (RPA)**: Resilient DOM navigation, form-field heuristic mapping, and staged application pre-filling using Playwright / Selenium.
5. **Generative LLM Prompt Engineering & Free-Tier Optimization**: Tailored bullet point synthesis using the CAR/STAR framework, JD-derived interview generation, and structured outputs running on zero-cost free-tier infrastructure.

### The Multi-Agent Pipeline
The system takes a candidate's:

* Resume (PDF/DOCX)
* GitHub public profile & repositories
* LeetCode public performance metrics
* Target roles & target region
* Current self-reported and extracted skills

and coordinates a multi-agent pipeline (using LangGraph or CrewAI) that:

1. **Assessment Agent**: Parses the resume + GitHub/LeetCode profiles via public endpoints, builds an empirical skill vector, and benchmarks it against real scraped/aggregated job postings for target roles/regions.
2. **Gap & Learning Agent**: Identifies missing skills ranked strictly by real-market posting frequency (not generic static checklists) and recommends curated free learning resources (NPTEL, YouTube channels, official documentation).
3. **Tailoring Agent**: For each shortlisted job, rewrites resume bullet points to truthfully emphasize JD alignment and generates a bespoke cover letter using free-tier LLMs (Gemini / Groq).
4. **Application Agent (Innovative Core)**: Uses browser automation (Playwright/Selenium) to navigate job portals (e.g., Naukri, LinkedIn, ATS forms), pre-fill and stage application fields, and halts at a mandatory review-and-confirm checkpoint.
5. **Interview Prep Agent**: Synthesizes probable technical and behavioral questions derived from the specific JD and conducts interactive mock Q&A with evaluation and feedback.
6. **Progress & Analytics Agent**: Tracks skill progression, application stages, and interview feedback loops.

The product is **not a chatbot** and **not a simple form-filler**.

It is a workflow orchestration system where specialized agents perform clearly defined tasks, validate intermediate representations, pass structured state down a directed graph, and respect human oversight.

---

# IMPORTANT WORKSPACE INSTRUCTIONS

The coding agent MUST follow these rules.

### 1. Clean project separation

Use:

```text
client/
server/
```

All frontend code must remain inside `client/`.

All backend code must remain inside `server/`.

Never create:

```text
frontend/
backend/
```

unless explicitly instructed.

---

### 2. Human-in-the-loop (HITL) is mandatory & strategic

The Application Agent MUST NOT automatically submit applications.

The maximum permitted automation flow is:

```text
Find Job
   ↓
Analyze Job
   ↓
Tailor Resume
   ↓
Generate Cover Letter
   ↓
Open Application in Staging Browser
   ↓
Pre-fill / Stage Form Fields
   ↓
HUMAN REVIEW & APPROVAL GATE
   ↓
User manually reviews & confirms/submits
```

The system must never automatically trigger the final Submit/Apply button.

#### Why HITL is an Architectural Virtue, Not a Compromise:
1. **Platform Terms of Service (ToS) Compliance**: Leading recruitment platforms (e.g., LinkedIn User Agreement Section 8.2, Naukri.com Terms of Use, Workday, Greenhouse) strictly forbid automated bot submissions, scrapers, and headless applying scripts. Automated mass-submit bots trigger IP bans, CAPTCHA blocks, and candidate profile blacklisting.
2. **Responsible AI Agent Design**: In academic capstones and enterprise AI, autonomous agents that perform unreviewed external side effects (like binding job submissions) are an antipattern. Integrating an explicit approval checkpoint proves mastery of safe, ethical, and defensible agent design.
3. **Accuracy & Agency**: LLM-tailored fields and auto-filled data must be human-verified to prevent submitting inaccurate answers to legal or compliance screening questions (e.g., visa status, disability disclosures, salary expectations).

---

### 3. No fabricated candidate information

AI agents MUST NOT invent:

* Skills
* Projects
* Work experience
* Education
* Certifications
* Job experience
* Achievements
* GitHub contributions
* LeetCode statistics

Tailoring may improve wording and ordering, but the candidate's factual information must remain truthful.

---

### 4. Public profile data only

GitHub and LeetCode information must use publicly accessible profile information or officially available APIs/endpoints where supported.

Do not bypass:

* Authentication
* CAPTCHA
* Rate limits
* Security mechanisms
* Private profiles
* Access restrictions

---

### 5. Job portal automation safety (Naukri, LinkedIn, ATS)

Browser automation is strictly limited to **staging and pre-filling applications**.

The system must stop before final submission.

If a portal prevents automation or requires CAPTCHA/login verification, the workflow must pause, alert the user, and pass control to the user to continue manually in an open browser session.

---

### 6. Zero-Cost AI provider abstraction for student projects

AI calls must be isolated behind a unified service layer (`server/services/ai_service.py`).

To ensure zero financial burden for a student/capstone engineering project, the system must run on generous free tiers:

* **Google Gemini API Free Tier**: Gemini 1.5 Flash (15 RPM / 1M TPM free)
* **Groq API Free Tier**: Llama 3.3 70B Versatile / Llama 3.1 8B (ultra-fast inference, free tier)
* **Local Embeddings**: `sentence-transformers` (`all-MiniLM-L6-v2`) or Gemini Embeddings free tier
* **Vector Search**: Local in-memory / disk FAISS index (zero cloud vector DB cost)
* **Database**: MongoDB Community Edition (local) or MongoDB Atlas M0 Free Tier (512MB free)

The application must switch providers via environment configuration without code changes.

A deterministic rule-based fallback must be available if external LLM APIs experience rate limits or network outages.

---

### 7. Environment variables

All secrets must use `.env`.

Examples:

```text
GEMINI_API_KEY=
GROQ_API_KEY=
JWT_SECRET=
DATABASE_URL=
GITHUB_TOKEN=
```

Never commit secrets.

---

# PROJECT OVERVIEW

CareerPilot AI is a full-stack agentic system designed for graduating engineering students who want to become job-ready and apply for software roles more effectively.

The system combines:

* NLP
* Resume parsing
* Skill extraction
* Semantic job matching
* Embeddings
* Multi-agent orchestration
* LLM prompting
* Learning-resource recommendation
* Resume tailoring
* Browser automation
* Interview preparation
* Human-in-the-loop approval

The central pipeline is:

```text
Candidate Profile
       ↓
Assessment Agent
       ↓
Job Discovery
       ↓
Gap & Learning Agent
       ↓
Tailoring Agent
       ↓
Human Review
       ↓
Application Agent
       ↓
Interview Prep Agent
       ↓
Progress / Feedback
```

The system should continuously improve recommendations based on the candidate's:

* target roles
* applications
* interview outcomes
* rejected applications
* skill gaps
* learning progress

---

# CORE DIFFERENTIATOR

CareerPilot is not a resume generator.

It is an **agentic career workflow**.

The system should answer:

> "Given my current profile and the jobs I want, what should I learn, which jobs should I target, how should I apply, and how should I prepare for the interview?"

Instead of:

```text
Resume → Chatbot → Response
```

CareerPilot performs:

```text
Resume
  ↓
Skill Vector
  ↓
Real Job Market
  ↓
Skill Benchmark
  ↓
Skill Gaps
  ↓
Learning Plan
  ↓
Job Shortlist
  ↓
Tailored Application
  ↓
Human Approval
  ↓
Application Staging
  ↓
Interview Preparation
```

---

# TECH STACK

## Frontend

Use:

* React 18
* Vite
* Tailwind CSS
* React Router
* TanStack React Query
* Zustand
* React Hook Form
* Axios
* Lucide React

Frontend language:

```text
JavaScript / JSX
```

---

# Backend

Use:

* Python 3.11+
* FastAPI
* Pydantic
* Uvicorn
* MongoDB
* PyMongo
* JWT authentication
* bcrypt/passlib
* Playwright
* HTTPX

---

# AI / AGENT LAYER

Primary orchestration framework:

```text
LangGraph
```

AI providers:

```text
Gemini
Groq
```

Embedding support:

```text
Gemini Embeddings
```

or another configurable embedding provider.

Vector search:

```text
FAISS
```

The agent layer must be independent from the API controllers.

---

# EXTERNAL DATA SOURCES

CareerPilot may integrate with:

### GitHub

Used for:

* repositories
* languages
* repository activity
* stars
* forks
* contribution information where publicly available

### LeetCode

Used only for publicly available information where technically and legally permitted.

Possible information:

* solved count
* easy/medium/hard distribution
* contest information where available

### Job sources & Regional Ingestion

CareerPilot ingests real, live job postings aligned with the candidate's target roles and target geographic region (e.g., India: Bengaluru, Hyderabad, Pune, NCR, Remote, or global).

The system supports:

1. **Regional Portals & Feeds**:
   * **Naukri & LinkedIn**: Ingestion via public job feeds, RSS/Atom, permitted scrapers, or direct URL import.
   * **Campus & Entry-level Portals**: Internshala, Unstop, Wellfound (AngelList).
   * **Company ATS Portals**: Direct parsing of Greenhouse, Lever, Ashby, and Workday public job links.
2. **Standard Job APIs**: Adzuna, Remotive, Arbeitnow, Jooble public developer APIs.
3. **Manual / Pasted Job Descriptions**: Paste any raw JD text or drop a job link for instant parsing, normalization, and on-demand matching.
4. **Target Role & Region Filtering**:
   * Target roles: e.g., SDE-1 / Fresher, Backend Engineer, Frontend Engineer, Full Stack Developer, Data Analyst.
   * Target regions: Filtered by city tier, country, and remote/hybrid eligibility.

All ingested postings are scrubbed, deduplicated, and stored in MongoDB with full-text and vector embeddings for semantic matching.

---

# USER WORKFLOW

## Step 1 — Create Account

User registers with:

```text
Name
Email
Password
```

---

## Step 2 — Build Profile

User provides:

```text
Resume PDF
GitHub username
LeetCode username
Target roles
Target location
Preferred work mode
Experience level
```

Example:

```text
Target roles:
- Software Engineer
- Backend Developer
- AI Engineer

Location:
India

Work mode:
Remote / Hybrid

Experience:
Fresher
```

---

# STEP 3 — ASSESSMENT AGENT

## Assessment Agent

File:

```text
server/agents/assessment_agent.py
```

### Responsibilities

The Assessment Agent builds the candidate's current skill profile.

Inputs:

```text
Resume
GitHub profile
LeetCode profile
Candidate preferences
```

Outputs:

```json
{
  "skills": [],
  "skillVector": {},
  "projects": [],
  "experience": [],
  "education": [],
  "githubSummary": {},
  "leetcodeSummary": {},
  "strengths": [],
  "weaknesses": [],
  "targetRoles": []
}
```

---

## Resume Processing

Extract:

* Skills
* Projects
* Experience
* Education
* Certifications
* Achievements
* Programming languages
* Frameworks
* Databases
* Tools

The parser must preserve the original resume text.

---

# SKILL VECTOR

Represent skills in a structured form.

Example:

```json
{
  "java": 0.8,
  "python": 0.7,
  "sql": 0.8,
  "dsa": 0.6,
  "react": 0.5,
  "mongodb": 0.5,
  "git": 0.8
}
```

Scores represent evidence/confidence rather than claiming professional proficiency.

The system must distinguish between:

```text
Mentioned
Practiced
Project Evidence
Strong Evidence
```

---

# GITHUB ANALYSIS

The Assessment Agent should analyze public GitHub information.

Possible signals:

```text
Repository count
Languages
Recent activity
Project topics
README content
Stars
Forks
Technology usage
```

Example:

```json
{
  "languages": ["Java", "Python", "HTML"],
  "repositories": 12,
  "relevantProjects": 4,
  "technologyEvidence": [
    "Java",
    "Python",
    "MongoDB"
  ]
}
```

The system must not convert repository existence alone into a claim of expertise.

---

# LEETCODE ANALYSIS

Where publicly available, extract:

```text
Problems solved
Easy
Medium
Hard
Contest participation
Problem-solving activity
```

Example:

```json
{
  "totalSolved": 180,
  "easy": 80,
  "medium": 85,
  "hard": 15
}
```

These statistics should contribute to the assessment but should not be treated as direct evidence of mastery.

---

# JOB DISCOVERY

CareerPilot should collect job postings relevant to the candidate's target roles.

Each job should contain:

```json
{
  "title": "",
  "company": "",
  "location": "",
  "description": "",
  "requiredSkills": [],
  "preferredSkills": [],
  "experienceLevel": "",
  "applyUrl": "",
  "source": "",
  "postedDate": null
}
```

---

# JOB NORMALIZATION

Different job sources use different terminology.

Normalize skills:

```text
React.js → react
ReactJS → react
Node.js → node
Mongo DB → mongodb
Java SE → java
```

Store the normalized representation while preserving original job text.

---

# MATCHING / BENCHMARKING

CareerPilot must compare candidate skills against actual job requirements.

Example:

```text
Candidate:
Java
Python
SQL
Git
MongoDB

Job:
Java
Spring Boot
SQL
Docker
AWS
```

Result:

```text
Matched:
Java
SQL

Missing:
Spring Boot
Docker
AWS
```

---

# MATCH SCORE

Each job receives a score from:

```text
0–100
```

The score should consider:

```text
Required skill overlap
Preferred skill overlap
Role relevance
Experience compatibility
Location compatibility
Project evidence
```

Example:

```text
Skill Match       65
Role Relevance    15
Project Evidence  10
Location          10
--------------------
Final Score       100
```

The exact formula must be implemented in one service and not scattered throughout controllers.

---

# GAP & LEARNING AGENT

File:

```text
server/agents/gap_learning_agent.py
```

## Responsibilities

Identify missing skills that the candidate must acquire to maximize job readiness, strictly ranked by empirical frequency across real-world target job postings.

### Empirical Frequency Ranking (Anti-Generic Philosophy)
Unlike standard career portals that spit out generic, static checklists, the Gap & Learning Agent computes real-market urgency:

$$\text{Market Demand Frequency}(s) = \frac{\text{Count of target postings requiring } s}{\text{Total target postings analyzed } (N)} \times 100\%$$

The agent calculates:
1. **Target Postings Cluster**: Ingests $N$ real job postings matching user's target role (e.g., "SDE-1", "Backend Developer") and location (e.g., "India / Remote").
2. **Skill Extraction & Aggregation**: Extracts all required and preferred technologies across the cluster.
3. **Candidate Diff**: Computes $\text{Gaps} = \text{Skills}_{\text{market}} \setminus \text{Skills}_{\text{candidate}}$.
4. **Prioritization Score**:
   * **Tier 1 (CRITICAL)**: Appears in $\ge 60\%$ of postings, absent from candidate profile.
   * **Tier 2 (HIGH)**: Appears in $30\% - 59\%$ of postings.
   * **Tier 3 (GOOD TO HAVE)**: Appears in $10\% - 29\%$ of postings.

Example:
Suppose 30 relevant postings contain:

```text
Java           27 (90%) -> CRITICAL GAP (if missing)
SQL            25 (83%) -> CRITICAL GAP (if missing)
Spring Boot    22 (73%) -> CRITICAL GAP (if missing)
Docker         18 (60%) -> HIGH GAP (if missing)
AWS            12 (40%) -> HIGH GAP (if missing)
Kubernetes      4 (13%) -> GOOD TO HAVE (low priority for freshers)
```

The system tells the student: *"Focus on Spring Boot and Docker this week—they appear in 73% and 60% of campus postings. Do not waste time on Kubernetes yet (only 13%)."*

---

# SKILL GAP OUTPUT

```json
{
  "skill": "Spring Boot",
  "priority": "CRITICAL",
  "jobFrequency": 22,
  "percentage": 73.3,
  "marketContext": "Appears in 22 of 30 analyzed SDE-1 backend postings in your target region.",
  "currentCandidateEvidence": "Java syntax detected, but zero MVC or REST API project evidence.",
  "suggestedAction": "Build a production-style REST API with Spring Data JPA and MySQL.",
  "estimatedLearningTime": "7-10 days",
  "recommendedResources": [
    {
      "provider": "Official Documentation",
      "title": "Spring Boot Official Guides — Building a RESTful Web Service",
      "url": "https://spring.io/guides/gs/rest-service/",
      "type": "DOCUMENTATION",
      "cost": "FREE",
      "timeCommitment": "2 hours"
    },
    {
      "provider": "NPTEL",
      "title": "IIT Kharagpur / SWAYAM: Software Engineering & Enterprise Java Design",
      "url": "https://nptel.ac.in/courses",
      "type": "ACADEMIC_COURSE",
      "cost": "FREE",
      "timeCommitment": "10 hours"
    },
    {
      "provider": "YouTube",
      "title": "freeCodeCamp / Amigoscode — Full Spring Boot 3 Tutorial",
      "url": "https://www.youtube.com/results?search_query=spring+boot+3+full+course",
      "type": "PRACTICAL_VIDEO",
      "cost": "FREE",
      "timeCommitment": "4 hours"
    }
  ]
}
```

---

# LEARNING RESOURCE AGENT

Curate high-yield, 100% free learning resources tailored to the student:

1. **NPTEL (National Programme on Technology Enhanced Learning / SWAYAM)**:
   * Rigorous, university-accredited video lectures from IIT professors.
   * Ideal for core CS foundations (DBMS, Computer Networks, Operating Systems, Compiler Design).
2. **Curated Developer YouTube Channels**:
   * Practical, hands-on, and interview-oriented playlists.
   * Key domains: Striver (TakeUForward) for DSA, NeetCode for algorithm patterns, freeCodeCamp and Traversy Media for full-stack frameworks, Hussein Nasser for backend engineering.
3. **Authoritative Official Documentation**:
   * First-party documentation (MDN Web Docs, Python.org, React.dev, Spring.io, FastAPI docs).
   * Teaches students industry-standard reading skills rather than relying on outdated blog snippets.
4. **Hands-on Capstone Projects**:
   * Actionable project blueprints designed to be committed to GitHub to turn the gap into verified proof.

The system strictly avoids fabricating URLs and validates link integrity before presenting to candidates.

---

# LEARNING PLAN

Generate a personalized plan.

Example:

```text
Week 1
├── Spring Boot fundamentals
├── REST APIs
└── Build CRUD API

Week 2
├── SQL optimization
├── Database integration
└── Add authentication

Week 3
├── Docker basics
└── Containerize project
```

The plan should be based on the candidate's actual gaps.

---

# TAILORING AGENT

File:

```text
server/agents/tailoring_agent.py
```

## Responsibilities

For each shortlisted target job:
1. **Analyze Target JD**: Extract core keywords, technical competencies, and architectural patterns demanded.
2. **Contextual Resume Bullet Rewriting (CAR/STAR Framework)**:
   * Rephrase candidate's existing experience and project bullets using the **Context - Action - Result (CAR / STAR)** formula:
     * *Weak Bullet*: "Built a backend using Node.js and MongoDB."
     * *Tailored Bullet*: "Engineered a scalable Node.js/Express REST API integrated with MongoDB, implementing JWT authentication and indexed queries to reduce lookup latency by 35%."
   * Re-rank projects and technical skills so the most JD-relevant items appear at the top of the resume.
3. **Zero-Cost Free-Tier LLM Architecture**:
   * Uses **Groq API Free Tier (Llama 3.3 70B Versatile)** or **Google Gemini 1.5 Flash Free Tier** via prompt templates with strict system instructions and structured JSON response formatting.
   * Zero cost per run for student users.
4. **Strict Zero-Hallucination Policy**:
   * The agent runs a programmatic verification diff: every skill keyword in the tailored resume must exist in the candidate's original verified profile.
   * Never fabricates degrees, GPA, dates, former employers, or technologies never touched.
5. **Job-Tuned Cover Letter Synthesis**:
   * Generates a concise, high-impact cover letter connecting the student's actual GitHub/LeetCode projects to the specific company's mission and tech stack.

---

# RESUME TAILORING RULES

The agent MUST:

* Preserve factual integrity (education, degrees, dates, company names).
* Preserve actual projects and verifiable metrics.
* Align technical nomenclature with the JD (e.g., if JD specifies "RESTful Microservices" and candidate has "Express APIs", highlight microservices architecture).
* Reorder relevant skills to match JD keyword hierarchy.
* Improve impact wording truthfully (Action verbs: *Architected, Engineered, Implemented, Optimized, Deployed*).

The agent MUST NOT:

* Invent experience or tenure.
* Invent fake metrics or fabricated percentages.
* Add programming languages or libraries the candidate has never used.
* Claim certifications not officially verified.

---

# COVER LETTER

Generate:

```text
[Header: Candidate Info | Target Company | Date]

1. Targeted Hook: Specific role name, company name, and candidate's core engineering focus.
2. Value Proposition: Direct connection between candidate's top project/GitHub repo and the company's tech stack.
3. Problem Solving Proof: Quantitative accomplishment from internships, open-source, or LeetCode problem solving.
4. Cultural & Engineering Alignment: Why the candidate is eager to grow within their specific engineering team.
5. Call to Action: Professional closing and request for technical discussion.
```

Cover letters must be generated strictly from truthful candidate profile data.

---

# APPLICATION AGENT (THE INNOVATIVE CORE)

File:

```text
server/agents/application_agent.py
```

The Application Agent is the innovative automation engine of CareerPilot AI, combining robotic process automation (RPA) with responsible AI design.

## Technical Architecture & Portal Support

The agent utilizes **Playwright** (with Python async bindings, fallback support for Selenium) to interact with job portals:

* **Primary Regional & Global Targets**:
  * **Naukri.com**: Login session preservation, navigating to Quick Apply / Apply on Company Site.
  * **LinkedIn Jobs**: Handling multi-step "Easy Apply" dialogs (Contact Info → Resume Upload → Screening Questions).
  * **Direct ATS Portals**: Greenhouse.io, Lever.co, Workday, SmartRecruiters.

## Staged Browser Automation Workflow

```text
User selects shortlisted job
         ↓
Tailoring Agent generates tuned Resume PDF + Cover Letter
         ↓
User clicks "Stage Application"
         ↓
Playwright launches browser context (Headed or Staged session)
         ↓
Navigates to job application portal / URL
         ↓
Heuristic DOM Field Mapping:
  - First Name, Last Name, Email, Phone
  - LinkedIn, GitHub, Portfolio URLs
  - Uploads Tailored Resume PDF
  - Pastes Tailored Cover Letter
  - Auto-fills known candidate answers (Notice period: Immediate, Experience: 0-1 yr)
         ↓
SYSTEM INTENTIONALLY HALTS (Hard Stop)
         ↓
┌────────────────────────────────────────────────────────┐
│             MANDATORY HUMAN REVIEW GATE               │
│                                                        │
│  "Application staged on Naukri/LinkedIn.               │
│   Please review all pre-filled answers and click       │
│   'Submit' in the browser window to confirm."          │
└────────────────────────────────────────────────────────┘
         ↓
Candidate manually verifies, solves any CAPTCHA, and submits
         ↓
Application Agent records timestamp, portal, and status as USER_SUBMITTED
```

## Why Staging (Stopping at Review) is a Core Architectural Decision, Not a Limitation:

1. **LinkedIn Section 8.2 & Naukri Anti-Bot Terms**: Automated headless submission bots blatantly violate platform ToS. Portals aggressively detect and ban candidate accounts that submit without human interaction. By keeping the final submit human-triggered, CareerPilot keeps the candidate 100% compliant and unbanned.
2. **Responsible AI Design**: Legal screening questions (e.g. work authorization, disability, criminal disclosures, compensation) carry legal consequences and must never be auto-signed by an autonomous agent.
3. **Overcoming Cloudflare & CAPTCHA**: Portals present CAPTCHAs to prevent spam. CareerPilot's interactive staging allows the candidate to complete human verification natively in the browser session.

---

# HUMAN REVIEW CHECKPOINT

The UI presents an interactive verification card:

```text
===========================================================
               APPLICATION READY FOR REVIEW
===========================================================
Target Company: Acme Software
Role:           Associate Backend Engineer (SDE-1)
Portal:         LinkedIn Easy Apply / Naukri

PREPARED ASSETS:
 [✓] Tailored Resume:    resume_acme_backend.pdf (Attached)
 [✓] Cover Letter:       Personalized to Acme engineering
 [✓] Staged Fields:      Contact, GitHub, Notice Period, Skills

STAGING STATUS:
 Browser session paused on final application confirmation screen.

REMINDER:
 In compliance with platform Terms of Service and Responsible AI
 principles, CareerPilot NEVER automatically clicks "Submit".

 [Open / Focus Staging Browser]     [Mark as Submitted]     [Cancel]
===========================================================
```

---

# AUTOMATION STATES

Applications can have:

```text
DISCOVERED
SHORTLISTED
PREPARING
READY_FOR_REVIEW
USER_SUBMITTED
INTERVIEW
OFFER
REJECTED
WITHDRAWN
```

---

# APPLICATION AUTOMATION SAFETY

The automation must stop when encountering:

```text
CAPTCHA
Two-factor authentication
Unexpected login
Blocked automation
Unsupported form
Required manual verification
```

Display:

```text
Manual action required.
CareerPilot cannot safely continue this step.
```

Never attempt to bypass the restriction.

---

# APPLICATION AGENT LOG

Store:

```json
{
  "jobId": "",
  "startedAt": null,
  "completedAt": null,
  "fieldsPrepared": [],
  "fieldsSkipped": [],
  "status": "READY_FOR_REVIEW"
}
```

Never store passwords or authentication cookies in the database.

---

# INTERVIEW PREP AGENT

File:

```text
server/agents/interview_agent.py
```

## Responsibilities

Generate interview preparation from:

```text
Job Description
Candidate Resume
Matched Skills
Missing Skills
Projects
Company/role information where available
```

---

# INTERVIEW QUESTION CATEGORIES

Generate:

### Technical

```text
Java
Python
SQL
DSA
React
Backend
Database
APIs
```

based on the actual JD.

### Project Questions

Questions about the candidate's projects.

Example:

```text
Explain how your CareerPilot project works.

Why did you use LangGraph?

How does your matching system work?

How did you handle human approval?
```

### Behavioral

```text
Tell me about yourself.
Why this role?
Why should we hire you?
Tell me about a difficult problem you solved.
```

---

# MOCK INTERVIEW

User can start:

```text
Start Mock Interview
```

The system presents one question at a time.

Flow:

```text
Question
   ↓
User Answer
   ↓
AI Evaluation
   ↓
Feedback
   ↓
Next Question
```

---

# INTERVIEW FEEDBACK

Evaluate:

```text
Technical correctness
Relevance
Clarity
Structure
Confidence
Missing points
Suggested improvement
```

Example:

```json
{
  "score": 7,
  "strengths": [
    "Correct explanation",
    "Good example"
  ],
  "improvements": [
    "Explain time complexity",
    "Mention edge cases"
  ]
}
```

---

# AGENT ORCHESTRATION

Use LangGraph to coordinate agents.

Graph:

```text
START
  ↓
Assessment Agent
  ↓
Job Discovery
  ↓
Matching
  ↓
Gap & Learning
  ↓
User Shortlist
  ↓
Tailoring
  ↓
Human Review
  ↓
Application Agent
  ↓
Interview Prep
  ↓
Feedback
  ↓
END
```

Not every agent must execute automatically.

The graph must respond to real user actions.

For example:

```text
Assessment
    ↓
Discovery
    ↓
Matching
    ↓
User selects job
    ↓
Tailoring
```

The Tailoring Agent should not generate versions for every job automatically.

---

# LANGGRAPH STATE

Create a shared state similar to:

```python
{
    "user_id": "",
    "profile": {},
    "jobs": [],
    "selected_job": {},
    "assessment": {},
    "skill_gaps": [],
    "learning_resources": [],
    "tailored_resume": "",
    "cover_letter": "",
    "application_status": "",
    "interview_questions": [],
    "human_approval": False
}
```

Every agent should read only the state it needs and return structured updates.

---

# FRONTEND PAGES

Create:

```text
/login
/register
/
/assessment
/jobs
/jobs/:id
/learning
/applications
/applications/:id
/interview
/analytics
/profile
```

---

# DASHBOARD

Dashboard should display:

```text
Job Readiness Score
Relevant Jobs
High-Match Jobs
Top Skill Gaps
Learning Progress
Applications
Interviews
```

Example:

```text
JOB READINESS

72 / 100

↑ 8 points this month
```

---

# WORKFLOW VISUALIZATION

Display the agent pipeline visually:

```text
Assessment
   ↓
Discovery
   ↓
Matching
   ↓
Gap Analysis
   ↓
Learning
   ↓
Tailoring
   ↓
Application
   ↓
Interview
```

Each node should show:

```text
Waiting
Running
Completed
Needs Review
Blocked
```

The graph must represent actual pipeline state.

---

# PROFILE PAGE

Show:

```text
Name
Resume
Target Roles
Location
GitHub
LeetCode
Skills
Projects
Education
```

Buttons:

```text
Upload Resume
Refresh GitHub
Refresh LeetCode
Update Preferences
```

Uploading a new resume must trigger reassessment.

---

# ASSESSMENT PAGE

Display:

```text
Overall Readiness
Skill Breakdown
Strengths
Weaknesses
GitHub Evidence
LeetCode Evidence
Target Role Compatibility
```

Example:

```text
Java       ████████░░ 80%
Python     ███████░░░ 70%
SQL        ████████░░ 80%
React      █████░░░░░ 50%
Docker     ██░░░░░░░░ 20%
```

---

# JOB EXPLORER

Features:

```text
Search
Role filter
Location filter
Remote filter
Match score filter
Source filter
```

Each job card shows:

```text
Company
Role
Location
Match Score
Matched Skills
Missing Skills
Apply URL
```

Example:

```text
Backend Developer Intern

Skill Match: 82%

✓ Java
✓ SQL
✓ Git

Missing:
• Spring Boot
• Docker

[View Job]
```

---

# JOB DETAILS

Show:

```text
Job Description
Match Score
Matched Skills
Missing Skills
Why this job matches
Skill gaps
Learning resources
Tailored resume
Cover letter
Application status
Interview preparation
```

Actions:

```text
Tailor Resume
Generate Cover Letter
Prepare Application
Start Interview Prep
```

---

# LEARNING PAGE

Display:

```text
Priority Skill Gaps
Job Frequency
Learning Resources
Progress
Mini Projects
```

Example:

```text
1. Spring Boot
HIGH PRIORITY

Appears in 73% of your relevant backend jobs.

Recommended:
• Official Spring documentation
• NPTEL resource
• Practical YouTube tutorial

Mini Project:
Build a Spring Boot REST API.
```

---

# APPLICATIONS PAGE

Use a Kanban board:

```text
SHORTLISTED
PREPARING
READY FOR REVIEW
SUBMITTED
INTERVIEW
OFFER
REJECTED
```

Cards show:

```text
Company
Role
Match score
Application status
Next action
```

---

# REVIEW PAGE

Before application staging/submission:

```text
Resume
Cover Letter
Application Answers
Personal Information
Job Details
```

User must explicitly approve the preparation.

The system must clearly state:

```text
CareerPilot does not automatically submit applications.
```

---

# INTERVIEW PAGE

Display:

```text
Select Job
↓
Interview Type
↓
Technical / Behavioral / Mixed
↓
Start Mock Interview
```

During the interview:

```text
Question 1

[User answer]

[Submit Answer]
```

Then:

```text
Score
Feedback
Better Answer
Next Question
```

---

# ANALYTICS PAGE

Display:

```text
Jobs analyzed
Jobs shortlisted
Applications prepared
Applications submitted
Interviews
Offers
Average match score
Top missing skills
Learning progress
```

---

# DATABASE MODELS

## User

```text
_id
name
email
passwordHash
createdAt
updatedAt
```

---

## Profile

```text
_id
userId
resumeText
skills[]
projects[]
experience[]
education[]
certifications[]
targetRoles[]
location
workMode
githubUsername
leetcodeUsername
skillVector
readinessScore
createdAt
updatedAt
```

---

## Job

```text
_id
title
company
description
location
source
applyUrl
requiredSkills[]
preferredSkills[]
experienceLevel
postedDate
embedding[]
createdAt
```

---

## JobMatch

```text
_id
userId
jobId
score
matchedSkills[]
missingSkills[]
reason
createdAt
```

---

## SkillGap

```text
_id
userId
skill
priority
jobFrequency
jobPercentage
reason
suggestedAction
miniProject
createdAt
```

---

## LearningResource

```text
_id
skill
title
url
provider
resourceType
description
estimatedTime
```

---

## ResumeVersion

```text
_id
userId
jobId
content
changeSummary[]
approved
createdAt
```

---

## CoverLetter

```text
_id
userId
jobId
content
approved
createdAt
```

---

## Application

```text
_id
userId
jobId
status
resumeVersionId
coverLetterId
preparedFields[]
skippedFields[]
humanApproved
submittedAt
nextActionDate
notes
createdAt
updatedAt
```

---

## InterviewSession

```text
_id
userId
jobId
questions[]
answers[]
feedback[]
overallScore
createdAt
```

---

# API ENDPOINTS

## Authentication

```text
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me
```

---

## Profile

```text
GET   /api/profile
PATCH /api/profile
POST  /api/profile/resume
POST  /api/profile/github/sync
POST  /api/profile/leetcode/sync
```

---

## Assessment

```text
POST /api/assessment/run
GET  /api/assessment
```

---

## Jobs

```text
GET  /api/jobs
GET  /api/jobs/:id
POST /api/jobs/sync
POST /api/jobs/:id/match
```

---

## Skill Gaps

```text
GET /api/skill-gaps
POST /api/skill-gaps/generate
```

---

## Learning

```text
GET /api/learning/resources
POST /api/learning/resources/recommend
PATCH /api/learning/:id/progress
```

---

## Resume Tailoring

```text
POST /api/materials/resume/generate
GET  /api/materials/resume
GET  /api/materials/resume/:id
```

---

## Cover Letter

```text
POST /api/materials/cover-letter/generate
GET  /api/materials/cover-letter/:id
```

---

## Applications

```text
GET   /api/applications
POST  /api/applications
GET   /api/applications/:id
PATCH /api/applications/:id
DELETE /api/applications/:id
```

---

## Application Preparation

```text
POST /api/applications/:id/prepare
POST /api/applications/:id/approve
POST /api/applications/:id/cancel
```

The `/approve` endpoint represents approval to proceed with the staging process.

It must NOT perform final submission.

---

## Interview

```text
POST /api/interview/start
POST /api/interview/:id/answer
GET  /api/interview/:id
POST /api/interview/:id/finish
```

---

## Analytics

```text
GET /api/analytics
```

---

# AGENT DIRECTORY

```text
server/
└── agents/
    ├── assessment_agent.py
    ├── discovery_agent.py
    ├── matching_agent.py
    ├── gap_learning_agent.py
    ├── tailoring_agent.py
    ├── application_agent.py
    ├── interview_agent.py
    └── feedback_agent.py
```

---

# SERVICE DIRECTORY

```text
server/
└── services/
    ├── ai_service.py
    ├── embedding_service.py
    ├── github_service.py
    ├── leetcode_service.py
    ├── job_service.py
    ├── matching_service.py
    ├── learning_service.py
    ├── resume_service.py
    ├── application_service.py
    └── interview_service.py
```

---

# API DIRECTORY

```text
server/
└── routes/
    ├── auth.py
    ├── profile.py
    ├── assessment.py
    ├── jobs.py
    ├── skill_gaps.py
    ├── learning.py
    ├── materials.py
    ├── applications.py
    ├── interview.py
    └── analytics.py
```

---

# FRONTEND STRUCTURE

```text
client/
└── src/
    ├── api/
    ├── components/
    ├── pages/
    ├── store/
    ├── hooks/
    ├── utils/
    ├── router.jsx
    ├── App.jsx
    └── main.jsx
```

Components should include:

```text
AppShell
WorkflowGraph
AgentNode
MetricCard
SkillBar
JobCard
MatchScore
SkillGapCard
LearningResourceCard
ResumePreview
CoverLetterPreview
ApplicationCard
ReviewCheckpoint
InterviewQuestion
InterviewFeedback
LoadingState
ErrorBanner
```

---

# AUTHENTICATION

Use JWT.

Protected endpoints require:

```text
Authorization: Bearer <token>
```

Password storage must use secure hashing.

Users must only be able to access their own:

```text
Profile
Assessment
Matches
Resume versions
Applications
Interview sessions
Analytics
```

---

# ERROR HANDLING

API errors should return:

```json
{
  "message": "Human-readable error"
}
```

Frontend must display appropriate:

```text
Loading
Success
Error
Empty
Retry
```

states.

---

# AI FAILURE HANDLING

If Gemini/Groq is unavailable:

```text
Do not crash the application.
```

The system should:

1. Retry where appropriate.
2. Fall back to deterministic processing.
3. Preserve previously generated results.
4. Display a clear status.

Example:

```text
AI service unavailable.

CareerPilot used rule-based matching for this analysis.
```

---

# JOB SOURCE FAILURE

If a job source fails:

```text
Do not break the application.
```

Other available sources should continue working.

If no live source is available:

```text
Allow the user to import a job description manually.
```

---

# MANUAL JOB IMPORT

User can paste:

```text
Job Title
Company
Job Description
Application URL
```

CareerPilot then runs:

```text
Matching
Gap Analysis
Tailoring
Interview Preparation
```

This ensures the core product remains useful even when external job APIs are unavailable.

---

# SECURITY

The application must:

* Hash passwords.
* Use JWT authentication.
* Keep API keys in environment variables.
* Never log secrets.
* Validate uploaded files.
* Limit request sizes.
* Validate URLs.
* Validate external API responses.
* Enforce user ownership.
* Never store portal passwords.
* Never expose authentication cookies.
* Never bypass CAPTCHA.
* Never bypass security controls.
* Never automatically submit applications.

---

# HUMAN-IN-THE-LOOP (HITL) DESIGN: THE ETHICAL & LEGAL CORNERSTONE

This is a core architectural pillar and a primary differentiator in academic evaluations and technical viva defense.

The system explicitly decouples AI generation and staging from external execution:

```text
┌─────────────────────────────────────────────────────────────┐
│                       AI SUB-SYSTEM                         │
│                                                             │
│   AI Assessment  ──>  AI Matching  ──>  AI Tailoring       │
│                                              │              │
│                                              ▼              │
│                                     AI Browser Staging      │
│                                     (DOM field pre-fill)    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
               ┌──────────────────────────────┐
               │    MANDATORY APPROVAL GATE   │
               │   (LangGraph State Checkpoint│
               │    / interrupt_before)       │
               └───────────────┬──────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      HUMAN OPERATOR                         │
│                                                             │
│   Inspects Pre-filled Data  ──>  Verifies Resume & Letter   │
│                                              │              │
│                                              ▼              │
│                                   Solves CAPTCHA / 2FA      │
│                                              │              │
│                                              ▼              │
│                                   Clicks "SUBMIT APPLICATION"│
│                                   (External Real-world Action)│
└─────────────────────────────────────────────────────────────┘
```

## Why Fully Autonomous Bots are an Anti-Pattern:

### 1. The Terms of Service (ToS) & Legal Reality
* **LinkedIn User Agreement (Section 8.2)**: Expressly prohibits any software, bot, scraper, or browser automation extension that engages in automated profile interaction or submission. Accounts detected using autonomous "Easy Apply" scripts face immediate shadowbanning or permanent profile termination.
* **Naukri.com Terms of Use**: Strictly disallows automated crawling, bot applying, or API spoofing. Automated applying triggers Cloudflare rate-limiting and device fingerprint bans.
* **Applicant Tracking Systems (ATS)**: Enterprise platforms (Greenhouse, Lever, Workday) actively implement bot-detection heuristics (e.g., submission velocity, mouse telemetry, hidden honeypot fields). Headless bots lead to the candidate's email and phone number being blacklisted across recruiter databases.

### 2. "Responsible AI Agent Design" as an Academic Strength
In a capstone project presentation or research defense (Viva Voce), examiners frequently challenge students who claim to have built "fully autonomous job apply bots":
* *Examiner*: "How do you handle CAPTCHA? How do you prevent spamming companies? Doesn't this violate portal ToS?"
* *The Defensible Answer*: **CareerPilot is engineered around Responsible AI Agent Design.** We automate the cognitively intensive and time-consuming tasks (skill gap analysis, semantic matching, STAR bullet refinement, DOM locator mapping, form pre-filling), while intentionally enforcing an immutable Human-in-the-Loop checkpoint before any real-world binding action occurs.

### 3. Verification of Critical Legal Disclosures
Job applications include binding legal disclosures that an AI cannot ethically sign on a candidate's behalf:
* Citizenship, visa sponsorship requirements, and work eligibility.
* Non-compete covenants and conflict-of-interest agreements.
* Equal Opportunity disclosures (veteran status, disability, race).
* Salary expectations and background verification consent.

The HITL design guarantees that the candidate retains complete ownership, agency, and accountability over their professional career.

---

# NOTIFICATION SYSTEM

Generate notifications for:

```text
New high-match job
Important skill gap
Learning milestone
Application ready for review
Interview preparation available
Application status update
Upcoming follow-up
```

Example:

```text
High Match Found

Backend Developer Intern at XYZ has an 87% match score.
```

---

# READINESS SCORE

Calculate an overall readiness score based on:

```text
Skill coverage
Project evidence
Target-role compatibility
DSA/problem-solving evidence
Job-market alignment
Learning progress
```

The score should be explainable.

Never show only:

```text
Readiness = 82
```

Instead show:

```text
Readiness: 82/100

Strong:
✓ Java
✓ SQL
✓ Git

Needs improvement:
• Spring Boot
• Docker

Based on 46 relevant job postings.
```

---

# JOB RECOMMENDATION EXPLANATION

Every recommendation must answer:

```text
Why was this job recommended?
```

Example:

```text
87% Match

You match 7/8 required skills.
Your Java and SQL project experience strongly
matches the role.

Missing:
Spring Boot
```

---

# RESUME VERSIONING

Each tailored resume must be stored separately.

Example:

```text
Original Resume
     ↓
Backend Developer — Resume
     ↓
AI Engineer — Resume
     ↓
Frontend Developer — Resume
```

The original resume must never be overwritten.

---

# PROJECT PHASES

## PHASE 1 — FOUNDATION

Implement:

* React frontend
* FastAPI backend
* MongoDB
* Authentication
* User profile
* Resume upload
* Basic dashboard

Acceptance:

```text
User can register.
User can login.
User can upload resume.
Profile is stored.
```

---

## PHASE 2 — ASSESSMENT

Implement:

* Resume parsing
* Skill extraction
* GitHub integration
* LeetCode integration
* Skill vector
* Readiness score

Acceptance:

```text
Resume + public profiles
        ↓
Assessment
        ↓
Structured skill profile
```

---

## PHASE 3 — JOB INTELLIGENCE

Implement:

* Job ingestion
* Job normalization
* Skill extraction
* Embeddings
* Semantic matching
* Match scoring
* Match explanation

Acceptance:

```text
Candidate → relevant jobs ranked by fit
```

---

## PHASE 4 — GAP & LEARNING

Implement:

* Job-frequency skill analysis
* Skill gap ranking
* Free resource recommendations
* Learning plans
* Mini projects
* Progress tracking

Acceptance:

```text
Real job market
      ↓
Skill frequency
      ↓
Personalized learning plan
```

---

## PHASE 5 — APPLICATION COPILOT

Implement:

* Resume tailoring
* Cover letter generation
* Resume versioning
* Application tracker
* Playwright staging
* Human review checkpoint

Acceptance:

```text
Job
 ↓
Tailored application
 ↓
Human Review
 ↓
Application staging
```

Final submission must remain manual.

---

## PHASE 6 — INTERVIEW PREPARATION

Implement:

* JD-specific questions
* Resume-specific questions
* Technical questions
* Behavioral questions
* Mock interview
* AI feedback
* Interview scoring

Acceptance:

```text
Job → Interview Preparation
```

---

## PHASE 7 — ANALYTICS & FEEDBACK

Implement:

* Application metrics
* Interview rate
* Offer rate
* Skill gap trends
* Learning progress
* Match effectiveness
* Recommendations

Acceptance:

```text
Application history
       ↓
Feedback Agent
       ↓
Career recommendations
```

---

## PHASE 8 — TESTING & DEPLOYMENT

Verify:

* Authentication
* Resume parsing
* Profile extraction
* GitHub integration
* LeetCode integration
* Job discovery
* Matching
* Skill gaps
* Learning resources
* Resume tailoring
* Cover letters
* Application staging
* Human approval
* Interview preparation
* Analytics
* Error handling
* AI failure handling

---

# WORKFLOW STATE

The frontend Workflow Graph must display actual agent state.

Possible states:

```text
WAITING
RUNNING
COMPLETED
NEEDS_REVIEW
BLOCKED
FAILED
```

Example:

```text
Assessment       ✓ Completed
Discovery        ✓ Completed
Matching         ✓ Completed
Gap Analysis     ✓ Completed
Learning         ● Running
Tailoring        ○ Waiting
Application      ○ Waiting
Interview Prep   ○ Waiting
```

---

# ACCEPTANCE CRITERIA

The application is considered complete when all of the following work.

### A. Authentication

User can register/login and protected APIs reject unauthenticated requests.

### B. Resume

PDF resume is uploaded and parsed into structured profile information.

### C. Assessment

Resume + public profile information produce a structured skill assessment.

### D. GitHub

Public GitHub information can contribute evidence to the assessment.

### E. LeetCode

Available public problem-solving information can contribute to the assessment.

### F. Job Discovery

Relevant jobs can be discovered/imported and normalized.

### G. Matching

Each job receives an explainable 0–100 match score.

### H. Skill Gap

Missing skills are ranked using their frequency across relevant jobs.

### I. Learning

Specific free resources and practical actions are recommended.

### J. Tailoring

A job-specific resume and cover letter can be generated without fabricating candidate information.

### K. Versioning

Different job-specific resume versions can be stored without overwriting the original resume.

### L. Application Preparation

Playwright can assist with permitted application preparation.

### M. Human Review

The application workflow always stops before final submission.

### N. Safety

CAPTCHA, authentication challenges, blocked automation, or unsupported forms cause the system to pause rather than bypass restrictions.

### O. Interview

JD-specific interview questions and mock interview feedback work.

### P. Analytics

Application and interview outcomes are summarized.

### Q. Agent Orchestration

Agents operate as independent modules coordinated by LangGraph.

### R. Explainability

The system explains:

```text
Why this job?
Why this skill gap?
Why this recommendation?
Why this readiness score?
```

### S. Failure Recovery

Failure of an AI provider or external data source must not crash the application.

### T. Human Control

No external application is ever finally submitted without explicit user action.

---

# FINAL PRODUCT FLOW

The completed CareerPilot AI should demonstrate this complete journey:

```text
                    CAREERPILOT AI
                         │
                         ▼
                  Upload Resume
                         │
                         ▼
               ┌─────────────────┐
               │ Assessment Agent │
               └────────┬────────┘
                        │
             Resume + GitHub + LeetCode
                        │
                        ▼
                Skill Vector/Profile
                        │
                        ▼
                Job Discovery Agent
                        │
                        ▼
                 Real Job Postings
                        │
                        ▼
                 Matching Engine
                        │
                        ▼
                 Ranked Job List
                        │
                        ▼
              Gap & Learning Agent
                        │
                        ▼
              Personalized Learning
                        │
                        ▼
                User Shortlists Job
                        │
                        ▼
                 Tailoring Agent
                  /             \
                 ▼               ▼
          Tailored Resume    Cover Letter
                  \             /
                   ▼           ▼
                 Application Agent
                        │
                        ▼
                 Browser Staging
                        │
                        ▼
              ┌────────────────────┐
              │  HUMAN REVIEW      │
              │  REQUIRED          │
              └─────────┬──────────┘
                        │
                        ▼
              User manually submits
                        │
                        ▼
                Interview Prep Agent
                        │
                        ▼
                 Mock Interview
                        │
                        ▼
                 Feedback Agent
                        │
                        ▼
               Career Improvement
```

---

# FINAL ENGINEERING PRINCIPLES

The coding agent must follow these principles throughout development:

1. **Agent responsibilities must remain separate.**
2. **LangGraph controls orchestration; agents perform specialized work.**
3. **Business logic belongs in services/agents, not route handlers.**
4. **All AI outputs must be validated before persistence.**
5. **Candidate facts must never be fabricated.**
6. **Human approval is mandatory before external application submission.**
7. **Browser automation must never bypass CAPTCHA or security mechanisms.**
8. **External integrations must fail gracefully.**
9. **AI providers must be replaceable through a service abstraction.**
10. **Every important AI recommendation should be explainable.**
11. **The original resume must remain preserved.**
12. **Each tailored application must be traceable to a specific job.**
13. **The system should work even when some external services are unavailable.**
14. **The UI must clearly show what the AI did and what the human must decide.**
15. **Build phase-by-phase and verify every phase before moving to the next.**

---

# DEFINITION OF DONE

CareerPilot AI is complete when a graduating engineer can:

```text
Create account
      ↓
Upload resume
      ↓
Connect GitHub / LeetCode
      ↓
Receive skill assessment
      ↓
See real relevant jobs
      ↓
Understand match scores
      ↓
See market-based skill gaps
      ↓
Receive free learning resources
      ↓
Shortlist a job
      ↓
Generate tailored resume
      ↓
Generate cover letter
      ↓
Prepare application
      ↓
Review everything
      ↓
Manually submit
      ↓
Generate JD-specific interview preparation
      ↓
Practice mock interview
      ↓
Receive feedback
      ↓
Track career progress
```

**CareerPilot AI is an agentic career copilot, not an autonomous job-submission bot.**

The defining product principle is:

> **AI handles the analysis, preparation, and repetitive work. The candidate remains in control of the final decision.**

---

# ACADEMIC JUSTIFICATION & VIVA VOCE DEFENSE GUIDE

This section provides the theoretical foundation and evaluation defenses for academic reviewers, project guides, and external examiners (Viva Voce).

## 1. The 5 Core Computer Science Pillars

| CS / AI Pillar | Practical Implementation in CareerPilot AI | Academic Evaluation Criteria |
| :--- | :--- | :--- |
| **1. Natural Language Processing (NLP)** | PDF/DOCX resume text extraction, section identification, Named Entity Recognition (NER) for technical competencies, education, and tenure. | Information Extraction, regex normalization, structural document parsing. |
| **2. Semantic Search & Vector Embeddings** | Generating skill and JD vector embeddings using `all-MiniLM-L6-v2` / Gemini Embeddings; similarity scoring via local FAISS index. | Vector space modeling, cosine distance calculation, semantic thresholding. |
| **3. Multi-Agent Systems & State Graphs** | Orchestrating 5 specialized agents via LangGraph state graphs with typed state (`AgentState`), conditional branching, and checkpointing. | Distributed problem solving, state transition graphs, bounded agent autonomy. |
| **4. Browser Automation & RPA** | Playwright Chromium automation for DOM element discovery, selector healing, form field hydration, and session preservation on Naukri & LinkedIn. | Robotic process automation, asynchronous event handling, DOM tree traversal. |
| **5. LLM Prompting & Evaluative Feedback** | Prompt engineering for CAR/STAR bullet enhancement, zero-hallucination verification diffing, and dynamic mock interview question generation. | Few-shot prompting, structured JSON schema enforcement, LLM-as-a-judge evaluation. |

---

## 2. Viva Voce: Examiner Q&A Defense Strategy

### Question 1: "Why use a multi-agent framework (LangGraph) instead of a single prompt or simple LangChain sequential chain?"
> **Defense**:
> "A single prompt or linear chain suffers from context pollution, compounding hallucinations, and monolithic failure modes. If a single prompt tries to parse a resume, find jobs, tailor bullets, and prep interview questions, token limits are exceeded and reasoning degrades.
> 
> CareerPilot uses a **Stateful Multi-Agent Architecture (LangGraph)** where:
> 1. **Separation of Concerns**: The Assessment Agent only evaluates; the Tailoring Agent only rewrites; the Application Agent only automates DOM interactions.
> 2. **State Persistence & Checkpoints**: If browser staging fails due to a network glitch, the system recovers from the `tailored_assets` checkpoint without re-running costly LLM calls.
> 3. **Non-Linear Cycles**: If candidate feedback rejects a tailored resume, the graph routes backward specifically to the Tailoring Agent without restarting the entire workflow."

---

### Question 2: "Why didn't you automate the final submission button? Isn't an agent supposed to be fully autonomous?"
> **Defense**:
> "In software engineering and AI ethics, this is the vital distinction between **blind script execution** and **Responsible AI Agent Design**:
> 1. **Terms of Service (ToS) & Anti-Bot Defense**: LinkedIn Section 8.2 and Naukri strictly prohibit autonomous submission bots. Fully autonomous applying scripts trigger Cloudflare/Datadome bot tripwires and permanently blacklist the student's profile.
> 2. **Legal & Compliance Accountability**: Job applications contain legally binding representations regarding work authorization, visa sponsorships, and background disclosures. An AI agent cannot legally sign contracts or disclosures on behalf of a human.
> 3. **The 95/5 Principle**: CareerPilot automates 95% of the cognitive overhead (gap discovery, semantic matching, STAR bullet refinement, DOM locator pre-filling), but leaves the final 5%—the critical approval click—to the human operator."

---

### Question 3: "How do you prevent the Tailoring Agent from hallucinating false experience or fake skills?"
> **Defense**:
> "CareerPilot implements a **Strict Grounded Verification Diff**:
> * The candidate's original resume and verified GitHub/LeetCode data form an immutable *Ground Truth Skill Set* ($S_{\text{ground}}$).
> * The Tailoring Agent is constrained by strict system prompts to only reorder, rephrase, and emphasize existing facts using the CAR/STAR format.
> * Before any tailored output is saved, a deterministic verification function scans the generated bullet points for new technical keywords ($S_{\text{tailored}}$). If $S_{\text{tailored}} \setminus S_{\text{ground}} \neq \emptyset$, the output is rejected and regenerated. The AI is structurally forbidden from inventing experience."

---

### Question 4: "How does the Gap & Learning Agent differ from existing online skill lists?"
> **Defense**:
> "Existing tools provide static, generic checklists (e.g., 'every software engineer should know Kubernetes, C++, and System Design').
> 
> CareerPilot computes an **Empirical Market Frequency Score** based on real-time aggregated postings for the student's specific target role and geography:
> $$\text{Demand Frequency}(s) = \frac{\sum \text{Postings containing } s}{N_{\text{total target postings}}} \times 100\%$$
> Missing skills are ranked strictly by this frequency. Furthermore, each gap is mapped directly to free, accredited resources (NPTEL university courses, developer-vetted YouTube curricula, and authoritative documentation) with realistic completion timeframes."

---

### Question 5: "What is the operational cost of running this system?"
> **Defense**:
> "The entire system is intentionally engineered for **$0.00 operational cost**:
> * **LLM Inference**: Powered by Google Gemini 1.5 Flash and Groq (Llama 3.3 70B) developer free tiers.
> * **Embeddings & Vector Search**: Local `sentence-transformers` and local FAISS index (zero cloud vector DB hosting fees).
> * **Database**: MongoDB Community Edition (local) or MongoDB Atlas M0 free tier.
> * **Browser Automation**: Local headless Playwright instance.
> 
> This ensures that any engineering student or institution can deploy and run CareerPilot without incurring ongoing cloud expenses."

---

## 3. Project Presentation Narrative & Impact

```text
       BEFORE CAREERPILOT                                   WITH CAREERPILOT
┌────────────────────────────────┐                 ┌────────────────────────────────┐
│   "AI is taking my job."       │                 │   "AI is fighting for my job." │
│                                │                 │                                │
│ • Mass-applying generic resumes│                 │ • Targeted skill benchmarking  │
│ • Instant automated ATS reject │  ─────────────> │ • Real-market gap upskilling   │
│ • Paralysis by analysis        │                 │ • Tailored CAR/STAR resumes    │
│ • Risk of bot bans/blacklisting│                 │ • Compliant staged applications│
│ • Anxiety & uncertainty        │                 │ • JD-specific mock interviews  │
└────────────────────────────────┘                 └────────────────────────────────┘
```

By unifying modern NLP, vector retrieval, responsible multi-agent orchestration, and browser automation, CareerPilot transforms AI from an existential career threat into the graduating engineer's greatest professional asset.

