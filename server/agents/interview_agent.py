import json
import httpx
from typing import Dict, Any, List
from server.config import settings
from server.database import db

class InterviewPrepAgent:
    """
    Agent 5: High-impact Interview Preparation Agent.
    Generates realistic, domain-grounded technical & behavioral questions tailored to the exact role,
    evaluates responses with strict scoring, and provides actionable critique + senior engineer model answers.
    """

    def __init__(self):
        self.name = "Interview Prep Agent"

    async def _call_llm(self, prompt: str, system_prompt: str) -> str:
        if settings.GEMINI_API_KEY:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
                payload = {
                    "contents": [{"parts": [{"text": f"{system_prompt}\n\nTask:\n{prompt}"}]}],
                    "generationConfig": {"temperature": 0.4, "maxOutputTokens": 1200}
                }
                async with httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        candidates = resp.json().get("candidates", [])
                        if candidates:
                            return candidates[0]["content"]["parts"][0]["text"]
            except Exception as e:
                print(f"[{self.name}] Gemini call failed: {e}")

        if settings.GROQ_API_KEY:
            try:
                headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}", "Content-Type": "application/json"}
                payload = {
                    "model": "llama-3.1-70b-versatile",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.4
                }
                async with httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
                    if resp.status_code == 200:
                        return resp.json()["choices"][0]["message"]["content"]
            except Exception as e:
                print(f"[{self.name}] Groq call failed: {e}")

        return ""

    async def generate_questions(self, target_jd: Dict[str, Any], candidate_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        role = target_jd.get("title", "Software Engineer")
        company = target_jd.get("company", "Tech Company")
        skills = target_jd.get("required_skills", ["Python", "SQL", "Git"])
        domain = target_jd.get("domain", "Backend")

        print(f"[{self.name}] Synthesizing high-impact interview questions for {role} at {company}...")

        system_prompt = (
            "You are a Principal Software Engineering Interviewer conducting a realistic technical screening for a graduating engineer. "
            "Generate 5 substantive, authentic interview questions (3 deep technical questions grounded in the tech stack and 2 scenario/behavioral STAR questions). "
            "Never generate trivial definitions like 'What is Python?'. Ask realistic architectural, problem-solving, and trade-off questions."
        )

        prompt = (
            f"Target Position: {role} at {company}\n"
            f"Required Skills: {', '.join(skills)}\n"
            f"Engineering Domain: {domain}\n"
            f"Candidate Verified Skills: {', '.join(candidate_profile.get('skills', [])[:8])}\n\n"
            f"Return a JSON array of 5 objects with keys:\n"
            f"- 'id': integer (1 to 5)\n"
            f"- 'type': 'Technical Deep-Dive' | 'System & Data Architecture' | 'Behavioral (STAR)'\n"
            f"- 'question': string (Rigorous, realistic interview question)\n"
            f"- 'why_asked': string (What the interviewer is specifically evaluating)\n"
            f"- 'key_concepts': list of 3-4 specific concepts to mention\n"
            f"- 'hint': string (Guidance on structuring a winning answer)\n"
            f"Return ONLY valid JSON array."
        )

        llm_out = await self._call_llm(prompt, system_prompt)
        questions = []
        if llm_out:
            try:
                clean_json = llm_out.strip().replace("```json", "").replace("```", "").strip()
                questions = json.loads(clean_json)
            except Exception as e:
                print(f"[{self.name}] Failed to parse questions JSON: {e}")

        # High-signal curated questions per domain if LLM not connected
        if not questions:
            primary_skill = skills[0] if skills else "Python"
            secondary_skill = skills[1] if len(skills) > 1 else "SQL"
            domain_low = domain.lower()
            
            if "frontend" in domain_low:
                questions = [
                    {
                        "id": 1,
                        "type": "Technical Deep-Dive",
                        "question": f"In a modern web app using {primary_skill} and TypeScript, how does the Virtual DOM reconciliation algorithm work? How do you prevent unnecessary re-renders in deep component trees?",
                        "why_asked": "Evaluates understanding of UI render lifecycles, diffing algorithms, memoization (React.memo, useMemo, useCallback), and component purity.",
                        "key_concepts": ["Fiber Tree reconciliation", "Key props uniqueness", "Memoization hooks (useMemo, useCallback)", "Immutable state updates"],
                        "hint": "Explain how the diffing algorithm compares virtual trees, how stable keys avoid recreating DOM nodes, and when to memoize expensive sub-trees."
                    },
                    {
                        "id": 2,
                        "type": "System & Data Architecture",
                        "question": "How do you optimize Core Web Vitals (LCP, INP, CLS) for a high-traffic e-commerce storefront? What techniques do you use to reduce JavaScript execution time and bundle size?",
                        "why_asked": "Tests real-world web performance engineering, Lighthouse auditing, code-splitting, and layout stability.",
                        "key_concepts": ["Dynamic import() & code splitting", "Image optimization (WebP, srcset, aspect-ratio)", "Minimizing Long Tasks (INP)", "Critical CSS inlining"],
                        "hint": "Discuss lazy-loading offscreen routes, reserving layout dimensions to avoid CLS, and offloading heavy tasks so the main browser thread stays responsive."
                    },
                    {
                        "id": 3,
                        "type": "Technical Deep-Dive",
                        "question": f"When handling asynchronous network requests with {secondary_skill or 'REST APIs'}, how do you implement optimistic UI updates with automatic rollback on server error?",
                        "why_asked": "Assesses client-side state predictability, error handling UX, and network synchronization.",
                        "key_concepts": ["Optimistic mutations", "Rollback snapshot state", "Retry backoff logic", "Global toast error boundaries"],
                        "hint": "Walk through immediately updating local UI state, storing a rollback snapshot, sending the network request, and reverting to snapshot if 5xx errors occur."
                    },
                    {
                        "id": 4,
                        "type": "Behavioral (STAR)",
                        "question": "Describe a situation where a designer provided an interactive mockup that caused severe performance lag or layout breaking on mobile devices. How did you resolve the conflict?",
                        "why_asked": "Measures cross-functional communication with designers, technical compromise, and mobile-first responsiveness.",
                        "key_concepts": ["CSS Grid/Flexbox responsiveness", "Mobile constraint communication", "Pragmatic UI compromises", "Smooth 60fps animations"],
                        "hint": "Use STAR: Situation (the heavy mockup), Task (identifying mobile jank), Action (proposing CSS transforms over layout recalculations), Result (smooth 60fps on mobile)."
                    },
                    {
                        "id": 5,
                        "type": "Behavioral (STAR)",
                        "question": f"Why are you eager to join {company} as a Frontend Engineer, and how do you ensure the web experiences you build are accessible (WCAG 2.1 AA) to all users?",
                        "why_asked": "Evaluates genuine interest in the company, empathy for diverse users, and mastery of semantic HTML and ARIA standards.",
                        "key_concepts": ["Semantic HTML elements", "Keyboard navigation & focus trapping", "Color contrast ratios", "Screen reader aria-labels"],
                        "hint": "Mention a specific product feature of the company, and outline testing accessibility via keyboard-only navigation and screen readers."
                    }
                ]
            elif "data" in domain_low or "ai" in domain_low:
                questions = [
                    {
                        "id": 1,
                        "type": "Technical Deep-Dive",
                        "question": f"When training machine learning models using {primary_skill} and Scikit-Learn on highly imbalanced real-world datasets (e.g. 99% negative, 1% positive), why is Accuracy a misleading metric, and what techniques do you use to train and evaluate effectively?",
                        "why_asked": "Evaluates fundamental ML evaluation literacy, understanding of confusion matrices, and resampling strategies.",
                        "key_concepts": ["Precision, Recall, and PR-AUC", "F1-Score / Balanced Accuracy", "SMOTE / Class-weighting", "Stratified K-Fold Cross Validation"],
                        "hint": "Explain how a naive model predicting all negatives gets 99% accuracy but 0% recall, and describe setting class weights or optimizing the PR-AUC threshold."
                    },
                    {
                        "id": 2,
                        "type": "System & Data Architecture",
                        "question": f"How do you design a reliable batch and streaming ETL pipeline using {secondary_skill or 'SQL'} and Pandas that guarantees zero data leakage between training and testing sets during feature scaling?",
                        "why_asked": "Tests data pipeline integrity, feature engineering safety, and prevention of subtle test contamination in production.",
                        "key_concepts": ["Pipeline transformer isolation (fit on train only)", "Data leakage prevention", "Handling missing values & imputers", "Outlier capping vs removal"],
                        "hint": "Emphasize that scalers and imputers must only be fitted on the training split and transformed on test/validation splits to prevent future information leakage."
                    },
                    {
                        "id": 3,
                        "type": "Technical Deep-Dive",
                        "question": "Suppose your machine learning model has high training accuracy (97%) but low validation accuracy (68%). How do you systematically diagnose whether the issue is overfitting, feature noise, or data drift, and what corrective actions do you take?",
                        "why_asked": "Evaluates practical model debugging, bias-variance tradeoff, regularization, and feature selection.",
                        "key_concepts": ["Bias-Variance tradeoff", "L1/L2 Regularization (Lasso/Ridge)", "Dropout / Tree pruning", "Feature importance pruning"],
                        "hint": "Identify the high variance symptom (overfitting), and outline cross-validation, adding regularization, reducing model complexity, or collecting more data."
                    },
                    {
                        "id": 4,
                        "type": "Behavioral (STAR)",
                        "question": "Tell me about a data project where the raw dataset was messy, contained corrupted values, or had missing timestamps. How did you audit and clean it without biasing the end results?",
                        "why_asked": "Tests pragmatic data wrangling resilience, statistical sanity checking, and documentation discipline.",
                        "key_concepts": ["Exploratory Data Analysis (EDA)", "Imputation vs dropping criteria", "Domain validation checks", "Documenting data cleaning choices"],
                        "hint": "Use STAR: Situation (the raw messy data), Task (identifying anomalies), Action (auditing distributions and applying domain-informed cleaning), Result (clean model dataset)."
                    },
                    {
                        "id": 5,
                        "type": "Behavioral (STAR)",
                        "question": f"How would you explain the predictions and decision boundaries of a complex ML model to non-technical business stakeholders at {company}?",
                        "why_asked": "Evaluates model explainability, SHAP/LIME familiarity, and translating math into business impact.",
                        "key_concepts": ["Feature attribution (SHAP values)", "Translating coefficients to business metrics", "Risk and confidence bounds", "User-friendly visual reporting"],
                        "hint": "Discuss using feature importance or partial dependence plots, avoiding deep technical jargon, and tying predictions back to ROI or operational cost."
                    }
                ]
            elif "devops" in domain_low or "cloud" in domain_low:
                questions = [
                    {
                        "id": 1,
                        "type": "Technical Deep-Dive",
                        "question": f"When containerizing microservices with {primary_skill or 'Docker'}, how do multi-stage builds work, and what security practices do you follow to minimize image size and eliminate vulnerabilities?",
                        "why_asked": "Tests container optimization fundamentals, non-root user execution, and attack surface reduction.",
                        "key_concepts": ["Multi-stage Dockerfile stages", "Distroless / Alpine base images", "Running as non-root user", "Layer caching efficiency"],
                        "hint": "Explain separating the build environment (compilers/headers) from the minimal runtime image, and scanning layers for CVEs."
                    },
                    {
                        "id": 2,
                        "type": "System & Data Architecture",
                        "question": "Suppose a production microservice running in Linux containers starts reporting 502 Bad Gateway errors. Walk through your step-by-step diagnostic workflow using Linux command-line tools and container logs.",
                        "why_asked": "Evaluates live Linux troubleshooting methodology, process inspection, and network socket debugging.",
                        "key_concepts": ["systemctl / journalctl logs", "Process monitoring (top, ps aux, htop)", "Network verification (netstat, curl -v, ss)", "OOMKilled exit code 137 checks"],
                        "hint": "Start from ingress logs, check if container process exited due to Out Of Memory (OOM), test socket connectivity locally with curl, and inspect system logs."
                    },
                    {
                        "id": 3,
                        "type": "Technical Deep-Dive",
                        "question": f"How do you design a GitHub Actions or GitLab CI/CD pipeline that enforces automated unit testing, linting, security scanning, and blue-green or rolling zero-downtime deployment?",
                        "why_asked": "Assesses modern CI/CD automation principles, artifact generation, and deployment safety guards.",
                        "key_concepts": ["Parallel test matrix jobs", "Artifact passing between stages", "Automated rollbacks on healthcheck failure", "Zero-downtime rolling updates"],
                        "hint": "Describe defining fail-fast test stages, caching dependencies, publishing signed container images, and verifying health probes before routing traffic."
                    },
                    {
                        "id": 4,
                        "type": "Behavioral (STAR)",
                        "question": "Describe an incident where a deployment pipeline broke or a configuration drift caused a service interruption in a test or personal environment. How did you conduct root-cause analysis?",
                        "why_asked": "Tests blameless post-mortem culture, root-cause identification, and preventing recurrence through Infrastructure-as-Code.",
                        "key_concepts": ["Blameless root cause analysis", "Git commit history auditing", "Fixing root cause vs symptom", "Adding automated safeguards"],
                        "hint": "Use STAR: Situation (pipeline failure), Task (isolating failure), Action (inspecting recent commits and environment variable drift), Result (remediation and added test)."
                    },
                    {
                        "id": 5,
                        "type": "Behavioral (STAR)",
                        "question": f"Why do you want to pursue Cloud & Infrastructure engineering at {company}, and what is your strategy for keeping cloud resource costs lean while maintaining high availability?",
                        "why_asked": "Measures FinOps awareness, architectural efficiency, and proactive engineering responsibility.",
                        "key_concepts": ["Right-sizing compute instances", "Auto-scaling groups based on metric triggers", "Spot/Preemptible instance usage", "Lifecycle policies on storage"],
                        "hint": "Discuss auto-scaling rules based on traffic, stopping idle dev environments, and setting up automated budget billing alerts."
                    }
                ]
            elif "backend" in domain_low:
                questions = [
                    {
                        "id": 1,
                        "type": "Technical Deep-Dive",
                        "question": f"In a high-throughput backend using {primary_skill}, how does the runtime handle asynchronous I/O versus CPU-bound operations? How do you prevent blocking the main event loop or worker thread?",
                        "why_asked": "Tests core concurrency models, event loops, process vs thread pooling, and knowledge of non-blocking I/O.",
                        "key_concepts": ["Event Loop execution", "async/await vs ThreadPoolExecutor", "Database I/O non-blocking drivers", "CPU-bound offloading"],
                        "hint": "Explain how I/O bound calls yield control back to the event loop, and how you offload heavy computation (e.g. hashing, compression) to background workers."
                    },
                    {
                        "id": 2,
                        "type": "System & Data Architecture",
                        "question": f"Suppose your application queries a {secondary_skill} database table with 5 million rows, and an endpoint's latency spikes from 50ms to 2.5 seconds under load. How would you diagnose the bottleneck and fix it?",
                        "why_asked": "Evaluates practical database performance debugging, index selection, and caching trade-offs.",
                        "key_concepts": ["EXPLAIN ANALYZE & Query Execution Plans", "Composite B-Tree Indexes", "Connection Pool exhaustion", "Redis Cache-Aside pattern"],
                        "hint": "Walk through checking slow query logs, inspecting query plans for Sequential Scans, adding targeted indexes, and adding Redis caching for read-heavy hot keys."
                    },
                    {
                        "id": 3,
                        "type": "Technical Deep-Dive",
                        "question": "How do you implement API idempotency in payment and order creation endpoints to prevent duplicate charges when a client retries after a network timeout?",
                        "why_asked": "Evaluates distributed systems fundamentals, race conditions, and transactional consistency.",
                        "key_concepts": ["Idempotency Keys (UUID in headers)", "Atomic database constraints / Unique Index", "Distributed locking via Redis", "HTTP 200 vs 409 handling"],
                        "hint": "Explain client-generated Idempotency-Keys, checking Redis/DB atomically before execution, and caching previous responses to return on duplicates."
                    },
                    {
                        "id": 4,
                        "type": "Behavioral (STAR)",
                        "question": "Describe a difficult technical bug or race condition you encountered in a team or academic project close to a deadline. How did you diagnose it, prioritize fixes, and verify the resolution?",
                        "why_asked": "Tests composure under stress, structured debugging (logs over guessing), and team communication.",
                        "key_concepts": ["Structured log isolation", "Calm root-cause analysis", "Clear communication with teammates", "Regression unit tests"],
                        "hint": "Use the STAR method: Situation (the deadline), Task (what failed), Action (your diagnostic approach), Result (resolution and post-mortem prevention)."
                    },
                    {
                        "id": 5,
                        "type": "Behavioral (STAR)",
                        "question": f"Why are you interested in joining {company} specifically, and how do you approach learning and mastering an unfamiliar technology like {skills[-1] if skills else 'Docker'} within your first 30 days?",
                        "why_asked": "Checks genuine employer interest, curiosity, and rapid self-directed onboarding ability.",
                        "key_concepts": ["Company engineering culture", "Official documentation & spike projects", "Asking high-context questions", "Proactive delivery"],
                        "hint": "Mention a specific technical challenge the company tackles, and outline your 30-day strategy (reading codebase, small bug fixes, documentation)."
                    }
                ]
            else:
                # Full Stack / General Tech Questions
                questions = [
                    {
                        "id": 1,
                        "type": "Technical Deep-Dive",
                        "question": f"When building web applications with {primary_skill} and REST APIs, how do you handle state management, data caching, and race conditions when multiple async requests resolve out of order?",
                        "why_asked": "Tests front-to-back state consistency, network latency handling, and cancellation tokens.",
                        "key_concepts": ["AbortController / Request cancellation", "Optimistic UI updates", "Centralized state store", "Data normalization"],
                        "hint": "Discuss cancelling stale network requests with AbortController, and ensuring updates match the most recent timestamp."
                    },
                    {
                        "id": 2,
                        "type": "System & Data Architecture",
                        "question": "Explain the difference between authentication and authorization in web systems. How would you design a secure JWT-based auth flow that handles token expiration and revocation without overloading your database?",
                        "why_asked": "Evaluates security architecture, stateless tokens, and practical token invalidation.",
                        "key_concepts": ["Short-lived Access Token (15m)", "HttpOnly Secure Refresh Token", "Redis Token Blacklist for logout", "RBAC middleware"],
                        "hint": "Contrast 401 Unauthorized vs 403 Forbidden, and outline storing short-lived JWTs in memory with HttpOnly refresh cookies."
                    },
                    {
                        "id": 3,
                        "type": "Technical Deep-Dive",
                        "question": f"In a production system using {secondary_skill}, what are the primary trade-offs between horizontal scaling (adding nodes) versus vertical scaling (upgrading CPU/RAM), and how does statefulness affect this decision?",
                        "why_asked": "Evaluates system scalability, stateless services, and shared database bottlenecks.",
                        "key_concepts": ["Stateless web servers behind Load Balancer", "Database read-replicas & sharding", "Session storage in Redis", "Cost & resilience trade-offs"],
                        "hint": "Explain how stateless APIs scale horizontally behind Nginx/ALB easily, whereas stateful databases require replication or sharding."
                    },
                    {
                        "id": 4,
                        "type": "Behavioral (STAR)",
                        "question": "Tell me about a time you had to make a technical trade-off between writing perfect code and delivering an MVP on time. How did you decide what to sacrifice?",
                        "why_asked": "Tests pragmatic engineering judgment, prioritizing business outcomes over premature optimization.",
                        "key_concepts": ["Technical debt tracking", "Essential vs non-essential features", "Code maintainability & test coverage", "Stakeholder alignment"],
                        "hint": "Explain how you shipped a working, tested core feature first, documented the technical debt, and refactored once performance requirements were clear."
                    },
                    {
                        "id": 5,
                        "type": "Behavioral (STAR)",
                        "question": f"What is a recent technical development or open-source tool in the {domain} ecosystem that excited you, and how have you experimented with it?",
                        "why_asked": "Measures ongoing intellectual curiosity and proactive engineering mindset outside of required coursework.",
                        "key_concepts": ["Specific tool/library details", "Hands-on experimentation", "Understanding practical benefits", "Future outlook"],
                        "hint": "Pick a tool you actually tested (e.g. FastAPI, Docker, Tailwind, Vite), describe building a quick prototype, and explain what pain point it solved."
                    }
                ]

        # Save to MongoDB
        await db.update_one(
            "interviews",
            {"email": candidate_profile.get("email"), "job_id": target_jd.get("id")},
            {
                "email": candidate_profile.get("email"),
                "job_id": target_jd.get("id"),
                "company": company,
                "role": role,
                "questions": questions
            },
            upsert=True
        )

        return questions

    async def evaluate_answer(
        self,
        question: str,
        user_answer: str,
        role: str,
        target_skills: List[str]
    ) -> Dict[str, Any]:
        """
        Evaluates a candidate's answer with dual scoring (Technical Depth & STAR Communication),
        actionable feedback identifying missed key concepts, and an exemplary senior engineer model answer.
        """
        clean_ans = user_answer.strip()
        word_count = len(clean_ans.split())

        if word_count < 10:
            return {
                "technical_score": 3,
                "communication_score": 4,
                "overall_score": 3.5,
                "feedback": (
                    "Your answer is too brief to demonstrate technical competence to a hiring manager. "
                    "In real technical interviews, aim for 3-4 structured paragraphs: state the engineering trade-off directly, "
                    "provide a concrete example from your projects with tools and metrics, and explain how you verified the solution."
                ),
                "model_answer": (
                    "\"In my backend project, I handled this by implementing connection pooling with SQLAlchemy and configuring a composite B-Tree index on (user_id, created_at). "
                    "When analyzing query performance using EXPLAIN ANALYZE, this eliminated sequential scans and brought p99 query latency down from 850ms to 42ms across 10,000 requests. "
                    "For hot-key reads, I placed a Redis cache-aside layer with a 5-minute TTL, which absorbed 80% of database read traffic.\""
                )
            }

        system_prompt = (
            "You are a rigorous, highly respected Senior Engineering Interviewer evaluating a candidate's response. "
            "Score on technical_score (1-10) and communication_score (1-10). "
            "Provide honest, constructive critique identifying exactly what they missed technically, "
            "and craft an exemplary, realistic Senior Engineer Model Answer using the STAR framework."
        )

        prompt = (
            f"Interview Question: {question}\n"
            f"Target Position: {role}\n"
            f"Tech Stack: {', '.join(target_skills)}\n"
            f"Candidate Response:\n{clean_ans}\n\n"
            f"Return JSON format:\n"
            f"- 'technical_score': integer (1 to 10)\n"
            f"- 'communication_score': integer (1 to 10)\n"
            f"- 'feedback': string (2-3 sentences of direct, high-value advice on missing technical concepts and communication structure)\n"
            f"- 'model_answer': string (A complete, impressive 3-4 sentence model response demonstrating senior-level competence and STAR structure)\n"
            f"Return ONLY valid JSON."
        )

        llm_out = await self._call_llm(prompt, system_prompt)
        if llm_out:
            try:
                clean_json = llm_out.strip().replace("```json", "").replace("```", "").strip()
                eval_data = json.loads(clean_json)
                tech = max(1, min(10, int(eval_data.get("technical_score", 7))))
                comm = max(1, min(10, int(eval_data.get("communication_score", 8))))
                eval_data["overall_score"] = round((tech + comm) / 2.0, 1)
                eval_data["technical_score"] = tech
                eval_data["communication_score"] = comm
                return eval_data
            except Exception as e:
                print(f"[{self.name}] Failed to parse evaluation JSON: {e}")

        # High-precision heuristic scoring based on technical depth and structure
        has_metrics = any(char.isdigit() for char in clean_ans) or "%" in clean_ans or "ms" in clean_ans or "fps" in clean_ans or "sec" in clean_ans
        has_tech_terms = any(t in clean_ans.lower() for t in [
            "index", "async", "cache", "redis", "database", "query", "thread", "api", "latency",
            "pool", "lock", "scale", "test", "fastapi", "postgres", "react", "component", "virtual dom",
            "memo", "hook", "bundle", "lighthouse", "docker", "container", "linux", "ci/cd", "pipeline",
            "kubernetes", "pandas", "scikit", "model", "f1", "precision", "recall", "sql", "git"
        ])
        
        tech_score = 5
        if has_tech_terms: tech_score = 7
        if has_tech_terms and has_metrics: tech_score = 8
        if word_count > 50 and has_metrics and has_tech_terms: tech_score = 9

        comm_score = 6
        if word_count > 20: comm_score = 7
        if any(w in clean_ans.lower() for w in ["because", "result", "implemented", "used", "reduced", "achieved", "optimized"]): comm_score = 8
        if word_count > 50 and has_metrics: comm_score = 9

        overall = round((tech_score + comm_score) / 2.0, 1)

        critique_parts = []
        if not has_metrics:
            critique_parts.append("Include quantified engineering metrics (e.g. latency reduced by X%, throughput of Y req/sec, bundle size decreased by Z%) to substantiate your claims.")
        if not has_tech_terms:
            critique_parts.append("Reference concrete tools, protocols, or architectural patterns rather than speaking in abstract generalities.")
        if not critique_parts:
            critique_parts.append("Strong technical explanation! To refine further, clearly articulate the trade-offs (e.g. memory footprint vs CPU efficiency) of the approach you chose.")

        feedback_msg = " ".join(critique_parts)

        # Domain-aware Senior Engineer Model Answers
        role_low = role.lower()
        q_low = question.lower()

        if "frontend" in role_low or "virtual dom" in q_low or "vitals" in q_low or "react" in q_low:
            model_answer = (
                "\"In my frontend web application project, I tackled UI performance and re-render overhead by profiling component render cycles with React DevTools Profiler. "
                "I identified that unnecessary re-renders in our product catalog were caused by inline callback definitions and unmemoized object props. "
                "I wrapped the list item components in React.memo with custom comparison functions and stabilized callback references using useCallback. "
                "Combined with implementing route-level code splitting via React.lazy and Suspense, this dropped initial bundle size by 38% and improved our Google Lighthouse Performance score from 64 to 96, guaranteeing 60fps scrolling on mobile devices.\""
            )
        elif "data" in role_low or "ml" in role_low or "imbalanced" in q_low or "etl" in q_low or "leakage" in q_low or "overfitting" in q_low:
            model_answer = (
                "\"In my machine learning project, I addressed class imbalance (98:2 ratio) by replacing standard Accuracy with Precision-Recall AUC (PR-AUC) and Macro F1-Score as primary evaluation metrics. "
                "To prevent data leakage during preprocessing, I encapsulated all feature scaling, one-hot encoding, and median imputers inside a Scikit-Learn Pipeline that fitted strictly on training folds within a 5-fold Stratified K-Fold setup. "
                "I applied class weighting and tuned decision thresholds, which elevated minority class recall from 24% to 83% while sustaining an 88.5% PR-AUC on completely unseen holdout test data.\""
            )
        elif "devops" in role_low or "cloud" in role_low or "docker" in q_low or "container" in q_low or "pipeline" in q_low or "linux" in q_low:
            model_answer = (
                "\"In my cloud deployment project, I optimized our microservice build and deployment lifecycle by architecting multi-stage Dockerfiles. "
                "The build stage compiled binary dependencies and ran static linting with Ruff, while the minimal runtime stage copied only release artifacts onto an Alpine distroless base image running as a non-root user. "
                "This slashed image size from 850MB to 54MB and eliminated 14 high-severity CVE vulnerabilities. "
                "I automated this in GitHub Actions with self-hosted cache layers, shortening our pull request test and build pipeline duration from 18 minutes down to 3.5 minutes.\""
            )
        else:
            model_answer = (
                "\"In my backend services project, I addressed this concurrency and latency challenge by structuring our endpoints with asynchronous I/O using FastAPI and asyncpg for non-blocking database connections. "
                "To resolve high read latency on user feeds, I analyzed query performance using EXPLAIN ANALYZE and implemented a composite B-Tree index on (tenant_id, created_at), which dropped query latency from 450ms to 28ms. "
                "Furthermore, I introduced an in-memory Redis cache-aside layer with atomic key expiry, allowing the service to reliably sustain 1,200 requests/sec under Apache JMeter load tests with zero dropped connections.\""
            )

        return {
            "technical_score": tech_score,
            "communication_score": comm_score,
            "overall_score": overall,
            "feedback": feedback_msg,
            "model_answer": model_answer
        }

interview_agent = InterviewPrepAgent()
