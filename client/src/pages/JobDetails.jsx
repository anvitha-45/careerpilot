import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import api from '../api/client';
import { MatchScoreGauge } from '../components/MatchScoreGauge';
import { SkillBadge } from '../components/SkillBadge';
import {
  Building,
  MapPin,
  Briefcase,
  ExternalLink,
  Sparkles,
  Send,
  FileCheck,
  ChevronLeft,
  ShieldCheck,
  AlertCircle
} from 'lucide-react';

export const JobDetails = () => {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDetail();
  }, [jobId]);

  const fetchDetail = async () => {
    try {
      const res = await api.get(`/jobs/${jobId}`);
      setData(res.data);
    } catch (err) {
      console.error('Failed to fetch job detail:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-500"></div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="p-8 text-center text-slate-400">
        Job description not found.
      </div>
    );
  }

  const job = data.job;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <button
        onClick={() => navigate(-1)}
        className="inline-flex items-center space-x-1.5 text-xs font-semibold text-slate-400 hover:text-white transition"
      >
        <ChevronLeft className="w-4 h-4" />
        <span>Back to Jobs</span>
      </button>

      {/* Main Header Box */}
      <div className="p-8 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="space-y-3 flex-1">
          <div className="flex items-center space-x-3">
            <h1 className="text-2xl font-extrabold text-white tracking-tight">{job.title}</h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-slate-300 font-medium">
              {job.portal}
            </span>
          </div>

          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-slate-400">
            <span className="font-semibold text-slate-200 flex items-center space-x-1">
              <Building className="w-4 h-4 text-slate-500" />
              <span>{job.company}</span>
            </span>
            <span>•</span>
            <span className="flex items-center space-x-1">
              <MapPin className="w-4 h-4 text-slate-500" />
              <span>{job.location}</span>
            </span>
            <span>•</span>
            <span className="text-emerald-400 font-semibold">{job.salary_range}</span>
            <span>•</span>
            <span>{job.work_mode}</span>
          </div>
        </div>

        <div className="flex items-center space-x-4 shrink-0">
          <MatchScoreGauge score={data.match_score} size="lg" />
        </div>
      </div>

      {/* Score Breakdown Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-center">
          <span className="text-[11px] font-semibold text-slate-400 uppercase">Skill Overlap</span>
          <div className="text-lg font-bold text-brand-400 mt-1">{data.skills_score} / 60</div>
        </div>
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-center">
          <span className="text-[11px] font-semibold text-slate-400 uppercase">Role Relevance</span>
          <div className="text-lg font-bold text-indigo-400 mt-1">{data.role_relevance_score} / 20</div>
        </div>
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-center">
          <span className="text-[11px] font-semibold text-slate-400 uppercase">Project Evidence</span>
          <div className="text-lg font-bold text-emerald-400 mt-1">{data.project_evidence_score} / 10</div>
        </div>
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-center">
          <span className="text-[11px] font-semibold text-slate-400 uppercase">Location Match</span>
          <div className="text-lg font-bold text-amber-400 mt-1">{data.location_score} / 10</div>
        </div>
      </div>

      {/* Explainability Callout */}
      <div className="p-4 rounded-xl bg-brand-950/40 border border-brand-800/40 text-xs text-brand-300 flex items-start space-x-3 leading-relaxed">
        <Sparkles className="w-5 h-5 text-brand-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-bold text-white">Semantic Match Assessment:</span>
          <p className="mt-0.5 text-slate-300">{data.explanation}</p>
        </div>
      </div>

      {/* Skills Matrix */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
          <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center space-x-1.5">
            <span>Verified Skills You Possess ({data.matched_skills.length})</span>
          </h4>
          <div className="flex flex-wrap gap-2">
            {data.matched_skills.map((s) => (
              <SkillBadge key={s} name={s} type="matched" />
            ))}
          </div>
        </div>

        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
          <h4 className="text-xs font-bold text-rose-400 uppercase tracking-wider flex items-center space-x-1.5">
            <AlertCircle className="w-4 h-4" />
            <span>Missing Skills To Address ({data.missing_skills.length})</span>
          </h4>
          <div className="flex flex-wrap gap-2">
            {data.missing_skills.map((s) => (
              <SkillBadge key={s} name={s} type="missing" priority="CRITICAL" />
            ))}
          </div>
        </div>
      </div>

      {/* Full Description */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider">
          Complete Job Description
        </h3>
        <div className="text-xs text-slate-300 leading-relaxed whitespace-pre-line bg-slate-950 p-4 rounded-xl border border-slate-850">
          {job.description}
        </div>
      </div>

      {/* Action Bar */}
      <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
        {job.apply_url && (
          <a
            href={job.apply_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center space-x-2 text-xs text-slate-400 hover:text-white transition"
          >
            <span>Direct Portal URL</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        )}

        <div className="flex items-center space-x-3 w-full sm:w-auto">
          <Link
            to={`/interview?jobId=${job.id}`}
            className="flex-1 sm:flex-none px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-750 text-slate-200 text-xs font-semibold border border-slate-700 transition text-center"
          >
            Practice Mock Interview
          </Link>
          <Link
            to={`/tailoring?jobId=${job.id}`}
            className="flex-1 sm:flex-none px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold shadow-lg shadow-brand-500/20 transition text-center flex items-center justify-center space-x-2"
          >
            <FileCheck className="w-4 h-4" />
            <span>Tailor Resume for this Job</span>
          </Link>
        </div>
      </div>
    </div>
  );
};

