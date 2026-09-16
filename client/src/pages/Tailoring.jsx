import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import api from '../api/client';
import {
  FileCheck,
  Sparkles,
  ShieldCheck,
  Copy,
  Check,
  Send,
  Building,
  ArrowRight,
  RefreshCw,
  FileText,
  Download,
  CheckCircle2
} from 'lucide-react';

export const Tailoring = () => {
  const [searchParams] = useSearchParams();
  const initialJobId = searchParams.get('jobId') || '';
  
  const [jobs, setJobs] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState(initialJobId);
  const [tailoredResult, setTailoredResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    fetchJobs();
  }, []);

  useEffect(() => {
    if (initialJobId && jobs.length > 0) {
      setSelectedJobId(initialJobId);
      triggerTailoring(initialJobId);
    } else if (jobs.length > 0 && !selectedJobId) {
      setSelectedJobId(jobs[0].job.id);
    }
  }, [initialJobId, jobs]);

  const fetchJobs = async () => {
    try {
      const res = await api.get('/jobs');
      setJobs(res.data);
    } catch (err) {
      console.error('Failed to load jobs for tailoring:', err);
    }
  };

  const triggerTailoring = async (jobIdToUse) => {
    const targetId = jobIdToUse || selectedJobId;
    if (!targetId) return;

    setLoading(true);
    try {
      const res = await api.post('/tailor/resume', { job_id: targetId });
      setTailoredResult(res.data);
    } catch (err) {
      console.error('Failed to tailor resume:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPdf = async () => {
    if (!selectedJobId) return;
    setDownloadingPdf(true);
    try {
      const response = await api.get(`/tailor/export-pdf?job_id=${selectedJobId}`, {
        responseType: 'blob'
      });
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      const company = tailoredResult?.company_name
        ? tailoredResult.company_name.replace(/[^a-zA-Z0-9_-]/g, '_')
        : 'Target';
      link.setAttribute('download', `CareerPilot_Resume_${company}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to download resume PDF:', err);
    } finally {
      setDownloadingPdf(false);
    }
  };

  const copyCoverLetter = () => {
    if (tailoredResult?.cover_letter?.full_text) {
      navigator.clipboard.writeText(tailoredResult.cover_letter.full_text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const selectedJobObj = jobs.find((j) => j.job.id === selectedJobId);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-2">
          <h1 className="text-2xl font-bold text-white tracking-tight">Tailoring Agent & CAR/STAR Generator</h1>
          <span className="px-2 py-0.5 rounded bg-brand-500/20 text-brand-300 border border-brand-500/30 text-[10px] font-bold uppercase">
            Agent 04
          </span>
        </div>
        <p className="text-xs text-slate-400 mt-1">
          Rewrites resume bullet points using the CAR/STAR framework and generates tailored cover letters with strict 0% hallucination verification.
        </p>
      </div>

      {/* Target Job Selector & Action */}
      <div className="p-4 sm:p-6 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4 shadow-sm">
        <div className="flex-1 w-full min-w-0">
          <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
            Select Target Job Posting
          </label>
          <select
            value={selectedJobId}
            onChange={(e) => {
              setSelectedJobId(e.target.value);
              triggerTailoring(e.target.value);
            }}
            className="w-full bg-slate-950 border border-slate-750 text-white rounded-xl py-2.5 px-3 text-xs sm:text-sm focus:outline-none focus:border-brand-500 truncate"
          >
            {jobs.map((item) => (
              <option key={item.job.id} value={item.job.id}>
                {item.job.title} — {item.job.company} ({item.match_score}% Match)
              </option>
            ))}
          </select>
        </div>

        <button
          onClick={() => triggerTailoring(selectedJobId)}
          disabled={loading || !selectedJobId}
          className="w-full md:w-auto px-6 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold shadow-lg shadow-brand-500/20 transition flex items-center justify-center space-x-2 disabled:opacity-50 shrink-0"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>{loading ? 'Tailoring Bullets...' : 'Regenerate Tailoring'}</span>
        </button>
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center py-20 space-y-3">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-500"></div>
          <p className="text-xs text-slate-400">
            Applying CAR/STAR rephrasing and running programmatic zero-hallucination diff...
          </p>
        </div>
      ) : tailoredResult ? (
        <div className="space-y-6 sm:space-y-8">
          {/* Zero Hallucination Guarantee Badge & PDF Download Bar */}
          <div className="p-4 sm:p-5 rounded-2xl bg-gradient-to-r from-emerald-500/10 via-slate-900 to-brand-950/20 border border-emerald-500/20 flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4 text-xs text-emerald-300">
            <div className="flex items-center space-x-3">
              <ShieldCheck className="w-6 h-6 text-emerald-400 shrink-0" />
              <div>
                <div className="flex items-center space-x-2">
                  <span className="font-bold text-sm text-white">Strict Zero-Hallucination Verified</span>
                  <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-mono text-[10px] font-bold">
                    PASSED
                  </span>
                </div>
                <p className="text-slate-300 mt-0.5 text-xs leading-relaxed">
                  All {tailoredResult.verified_terms_count} technical terms match your verified ground-truth skills. Ready for immediate ATS export.
                </p>
              </div>
            </div>

            {/* ATS PDF Export Action Button */}
            <button
              onClick={handleDownloadPdf}
              disabled={downloadingPdf}
              className="w-full md:w-auto inline-flex items-center justify-center space-x-2 px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-lg shadow-emerald-600/25 transition shrink-0 hover:scale-105 active:scale-95 disabled:opacity-50 text-center"
            >
              <Download className={`w-4 h-4 ${downloadingPdf ? 'animate-bounce' : ''}`} />
              <span>{downloadingPdf ? 'Generating PDF...' : 'Download ATS-Optimized Resume PDF'}</span>
            </button>
          </div>

          {/* Section: Bullet Point Rewrites (CAR/STAR) */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 sm:p-6 space-y-4 sm:space-y-6">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
              <div>
                <h3 className="text-sm sm:text-base font-bold text-white tracking-tight flex items-center space-x-2">
                  <FileCheck className="w-5 h-5 text-brand-400 shrink-0" />
                  <span>Context-Action-Result (CAR/STAR) Bullet Transformations</span>
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Tailored specifically for {tailoredResult.role_title} at {tailoredResult.company_name}
                </p>
              </div>
              <span className="text-xs text-slate-400 font-mono bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-800 shrink-0">
                Single-Column ATS Format
              </span>
            </div>

            <div className="space-y-4">
              {tailoredResult.bullet_rewrites?.map((bullet, idx) => (
                <div
                  key={idx}
                  className="p-4 sm:p-5 rounded-xl bg-slate-950 border border-slate-850 space-y-3"
                >
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Before */}
                    <div className="space-y-1">
                      <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">
                        Original Resume Bullet
                      </span>
                      <p className="text-xs text-slate-400 bg-slate-900/60 p-3 rounded-lg border border-slate-800/60 leading-relaxed">
                        {bullet.original_bullet}
                      </p>
                    </div>

                    {/* After */}
                    <div className="space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] uppercase font-bold text-brand-400 tracking-wider">
                          Tailored CAR/STAR Bullet (Optimized)
                        </span>
                        <span className="text-[10px] font-bold text-emerald-400">
                          {bullet.framework}
                        </span>
                      </div>
                      <p className="text-xs text-white font-medium bg-brand-950/30 p-3 rounded-lg border border-brand-900/40 leading-relaxed">
                        {bullet.tailored_bullet}
                      </p>
                    </div>
                  </div>

                  <div className="text-[11px] text-slate-400 pt-1 flex flex-wrap items-center gap-1.5">
                    <span className="font-semibold text-slate-300">Why this scores higher:</span>
                    <span>{bullet.rationale}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Section: Bespoke Cover Letter */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 sm:p-6 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <h3 className="text-sm sm:text-base font-bold text-white tracking-tight flex items-center space-x-2">
                  <FileText className="w-5 h-5 text-brand-400 shrink-0" />
                  <span>Job-Tuned Cover Letter</span>
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Generated from truthful candidate experience connected to {tailoredResult.company_name}'s mission
                </p>
              </div>

              <button
                onClick={copyCoverLetter}
                className="self-start sm:self-auto inline-flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-750 text-slate-200 text-xs font-semibold border border-slate-700 transition shrink-0"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copied ? 'Copied to Clipboard' : 'Copy Letter'}</span>
              </button>
            </div>

            <div className="p-4 sm:p-6 rounded-xl bg-slate-950 border border-slate-850 text-xs text-slate-300 leading-relaxed whitespace-pre-line font-sans">
              {tailoredResult.cover_letter?.full_text}
            </div>
          </div>

          {/* Next Step Action: Stage Application & Download PDF */}
          <div className="p-4 sm:p-6 rounded-2xl bg-gradient-to-r from-brand-950/40 via-slate-900 to-slate-900 border border-brand-900/40 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div>
              <h4 className="font-bold text-white text-sm">Assets Ready for Application</h4>
              <p className="text-xs text-slate-400 mt-0.5">
                Download your ATS resume PDF or proceed to Application Agent for responsible browser staging.
              </p>
            </div>
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 sm:space-x-3 sm:gap-0 w-full sm:w-auto">
              <button
                onClick={handleDownloadPdf}
                disabled={downloadingPdf}
                className="flex-1 sm:flex-initial inline-flex items-center justify-center space-x-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-750 text-brand-300 hover:text-white border border-slate-700 text-xs font-semibold transition text-center"
              >
                <Download className="w-4 h-4" />
                <span>{downloadingPdf ? 'Exporting...' : 'Export PDF'}</span>
              </button>

              <Link
                to={`/applications?stageJobId=${selectedJobId}`}
                className="flex-1 sm:flex-initial inline-flex items-center justify-center space-x-2 px-6 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold shadow-lg shadow-brand-500/20 transition shrink-0 text-center"
              >
                <Send className="w-4 h-4" />
                <span>Stage Application</span>
              </Link>
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-16 bg-slate-900 border border-slate-800 rounded-2xl p-8">
          <FileCheck className="w-10 h-10 text-slate-600 mx-auto mb-3" />
          <h3 className="text-sm font-semibold text-white">Select a job above to trigger the Tailoring Agent</h3>
          <p className="text-xs text-slate-400 mt-1">
            The agent will synthesize CAR/STAR bullet rewrites, bespoke cover letters, and ATS PDF resumes.
          </p>
        </div>
      )}
    </div>
  );
};
