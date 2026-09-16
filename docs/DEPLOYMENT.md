# CareerPilot AI — Cloud Deployment & Public Sharing Guide 🌐

This guide outlines two proven methods to give others a live public link to use **CareerPilot AI**:

---

## 🌟 Method 1: Permanent 24/7 Free Cloud Hosting on Render (Recommended)

This method deploys CareerPilot to the cloud for **100% free**, giving you a permanent public HTTPS URL (e.g. `https://careerpilot-ai.onrender.com`) that anyone in the world can open on their phone, tablet, or laptop 24/7 — even when your computer is shut down.

### Step-by-Step Instructions:

1. **Sign Up / Log In to Render**:
   - Go to **[https://render.com](https://render.com)**.
   - Click **"Get Started"** and sign in with your GitHub account (`anvitha-45`).

2. **Deploy Using the Blueprint (1-Click)**:
   - On the Render dashboard, click the **"New +"** button in the top right.
   - Select **"Blueprint"**.
   - Select your repository: **`anvitha-45/careerpilot`**.
   - Render will automatically detect the [`render.yaml`](../render.yaml) file we created!
   - Click **"Apply"**.

3. **Wait for Build & Launch (Approx. 2–3 minutes)**:
   - Render automatically:
     - Builds the React client (`npm run build`).
     - Installs Python dependencies (`pip install -r server/requirements.txt`).
     - Starts FastAPI (`uvicorn server.main:app`).
   - Your live website link will appear at the top of the dashboard:  
     👉 **`https://careerpilot-ai.onrender.com`** *(or your chosen name)*.

4. **(Optional) Add Free API Keys for Real LLM Generation**:
   - In your Render service settings under **Environment Variables**, you can add:
     - `GEMINI_API_KEY`: *(Your Google AI Studio free key)*
     - `GROQ_API_KEY`: *(Your Groq free key)*
   - *Note: If no keys are added, CareerPilot's built-in deterministic NLP engine handles all requests with zero cloud spend!*

---

## ⚡ Method 2: Instant 30-Second Public Link (While Your Laptop is On)

If you want an immediate link right now to share with a friend, recruiter, or professor while testing:

### Option A: Using Free Cloudflare Tunnel (No Signup Required)
1. Start the application locally:
   ```powershell
   .\run_dev.ps1
   ```
2. In a second PowerShell window, run:
   ```powershell
   npx cloudflared tunnel --url http://localhost:5173
   ```
3. Cloudflare will print a live public HTTPS link in your terminal:
   ```text
   +--------------------------------------------------------------------------------------------+
   |  Your quick Tunnel has been created! Visit it at:                                          |
   |  https://unique-random-words.trycloudflare.com                                             |
   +--------------------------------------------------------------------------------------------+
   ```
4. Copy and send that link to anyone — they can open it immediately on their phone or computer!

### Option B: Using Localtunnel
1. Start the application locally:
   ```powershell
   .\run_dev.ps1
   ```
2. In a second PowerShell window, run:
   ```powershell
   npx localtunnel --port 5173
   ```
3. It gives you a public URL (e.g. `https://careerpilot-demo.loca.lt`) to share.

---

## 🚀 Comparison Summary

| Feature | Method 1: Render.com Cloud | Method 2: Cloudflare Tunnel |
| :--- | :--- | :--- |
| **Availability** | **24/7 Permanent (Always online)** | Only while your computer is on |
| **URL Format** | `https://careerpilot-ai.onrender.com` | `https://xyz.trycloudflare.com` |
| **Setup Time** | ~2–3 minutes | ~30 seconds |
| **Cost** | **$0.00 (100% Free Tier)** | **$0.00 (100% Free)** |
| **Best For** | **Resumes, Portfolio, LinkedIn, Evaluators** | **Instant live screen testing with friends** |

