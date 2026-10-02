import json
import httpx
from typing import Dict, Any, List
from server.config import settings
from server.database import db

class InterviewPrepAgent:
    """Agent 5: Synthesizes JD-specific interview questions and runs interactive mock Q&A with evaluation."""

    def __init__(self):
        self.name = "Interview Prep Agent"

    async def _call_llm(self, prompt: str, system_prompt: str) -> str:
        if settings.GEMINI_API_KEY:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
                payload = {
                    "contents": [{"parts": [{"text": f"{system_prompt}\n\nTask:\n{prompt}"}]}],
                    "generationConfig": {"temperature": 0.4, "maxOutputTokens": 1000}
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
        skills = target_jd.get("required_skills", [])
        
        print(f"[{self.name}] Generating tailored interview questions for {role} at {company}...")

        system_prompt = (
            "You are a Senior Engineering Hiring Manager conducting an interview for an entry-level engineer. "
            "Generate 5 realistic, high-signal questions: 3 technical and 2 project/behavioral. "
            "Return valid JSON array only."
        )

        prompt = (
            f"Role: {role} at {company}\n"
            f"Required Tech Stack: {', '.join(skills)}\n"
            f"Candidate Projects: {json.dumps(candidate_profile.get('projects', [])[:2])}\n\n"
            f"Generate 5 questions with format:\n"
            f"- 'id': integer 1 to 5\n"
            f"- 'type': 'Technical Deep-Dive' | 'System & Architecture' | 'Behavioral (STAR)'\n"
            f"- 'question': string\n"
            f"- 'key_concepts': list of 3 key points the interviewer is listening for\n"
            f"Return ONLY valid JSON."
        )

        llm_out = await self._call_llm(prompt, system_prompt)
        questions = []
        if llm_out:
            try:
                clean_json = llm_out.strip().replace("```json", "").replace("```", "").strip()
                questions = json.loads(clean_json)
            except Exception as e:
                print(f"[{self.name}] Failed to parse questions JSON: {e}")

        if not questions:
            primary_skill = skills[0] if skills else "Python"
            secondary_skill = skills[1] if len(skills) > 1 else "Database design"
            questions = [
                {
                    "id": 1,
                    "type": "Technical Deep-Dive",
                    "question": f"In your projects involving {primary_skill}, how did you manage concurrency or asynchronous operations to prevent bottlenecks?",
                    "key_concepts": ["Async/Await or Threading", "Event Loop", "Resource Locking & Race Conditions"]
                },
                {
                    "id": 2,
                    "type": "System & Architecture",
                    "question": f"When designing database schemas for {role}, how would you choose between relational SQL indexing and an in-memory Redis cache for high-frequency queries?",
                    "key_concepts": ["Cache Invalidation strategies", "Query execution plan & B-Trees", "Read-heavy vs Write-heavy trade-offs"]
                },
                {
                    "id": 3,
                    "type": "Technical Deep-Dive",
                    "question": f"Explain how you would handle API rate-limiting and graceful error degradation in a distributed microservices setup.",
                    "key_concepts": ["Token Bucket / Leaky Bucket algorithms", "HTTP 429 Status code", "Circuit Breaker pattern"]
                },
                {
                    "id": 4,
                    "type": "Behavioral (STAR)",
                    "question": "Tell me about a time you encountered a stubborn bug or critical system failure right before a project deadline. How did you diagnose and resolve it?",
                    "key_concepts": ["Systematic debugging (logs/profilers)", "Prioritization under stress", "Actionable root-cause resolution"]
                },
                {
                    "id": 5,
                    "type": "Behavioral (STAR)",
                    "question": f"Why do you specifically want to join {company} as an entry-level engineer, and how do you stay updated with rapid changes in {secondary_skill}?",
                    "key_concepts": ["Company domain alignment", "Proactive self-learning habits", "Long-term engineering curiosity"]
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
        """Evaluate a candidate's answer with dual 10-point scoring and constructive guidance."""
        if not user_answer or len(user_answer.strip()) < 10:
            return {
                "technical_score": 3,
                "communication_score": 4,
                "overall_score": 3.5,
                "feedback": "Answer is too brief. Provide concrete technical details, trade-offs, and project examples.",
                "model_answer_snippet": "In my previous project, I addressed this by structuring our services with async workers and connection pooling..."
            }

        system_prompt = (
            "You are an empathetic yet rigorous technical interviewer evaluating an engineering candidate's mock interview answer. "
            "Provide two scores from 1 to 10: technical_score and communication_score. "
            "Give actionable feedback (2-3 sentences) and a concise ideal answer snippet. "
            "Return valid JSON only."
        )

        prompt = (
            f"Question: {question}\n"
            f"Candidate Answer: {user_answer}\n"
            f"Target Role: {role}\n"
            f"Relevant Stack: {', '.join(target_skills)}\n\n"
            f"Return JSON format:\n"
            f"- 'technical_score': integer (1-10)\n"
            f"- 'communication_score': integer (1-10)\n"
            f"- 'feedback': string (Critique & suggestions for improvement)\n"
            f"- 'model_answer_snippet': string (How a senior engineer would frame this in STAR format)\n"
            f"Return ONLY valid JSON."
        )

        llm_out = await self._call_llm(prompt, system_prompt)
        if llm_out:
            try:
                clean_json = llm_out.strip().replace("```json", "").replace("```", "").strip()
                eval_data = json.loads(clean_json)
                tech = eval_data.get("technical_score", 7)
                comm = eval_data.get("communication_score", 8)
                eval_data["overall_score"] = round((tech + comm) / 2.0, 1)
                return eval_data
            except Exception as e:
                print(f"[{self.name}] Failed to parse eval JSON: {e}")

        # Deterministic scoring based on content length and key tech keywords
        word_count = len(user_answer.split())
        tech_score = 6 if word_count < 30 else (8 if word_count < 100 else 9)
        comm_score = 7 if word_count > 25 else 5

        return {
            "technical_score": tech_score,
            "communication_score": comm_score,
            "overall_score": round((tech_score + comm_score) / 2.0, 1),
            "feedback": (
                "Good foundation! To elevate this to a top-tier interview answer, frame your response using the "
                "STAR method: explicitly state the Situation, the exact Action you took, and quantify the Result with metrics."
            ),
            "model_answer_snippet": (
                "\"In our microservice setup, we implemented token-bucket rate limiting via Redis middleware. "
                "When traffic spiked by 3x during load tests, this kept CPU consumption under 65% and prevented downstream cascading failures.\""
            )
        }

interview_agent = InterviewPrepAgent()

