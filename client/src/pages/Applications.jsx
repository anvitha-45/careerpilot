import React, { useState, useEffect, useRef, useMemo } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import api from '../api/client';
import { HumanReviewModal } from '../components/HumanReviewModal';
import {
  Send,
  ShieldCheck,
  CheckCircle2,
  Clock,
  ExternalLink,
  Play,
  Trash2,
  AlertCircle,
  Building,
  Sparkles,
  Download
} from 'lucide-react';

export const Applications = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const autoStageJobId = searchParams.get('stageJobId');
  const hasAutoStagedRef = useRef(false);

  const [applications, setApplications] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState(autoStageJobId || '');
  const [loading, setLoading] = useState(true);
  const [staging, setStaging] = useState(false);

  // Deduplicate applications by job_id so multiple stages of the same job don't produce redundant cards
  const uniqueApplications = useMemo(() => {
    const map = new Map();
    for (const app of applications) {
      const key = app.job_id || app.id;
      if (!map.has(key)) {
        map.set(key, app);
      } else {
        const existing = map.get(key);
        if (app.status === 'USER_SUBMITTED' && existing.status !== 'USER_SUBMITTED') {
          map.set(key, app);
        } else if (new Date(app.updated_at || 0) > new Date(existing.updated_at || 0)) {
          map.set(key, app);
        }
      }
    }
    return Array.from(map.values());
  }, [applications]);

  // Review Modal State
  const [reviewModalOpen, setReviewModalOpen] = useState(false);
  const [activeAppForReview, setActiveAppForReview] = useState(null);
  const [confirming, setConfirming] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (autoStageJobId && jobs.length > 0 && !hasAutoStagedRef.current) {
      hasAutoStagedRef.current = true;
      setSelectedJobId(autoStageJobId);
      // Remove query param from URL so it doesn't re-trigger
      const newParams = new URLSearchParams(searchParams);
      newParams.delete('stageJobId');
      setSearchParams(newParams, { replace: true });
      handleStageApplication(autoStageJobId);
    }
  }, [autoStageJobId, jobs]);

  const fetchData = async () => {
    try {
      const [appsRes, jobsRes] = await Promise.all([
        api.get('/applications'),
        api.get('/jobs')
      ]);
      setApplications(appsRes.data);
      setJobs(jobsRes.data);
      if (!selectedJobId && jobsRes.data.length > 0) {
        setSelectedJobId(jobsRes.data[0].job.id);
      }
    } catch (err) {
      console.error('Failed to load application data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStageApplication = async (jobIdToStage) => {
    const targetId = jobIdToStage || selectedJobId;
    if (!targetId) return;

    setStaging(true);
    try {
      const res = await api.post('/applications/stage', { job_id: targetId });
      const stagedApp = { ...res.data, id: res.data.id || res.data._id };
      setActiveAppForReview(stagedApp);
      setReviewModalOpen(true);
      // Refresh applications list only to prevent triggering jobs dependency
      const appsRes = await api.get('/applications');
      setApplications(appsRes.data);
    } catch (err) {
      console.error('Failed to stage application:', err);
    } finally {
      setStaging(false);
    }
  };

  const handleConfirmSubmission = async (appId) => {
    const targetId = appId || activeAppForReview?.id || activeAppForReview?._id;
    if (!targetId) {
      console.warn('No application ID found to confirm');
      setReviewModalOpen(false);
      setActiveAppForReview(null);
      return;
    }

    setConfirming(true);
    try {
      await api.post(`/applications/${targetId}/confirm`);
      setReviewModalOpen(false);
      setActiveAppForReview(null);
      const appsRes = await api.get('/applications');
      setApplications(appsRes.data);
    } catch (err) {
      console.error('Failed to confirm application submission:', err);
      // Close modal gracefully even if already confirmed
      setReviewModalOpen(false);
      setActiveAppForReview(null);
      const appsRes = await api.get('/applications');
      setApplications(appsRes.data);
    } finally {
      setConfirming(false);
    }
  };

  const handleDeleteApplication = async (appId) => {
    try {
      await api.delete(`/applications/${appId}`);
      await fetchData();
    } catch (err) {
      console.error('Failed to delete application:', err);
    }
  };

  const handleDownloadResumePdf = async (jobId, companyName) => {
    try {
      const response = await api.get(`/tailor/export-pdf?job_id=${jobId}`, {
        responseType: 'blob'
      });
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      const company = companyName ? companyName.replace(/[^a-zA-Z0-9_-]/g, '_') : 'Target';
      link.setAttribute('download', `CareerPilot_Resume_${company}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to download resume PDF:', err);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'READY_FOR_REVIEW':
        return (
          <span className="px-2.5 py-1 rounded-full text-xs font-bold uppercase bg-amber-500/15 border border-amber-500/30 text-amber-300 flex items-center space-x-1.5">
            <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping"></span>
            <span>Awaiting Human Review</span>
          </span>
        );
      case 'USER_SUBMITTED':
        return (
          <span className="px-2.5 py-1 rounded-full text-xs font-bold uppercase bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 flex items-center space-x-1.5">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Submitted (ToS Compliant)</span>
          </span>
        );
      case 'INTERVIEW':
        return (
          <span className="px-2.5 py-1 rounded-full text-xs font-bold uppercase bg-indigo-500/15 border border-indigo-500/30 text-indigo-300">
            Interview Scheduled
          </span>
        );
      default:
        return (
          <span className="px-2.5 py-1 rounded-full text-xs font-bold uppercase bg-slate-800 border border-slate-700 text-slate-300">
            {status}
          </span>
        );
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-2">
          <h1 className="text-2xl font-bold text-white tracking-tight">Application Agent & Staging Manager</h1>
          <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 text-[10px] font-bold uppercase">
            Agent 05 (HITL Core)
          </span>
        </div>
        <p className="text-xs text-slate-400 mt-1">
          Automates browser form pre-filling on Naukri, LinkedIn, and ATS portals. Strictly halts at the Human Review Gate.
        </p>
      </div>

      {/* Trigger Staging Section */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-sm">
        <div className="flex-1 w-full">
          <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
            Select Shortlisted Job to Stage
          </label>
          <select
            value={selectedJobId}
            onChange={(e) => setSelectedJobId(e.target.value)}
            className="w-full bg-slate-950 border border-slate-750 text-white rounded-xl py-2.5 px-3 text-sm focus:outline-none focus:border-brand-500"
          >
            {jobs.map((item) => (
              <option key={item.job.id} value={item.job.id}>
                {item.job.title} — {item.job.company} ({item.job.portal})
              </option>
            ))}
          </select>
        </div>

        <button
          onClick={() => handleStageApplication(selectedJobId)}
          disabled={staging || !selectedJobId}
          className="w-full md:w-auto px-6 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold shadow-lg shadow-brand-500/20 transition flex items-center justify-center space-x-2 disabled:opacity-50 shrink-0 self-end"
        >
          <Play className={`w-4 h-4 ${staging ? 'animate-pulse' : ''}`} />
          <span>{staging ? 'Staging Browser Session...' : 'Stage New Application'}</span>
        </button>
      </div>

      {/* Applications List */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-white tracking-tight">Active Applications & Review Queue</h2>
          <span className="text-xs text-slate-400 font-medium">
            {uniqueApplications.length} Active Target Roles
          </span>
        </div>

        {loading ? (
          <div className="text-center py-12 text-slate-400 text-xs">Loading application pipeline...</div>
        ) : uniqueApplications.length === 0 ? (
          <div className="text-center py-16 bg-slate-900 border border-slate-800 rounded-2xl p-8">
            <ShieldCheck className="w-10 h-10 text-slate-600 mx-auto mb-3" />
            <h3 className="text-sm font-semibold text-white">No Staged Applications Yet</h3>
            <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
              Select a role above or navigate to the Job Explorer to stage your first human-reviewed application.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {uniqueApplications.map((app) => (
              <div
                key={app.id}
                className="p-6 rounded-2xl bg-slate-900 border border-slate-800 hover:border-slate-750 transition flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-sm"
              >
                <div className="space-y-2 flex-1">
                  <div className="flex items-center space-x-3">
                    <h3 className="text-base font-bold text-white">{app.job_title}</h3>
                    <span className="text-xs px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300">
                      {app.portal}
                    </span>
                  </div>

                  <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-400">
                    <span className="font-semibold text-slate-200">{app.company_name}</span>
                    <span>•</span>
                    <span>Staged: {new Date(app.created_at || Date.now()).toLocaleDateString()}</span>
                    {app.applied_at && (
                      <>
                        <span>•</span>
                        <span className="text-emerald-400 font-medium">
                          Submitted: {new Date(app.applied_at).toLocaleDateString()}
                        </span>
                      </>
                    )}
                  </div>

                  <div className="pt-1">{getStatusBadge(app.status)}</div>
                </div>

                {/* Actions */}
                <div className="flex items-center space-x-3 self-end md:self-center">
                  {app.status === 'READY_FOR_REVIEW' && (
                    <button
                      onClick={() => {
                        setActiveAppForReview(app);
                        setReviewModalOpen(true);
                      }}
                      className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 text-xs font-bold shadow-md shadow-amber-500/20 transition"
                    >
                      <ShieldCheck className="w-4 h-4" />
                      <span>Review & Confirm</span>
                    </button>
                  )}

                  {/* Download Staged ATS Resume PDF */}
                  <button
                    onClick={() => handleDownloadResumePdf(app.job_id, app.company_name)}
                    className="p-2 rounded-lg bg-slate-800 hover:bg-slate-750 text-brand-300 hover:text-white border border-slate-700 transition"
                    title="Download Tailored ATS Resume PDF"
                  >
                    <Download className="w-4 h-4" />
                  </button>

                  {app.apply_url && (
                    <a
                      href={app.apply_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-2 rounded-lg bg-slate-800 hover:bg-slate-750 text-slate-400 hover:text-white border border-slate-700 transition"
                      title="Inspect portal page"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  )}

                  <Link
                    to={`/interview?jobId=${app.job_id}`}
                    className="px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-750 text-slate-300 text-xs font-semibold border border-slate-700 transition"
                  >
                    Mock Prep
                  </Link>

                  <button
                    onClick={() => handleDeleteApplication(app.id)}
                    className="p-2 rounded-lg bg-slate-800 hover:bg-rose-500/10 text-slate-500 hover:text-rose-400 border border-slate-700 transition"
                    title="Delete"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Human Review Modal */}
      <HumanReviewModal
        isOpen={reviewModalOpen}
        onClose={() => {
          setReviewModalOpen(false);
          setActiveAppForReview(null);
        }}
        application={activeAppForReview}
        onConfirmSubmission={handleConfirmSubmission}
        isConfirming={confirming}
      />
    </div>
  );
};
