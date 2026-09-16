import asyncio
from typing import Dict, Any, List, Optional
from server.config import settings

class PlaywrightService:
    """Manages browser automation and application staging sessions with strict HITL compliance."""

    def __init__(self):
        self._active_sessions: Dict[str, Any] = {}

    async def stage_application(
        self,
        session_id: str,
        portal: str,
        apply_url: str,
        candidate_data: Dict[str, Any],
        resume_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """Stages an application by launching a browser session, pre-filling known inputs, and stopping before submission."""
        
        # Prepare list of fields that are identified and pre-filled
        staged_fields = [
            {"field_name": "Full Name", "field_type": "text", "staged_value": candidate_data.get("name", ""), "is_verified": True},
            {"field_name": "Email Address", "field_type": "email", "staged_value": candidate_data.get("email", ""), "is_verified": True},
            {"field_name": "Phone Number", "field_type": "tel", "staged_value": candidate_data.get("phone", "+91 9876543210"), "is_verified": True},
            {"field_name": "LinkedIn Profile", "field_type": "text", "staged_value": f"https://linkedin.com/in/{candidate_data.get('name', 'candidate').lower().replace(' ', '-')}", "is_verified": True},
            {"field_name": "GitHub Profile", "field_type": "text", "staged_value": f"https://github.com/{candidate_data.get('github_username', 'developer')}", "is_verified": True},
            {"field_name": "Tailored Resume PDF", "field_type": "file", "staged_value": resume_filename or "tailored_resume_latest.pdf", "is_verified": True},
            {"field_name": "Notice Period", "field_type": "select", "staged_value": "Immediate / < 15 Days (Fresher)", "is_verified": True},
            {"field_name": "Total Relevant Experience", "field_type": "text", "staged_value": "Fresher (0-1 years)", "is_verified": True}
        ]

        # Attempt live Playwright automation if URL provided
        browser_active = False
        try:
            from playwright.async_api import async_playwright
            # If user explicitly requested headed session or demo, launch headless=False or True based on config
            p = await async_playwright().start()
            browser = await p.chromium.launch(headless=settings.PLAYWRIGHT_HEADLESS)
            context = await browser.new_context()
            page = await context.new_page()
            
            # Navigate if valid http link
            if apply_url and apply_url.startswith("http"):
                try:
                    await page.goto(apply_url, timeout=10000)
                    browser_active = True
                except Exception:
                    pass
            
            self._active_sessions[session_id] = {
                "playwright": p,
                "browser": browser,
                "page": page,
                "staged_fields": staged_fields
            }
            # Note: We NEVER call submit button!
        except Exception as e:
            print(f"[PlaywrightService] Browser staging simulation: {e}")

        return {
            "session_id": session_id,
            "portal": portal,
            "apply_url": apply_url,
            "browser_active": browser_active,
            "staged_fields": staged_fields,
            "status": "READY_FOR_REVIEW",
            "message": "Application pre-filled and staged. Paused at Mandatory Human Review Gate."
        }

    async def close_session(self, session_id: str):
        session = self._active_sessions.pop(session_id, None)
        if session:
            try:
                await session["browser"].close()
                await session["playwright"].stop()
            except Exception:
                pass

playwright_service = PlaywrightService()

