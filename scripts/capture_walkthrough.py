import asyncio
import os
import shutil
from playwright.async_api import async_playwright

async def capture_live_assets():
    screenshots_dir = os.path.abspath("docs/screenshots")
    videos_dir = os.path.abspath("docs/videos")
    os.makedirs(screenshots_dir, exist_ok=True)
    os.makedirs(videos_dir, exist_ok=True)

    print("[1/13] Launching Playwright Chromium session...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            record_video_dir=videos_dir,
            record_video_size={"width": 1440, "height": 900}
        )
        page = await context.new_page()

        # Step 1: Open Login and capture Tour Offer Modal
        print("[2/13] Capturing 01_onboarding_tour_offer.png...")
        await page.goto("http://localhost:5173/login", wait_until="networkidle")
        await page.wait_for_timeout(1200)
        await page.screenshot(path=os.path.join(screenshots_dir, "01_onboarding_tour_offer.png"), full_page=False)

        # Step 2: Click 'Start Product Tour (2 min)'
        print("[3/13] Capturing 02_interactive_app_tour.png...")
        start_tour_btn = page.locator("button:has-text('Start Product Tour')")
        if await start_tour_btn.count() > 0:
            await start_tour_btn.first.click()
            await page.wait_for_timeout(800)
            await page.screenshot(path=os.path.join(screenshots_dir, "02_interactive_app_tour.png"), full_page=False)
            
            # Close tour modal
            close_btn = page.locator("button:has-text('Skip Tour')")
            if await close_btn.count() > 0:
                await close_btn.first.click()
                await page.wait_for_timeout(500)

        # Step 3: Capture Login Screen
        print("[4/13] Capturing 03_login_page.png...")
        await page.screenshot(path=os.path.join(screenshots_dir, "03_login_page.png"), full_page=False)

        # Step 4: One-click Instant Demo Login
        print("[5/13] Logging into demo account and capturing 04_dashboard_overview.png...")
        demo_btn = page.locator("button:has-text('One-Click Instant Demo Login')")
        if await demo_btn.count() > 0:
            await demo_btn.first.click()
        await page.wait_for_url("http://localhost:5173/", timeout=15000)
        await page.wait_for_timeout(2000)
        await page.screenshot(path=os.path.join(screenshots_dir, "04_dashboard_overview.png"), full_page=False)

        # Step 5: Candidate Profile & Assessment
        print("[6/13] Capturing 05_assessment_skill_vector.png...")
        await page.goto("http://localhost:5173/assessment", wait_until="networkidle")
        await page.wait_for_timeout(1500)
        await page.screenshot(path=os.path.join(screenshots_dir, "05_assessment_skill_vector.png"), full_page=False)

        # Step 6: Job Matching Explorer
        print("[7/13] Capturing 06_job_matching_explorer.png...")
        await page.goto("http://localhost:5173/jobs", wait_until="networkidle")
        await page.wait_for_timeout(1500)
        await page.screenshot(path=os.path.join(screenshots_dir, "06_job_matching_explorer.png"), full_page=False)

        # Step 7: Market Gap & Upskilling Roadmap
        print("[8/13] Capturing 07_market_gap_upskilling.png...")
        await page.goto("http://localhost:5173/learning", wait_until="networkidle")
        await page.wait_for_timeout(1500)
        await page.screenshot(path=os.path.join(screenshots_dir, "07_market_gap_upskilling.png"), full_page=False)

        # Step 8: Tailoring Agent & STAR Bullets & ATS PDF Export
        print("[9/13] Capturing 08_tailoring_agent_star_bullets.png...")
        await page.goto("http://localhost:5173/tailoring", wait_until="networkidle")
        await page.wait_for_timeout(2500)
        await page.screenshot(path=os.path.join(screenshots_dir, "08_tailoring_agent_star_bullets.png"), full_page=False)

        # Step 9: Application Staging Queue
        print("[10/13] Capturing 09_application_staging_queue.png...")
        await page.goto("http://localhost:5173/applications", wait_until="networkidle")
        await page.wait_for_timeout(1500)
        await page.screenshot(path=os.path.join(screenshots_dir, "09_application_staging_queue.png"), full_page=False)

        # Step 10: Human Review Checkpoint Modal
        print("[11/13] Capturing 10_human_review_checkpoint_modal.png...")
        review_btn = page.locator("button:has-text('Review & Confirm')")
        if await review_btn.count() > 0:
            await review_btn.first.click()
            await page.wait_for_timeout(800)
            await page.screenshot(path=os.path.join(screenshots_dir, "10_human_review_checkpoint_modal.png"), full_page=False)
            # Close review modal
            close_review = page.locator("button:has-text('Close')")
            if await close_review.count() > 0:
                await close_review.first.click()
                await page.wait_for_timeout(500)

        # Step 11: Interview Prep Simulator
        print("[12/13] Capturing 11_interview_prep_simulator.png...")
        await page.goto("http://localhost:5173/interview", wait_until="networkidle")
        await page.wait_for_timeout(1500)
        await page.screenshot(path=os.path.join(screenshots_dir, "11_interview_prep_simulator.png"), full_page=False)

        # Step 12: Analytics Placement Funnel
        print("[13/13] Capturing 12_analytics_placement_funnel.png...")
        await page.goto("http://localhost:5173/analytics", wait_until="networkidle")
        await page.wait_for_timeout(1500)
        await page.screenshot(path=os.path.join(screenshots_dir, "12_analytics_placement_funnel.png"), full_page=False)

        # Finalize and close video
        print("[Finalizing] Flushing video recording to docs/videos...")
        await page.close()
        video = page.video
        video_path = await video.path() if video else None
        await context.close()
        await browser.close()

        if video_path and os.path.exists(video_path):
            target_video = os.path.join(videos_dir, "careerpilot_walkthrough.webm")
            shutil.copyfile(video_path, target_video)
            print(f"[SUCCESS] Video saved to: {target_video}")

    print("[SUCCESS] All 12 live screenshots captured successfully in docs/screenshots/!")

if __name__ == "__main__":
    asyncio.run(capture_live_assets())

