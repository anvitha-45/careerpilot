'use client';

import { useState } from 'react';

export default function Home() {
  const [activeTheme, setActiveTheme] = useState<'light' | 'dark'>('dark');
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [jobRoleDescription, setJobRoleDescription] = useState('');
  const [targetPortalUrl, setTargetPortalUrl] = useState('');
  const [isProcessingPipeline, setIsProcessingPipeline] = useState(false);
  const [pipelineResults, setPipelineResults] = useState<{
    extracted_skills: string[];
    missing_skills: string[];
    tailored_bullets: string[];
  } | null>(null);
  const [automationFeedback, setAutomationFeedback] = useState('');

  const themeStyles = {
    light: {
      background: 'bg-[#F9F8F6]',
      textMain: 'text-stone-800',
      textMuted: 'text-stone-500',
      card: 'bg-white border-stone-200',
      input: 'bg-[#F9F8F6] border-stone-200 text-stone-800 placeholder:text-stone-400 focus:border-stone-400 focus:ring-stone-400/20',
      primaryBtn: 'bg-[#C17767] hover:bg-[#A86455] text-white',
      secondaryBtn: 'bg-stone-100 hover:bg-stone-200 text-stone-700 border-stone-200',
      tagVerified: 'bg-[#E8F0EA] text-[#2C5234]',
      tagMissing: 'bg-[#FBEBE9] text-[#8C3A35]',
      panel: 'bg-[#F4F1EB] border-stone-200',
    },
    dark: {
      background: 'bg-[#1C1917]',
      textMain: 'text-stone-200',
      textMuted: 'text-stone-400',
      card: 'bg-[#292524] border-[#3F3936]',
      input: 'bg-[#1C1917] border-[#3F3936] text-stone-200 placeholder:text-stone-500 focus:border-stone-500 focus:ring-stone-500/20',
      primaryBtn: 'bg-[#A86455] hover:bg-[#8F5346] text-white',
      secondaryBtn: 'bg-[#3F3936] hover:bg-[#504A46] text-stone-200 border-[#3F3936]',
      tagVerified: 'bg-[#223528] text-[#84B995]',
      tagMissing: 'bg-[#4A2624] text-[#D88A85]',
      panel: 'bg-[#1C1917] border-[#3F3936]',
    }
  };

  const currentTheme = themeStyles[activeTheme];

  const handleThemeToggle = () => {
    setActiveTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  const executePipeline = async () => {
    if (!resumeFile) {
      alert('Please upload a resume document first.');
      return;
    }

    setIsProcessingPipeline(true);
    setPipelineResults(null);

    const formData = new FormData();
    formData.append('resume_file', resumeFile);
    formData.append('jd_text', jobRoleDescription);
    formData.append('jd_url', targetPortalUrl);

    try {
      const response = await fetch('http://localhost:8000/api/run-pipeline', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      setPipelineResults(data);
    } catch (error) {
      console.error(error);
      alert('Failed to connect to backend pipeline.');
    } finally {
      setIsProcessingPipeline(false);
    }
  };

  const launchBrowser = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/stage-application', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: targetPortalUrl }),
      });
      const data = await response.json();
      setAutomationFeedback(data.status);
    } catch (error) {
      console.error(error);
      setAutomationFeedback('Failed to launch browser automation.');
    }
  };

  return (
    <main className={`min-h-screen font-sans transition-colors duration-300 ${currentTheme.background} ${currentTheme.textMain}`}>
      <div className="max-w-5xl mx-auto px-6 py-12 md:py-20 space-y-12">
        
        <header className="flex flex-col sm:flex-row justify-between items-start gap-4">
          <div className="space-y-3">
            <h1 className="text-4xl font-serif tracking-tight">
              CareerPilot
            </h1>
            <p className={`text-base max-w-2xl leading-relaxed ${currentTheme.textMuted}`}>
              An intentional workspace for career growth. Upload any resume document (PDF, DOCX, TXT) and target role below to autonomously extract skills, analyze gaps, and tailor your narrative.
            </p>
          </div>

          <button
            onClick={handleThemeToggle}
            className={`p-2.5 rounded-lg border transition-all flex items-center justify-center ${currentTheme.secondaryBtn}`}
          >
            {activeTheme === 'light' ? (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path></svg>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>
            )}
          </button>
        </header>

        <div className="grid md:grid-cols-2 gap-8">
          <div className="space-y-3">
            <label className={`text-xs font-semibold uppercase tracking-widest ${currentTheme.textMuted}`}>
              Candidate Resume (PDF, DOCX, TXT)
            </label>
            <div className={`w-full h-64 rounded-xl p-6 flex flex-col items-center justify-center border border-dashed transition-all ${currentTheme.input}`}>
              <svg className="w-10 h-10 mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
              <input
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    setResumeFile(e.target.files[0]);
                  }
                }}
                className="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-[#C17767] file:text-white hover:file:bg-[#A86455] cursor-pointer"
              />
              {resumeFile && (
                <p className="mt-4 text-xs font-medium truncate max-w-full">
                  Selected: {resumeFile.name}
                </p>
              )}
            </div>
          </div>

          <div className="space-y-3">
            <label className={`text-xs font-semibold uppercase tracking-widest ${currentTheme.textMuted}`}>
              Target Role Requirements
            </label>
            <textarea
              className={`w-full h-64 rounded-xl p-5 text-sm focus:outline-none focus:ring-2 transition-all resize-none border shadow-sm ${currentTheme.input}`}
              placeholder="Paste the job description here..."
              value={jobRoleDescription}
              onChange={(e) => setJobRoleDescription(e.target.value)}
            />
          </div>
        </div>

        <div className={`rounded-2xl border p-6 md:p-8 flex flex-col md:flex-row gap-6 items-end transition-colors shadow-sm ${currentTheme.card}`}>
          <div className="flex-1 w-full space-y-3">
            <label className={`block text-xs font-semibold uppercase tracking-widest ${currentTheme.textMuted}`}>
              Application Portal
            </label>
            <input
              type="text"
              className={`w-full rounded-xl px-5 py-3.5 text-sm focus:outline-none focus:ring-2 transition-all border ${currentTheme.input}`}
              placeholder="https://company.com/careers/apply"
              value={targetPortalUrl}
              onChange={(e) => setTargetPortalUrl(e.target.value)}
            />
          </div>
          <button
            onClick={executePipeline}
            disabled={isProcessingPipeline}
            className={`w-full md:w-auto h-[48px] px-8 rounded-xl font-medium text-sm transition-all disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-sm ${currentTheme.primaryBtn}`}
          >
            {isProcessingPipeline ? 'Synthesizing...' : 'Synthesize Profile'}
          </button>
        </div>

        {pipelineResults && (
          <div className={`rounded-2xl border transition-colors shadow-sm overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-700 ${currentTheme.card}`}>
            
            <div className={`px-8 py-6 border-b flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 ${activeTheme === 'light' ? 'border-stone-200' : 'border-[#3F3936]'}`}>
              <div>
                <h2 className="text-xl font-serif">Editorial Synthesis</h2>
                <p className={`text-sm mt-1 ${currentTheme.textMuted}`}>Tailored insights based on the provided parameters.</p>
              </div>
              <button
                onClick={launchBrowser}
                className={`h-10 px-5 rounded-lg border font-medium text-sm transition-all flex items-center gap-2 shadow-sm ${currentTheme.secondaryBtn}`}
              >
                Stage Application
              </button>
            </div>

            <div className="p-8 space-y-10">
              <div className="grid md:grid-cols-2 gap-10">
                <div className="space-y-4">
                  <h3 className="text-xs font-semibold uppercase tracking-widest flex items-center gap-2">
                    Verified Capabilities
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {(pipelineResults.extracted_skills ?? []).map((skill, index) => (
                      <span key={index} className={`text-xs px-3 py-1.5 rounded-md font-medium ${currentTheme.tagVerified}`}>
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="text-xs font-semibold uppercase tracking-widest flex items-center gap-2">
                    Identified Gaps
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {(pipelineResults.missing_skills ?? []).map((skill, index) => (
                      <span key={index} className={`text-xs px-3 py-1.5 rounded-md font-medium ${currentTheme.tagMissing}`}>
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="space-y-4 pt-6">
                <h3 className="text-xs font-semibold uppercase tracking-widest">
                  Tailored Narrative & Materials
                </h3>
                <div className={`rounded-xl p-8 text-sm leading-loose border shadow-inner ${currentTheme.panel}`}>
                  {(pipelineResults.tailored_bullets ?? []).map((bullet, index) => (
                    <div key={index} className="mb-5 last:mb-0">
                      {bullet}
                    </div>
                  ))}
                </div>
              </div>

              {automationFeedback && (
                <div className="pt-2">
                  <p className={`text-sm font-medium italic ${activeTheme === 'light' ? 'text-[#C17767]' : 'text-[#A86455]'}`}>
                    {automationFeedback}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}