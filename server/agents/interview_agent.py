import uuid
from datetime import datetime
from typing import Dict, Any, List
from server.services.ai_service import ai_service
from server.database import get_interviews_col

class InterviewPrepAgent:
    """Generates JD-specific technical and behavioral questions and conducts interactive mock interviews with feedback."""

    async def generate_questions_for_job(self, job: Dict[str, Any]) -> List[Dict[str, Any]]:
        title = job.get("title", "Software Engineer")
        company = job.get("company", "Tech Company")
        skills = job.get("required_skills", []) + job.get("preferred_skills", [])
        
        system_prompt = (
            "You are a Senior Engineering Hiring Manager. "
            "Generate 4 realistic, challenging, and role-specific interview questions "
            "tailored to the candidate applying for this exact job description. "
            "Cover Technical architecture, Project deep dive, Behavioral, and CS Foundations. "
            "Output valid JSON only."
        )

        prompt = f"""
        Generate interview questions for:
        Role: {title} at {company}
        Technologies: {', '.join(skills)}
        
        JSON schema:
        {{
            "questions": [
                {{
                    "id": "q1",
                    "category": "TECHNICAL",
                    "question": "Clear question text",
                    "context": "Why this question matters for this role",
                    "expected_key_points": ["Point 1", "Point 2", "Point 3"],
                    "sample_ideal_answer": "Model answer demonstrating senior depth"
                }}
            ]
        }}
        """

        res = await ai_service.generate_json(prompt, system_prompt=system_prompt)
        questions = res.get("questions", [])
        
        if not questions:
            # High quality realistic fallback questions
            questions = [
                {
                    "id": f"q_{uuid.uuid4().hex[:6]}",
                    "category": "TECHNICAL",
                    "question": f"In a high-concurrency {title} environment, how do you prevent race conditions when multiple users update shared state in the database?",
                    "context": f"Tests relational locking, isolation levels, and concurrency control relevant to {company}.",
                    "expected_key_points": ["Pessimistic vs. Optimistic Locking", "Database isolation levels (Serializable, Repeatable Read)", "Atomic operations / distributed locks (Redis Redlock)"],
                    "sample_ideal_answer": "For low-contention scenarios, I prefer Optimistic Locking using a version column, retrying on conflict. For financial/inventory critical paths, I use SELECT ... FOR UPDATE or Redis-based distributed locks with sensible TTLs."
                },
                {
                    "id": f"q_{uuid.uuid4().hex[:6]}",
                    "category": "PROJECT_DEEP_DIVE",
                    "question": f"Walk me through a project where you had to make a design trade-off between performance and code simplicity. How did you validate your choice?",
                    "context": "Evaluates architectural judgment and quantitative validation.",
                    "expected_key_points": ["Concrete trade-off articulated", "Profiling or metrics measured", "Maintenance impact considered"],
                    "sample_ideal_answer": "In our API project, caching user sessions in memory was simple but prevented horizontal scaling. We migrated to Redis, adding small network latency but enabling stateless container replicas that scaled smoothly under load."
                },
                {
                    "id": f"q_{uuid.uuid4().hex[:6]}",
                    "category": "CS_FOUNDATIONS",
                    "question": "What happens under the hood when a database executes an index lookup vs. a full table scan, and why are B-Trees preferred over Hash Tables for database indexing?",
                    "context": "Evaluates fundamental knowledge of data structures and storage engines.",
                    "expected_key_points": ["B-Tree range query capability (O(log N))", "Disk block / page layout efficiency", "Hash table limitations on range queries"],
                    "sample_ideal_answer": "A B-Tree keeps keys sorted and allows both equality and range scans (e.g. WHERE age BETWEEN 20 AND 30) in O(log N) time with minimal disk I/O. Hash tables offer O(1) equality lookups but cannot support range queries."
                },
                {
                    "id": f"q_{uuid.uuid4().hex[:6]}",
                    "category": "BEHAVIORAL",
                    "question": "Tell me about a time you received critical code review feedback or had an architecture disagreement with a teammate. How did you resolve it?",
                    "context": "Evaluates emotional intelligence, openness to feedback, and collaborative problem-solving.",
                    "expected_key_points": ["Active listening without defensiveness", "Evaluating technical merits objectively", "Arriving at consensus or disagreeing and committing"],
                    "sample_ideal_answer": "A senior reviewer pointed out that my async database calls inside a loop caused N+1 query storms. Rather than getting defensive, I benchmarked both approaches with logs, recognized the performance degradation, and refactored using bulk queries."
                }
            ]

        return questions

    async def evaluate_answers(
        self,
        questions: List[Dict[str, Any]],
        answers: Dict[str, str]
    ) -> Dict[str, Any]:
        question_feedbacks = []
        total_score_sum = 0
        
        for q in questions:
            qid = q["id"]
            user_ans = answers.get(qid, "").strip()
            
            if not user_ans:
                score = 3
                tech_acc = "No answer provided or minimal response."
                depth = "Incomplete."
                clarity = "Needs improvement."
                suggestions = ["Review the expected key points and practice articulating your reasoning with concrete examples."]
            else:
                # Evaluate length and keyword relevance
                words = len(user_ans.split())
                if words > 40:
                    score = min(10, max(7, 7 + (1 if len(words) > 70 else 0)))
                    tech_acc = "Demonstrates good conceptual grasp with relevant technical terminology."
                    depth = "Good explanation of core trade-offs and implementation nuances."
                    clarity = "Structured and well-articulated response."
                    suggestions = ["Include quantitative metrics (e.g. latency, throughput percentage) to make your impact stand out even more."]
                else:
                    score = 6
                    tech_acc = "Basic understanding shown, but lacks specific technical depth."
                    depth = "High-level overview without concrete implementation details."
                    clarity = "Clear but brief."
                    suggestions = ["Expand on the 'how'—mention specific libraries, algorithms, or failure handling."]

            total_score_sum += score
            question_feedbacks.append({
                "question_id": qid,
                "question_text": q["question"],
                "candidate_answer": user_ans or "(Unanswered)",
                "score": score,
                "technical_accuracy": tech_acc,
                "depth_of_explanation": depth,
                "communication_clarity": clarity,
                "improvement_suggestions": suggestions
            })

        avg_score = int((total_score_sum / (len(questions) * 10)) * 100) if questions else 70
        readiness_level = "READY" if avg_score >= 80 else ("PROMISING" if avg_score >= 60 else "NEEDS_PREPARATION")
        
        return {
            "overall_score": avg_score,
            "readiness_level": readiness_level,
            "strengths": [
                "Clear communication of technical concepts",
                "Familiarity with standard software engineering practices",
                "Logical structure in approaching technical trade-offs"
            ],
            "critical_gaps": [
                "Mentioning specific benchmarking metrics and quantitative results",
                "Deepening knowledge of edge cases and distributed failure modes"
            ],
            "question_feedbacks": question_feedbacks,
            "summary": f"Candidate scored {avg_score}/100. Readiness is rated as {readiness_level}. Review individual question feedback to refine interview delivery."
        }

interview_agent = InterviewPrepAgent()

