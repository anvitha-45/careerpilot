import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

load_dotenv()

class VectorPipeline:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        
        self.language_model = ChatGoogleGenerativeAI(
            model="gemini-3.5-flash", 
            temperature=0.1,
            api_key=api_key
        )
        self.embedding_model = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=api_key
        )

    async def ainvoke(self, pipeline_state):
        resume_content = pipeline_state.get("resumeText", "")
        job_requirements = pipeline_state.get("jobDescription", "")
        
        # 1. Extract required skills
        extraction_prompt = f"Extract a comma-separated list of core technical skills from this job description. Only output the list.\n\n{job_requirements}"
        extracted_skills_response = await self.language_model.ainvoke(extraction_prompt)
        
        raw_content = extracted_skills_response.content
        if isinstance(raw_content, list):
            text_content = "".join([block.get("text", "") if isinstance(block, dict) else str(block) for block in raw_content])
        else:
            text_content = str(raw_content)
            
        target_skills = [skill.strip() for skill in text_content.split(',') if skill.strip()]
        
        # 2. Vectorize the Resume
        candidate_document = [Document(page_content=resume_content)]
        vector_database = FAISS.from_documents(candidate_document, self.embedding_model)
        
        verified_capabilities = []
        identified_gaps = []
        
        # --- NEW: Weighted ATS Scoring Logic ---
        total_skills_count = len(target_skills)
        earned_points = 0
        
        for skill in target_skills:
            search_results = vector_database.similarity_search_with_score(skill, k=1)
            if search_results:
                _, similarity_score = search_results[0]
                
                # Exact / Very Close Match
                if similarity_score < 0.3:
                    verified_capabilities.append(skill)
                    earned_points += 100
                # Strong Semantic Match
                elif similarity_score < 0.5:
                    verified_capabilities.append(skill)
                    earned_points += 85
                # Loose Match
                elif similarity_score < 0.7:
                    verified_capabilities.append(skill)
                    earned_points += 50
                # Missing
                else:
                    identified_gaps.append(skill)
            else:
                identified_gaps.append(skill)
                
        # Calculate the final percentage
        if total_skills_count > 0:
            overall_ats_score = int(earned_points / total_skills_count)
        else:
            overall_ats_score = 0
        # ---------------------------------------
                
        # 3. Generate tailored materials
        generation_prompt = f"""
        Write 3 optimized resume bullets and a cover letter for this job.
        Verified skills: {', '.join(verified_capabilities)}
        Missing skills: {', '.join(identified_gaps)}
        Job: {job_requirements}
        
        Return ONLY a valid JSON object with these exact keys: 
        "tailored_bullets" (array of strings)
        "cover_letter" (string)
        "interview_questions" (array of strings)
        """
        
        materials_response = await self.language_model.ainvoke(generation_prompt)
        
        try:
            materials_content = materials_response.content
            if isinstance(materials_content, list):
                materials_text = "".join([block.get("text", "") if isinstance(block, dict) else str(block) for block in materials_content])
            else:
                materials_text = str(materials_content)
                
            clean_json_string = materials_text.replace("```json", "").replace("```", "").strip()
            generated_materials = json.loads(clean_json_string)
        except Exception as e:
            print(f"JSON Parsing Error: {str(e)}")
            generated_materials = {
                "tailored_bullets": ["⚠️ AI output formatting error."],
                "cover_letter": "",
                "interview_questions": []
            }
            
        # 4. Update state with the new ATS Score
        pipeline_state["candidateSkills"] = verified_capabilities
        pipeline_state["missingSkills"] = identified_gaps
        pipeline_state["tailoredBullets"] = generated_materials.get("tailored_bullets", [])
        pipeline_state["coverLetter"] = generated_materials.get("cover_letter", "")
        pipeline_state["interviewQuestions"] = generated_materials.get("interview_questions", [])
        pipeline_state["atsScore"] = overall_ats_score # Added to state
        
        return pipeline_state

applicationWorkflow = VectorPipeline()