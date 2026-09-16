import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTour } from '../context/TourContext';
import api from '../api/client';
import { MultiAgentFlow } from '../components/MultiAgentFlow';
import { MatchScoreGauge } from '../components/MatchScoreGauge';
import { SkillBadge } from '../components/SkillBadge';
import {
  TrendingUp,
  Briefcase,
  GraduationCap,
  Sparkles,
  ArrowUpRight,
  ShieldCheck,
  AlertCircle,
  FileText,
  Compass
} from 'lucide-react';

export const Dashboard = () => {
  const { user, profile } = useAuth();
  const { restartTour } = useTour();
  const [analytics, setAnalytics] = useState(null);
  const [topJobs, setTopJobs] = useState([]);
  const [gaps, setGaps] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [analyticsRes, jobsRes, gapsRes] = await Promise.all([
        api.get('/analytics/summary'),
        api.get('/jobs?min_score=60'),
        api.get('/learning/gaps')
      ]);
      setAnalytics(analyticsRes.data);
      setTopJobs(jobsRes.data.slice(0, 4));
      setGaps(gapsRes.data.gaps ? gapsRes.data.gaps.slice(0, 3) : []);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  const readinessScore = profile?.overall_readiness_score || analytics?.readiness_score || 68;

  return (
    <div className="space-y-8">
      {/* Top Welcome Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-slate-850 to-brand-950/40 border border-slate-800 p-4 sm:p-8 shadow-xl">
        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-5 sm:gap-6">
          <div className="max-w-2xl min-w-0">
            <div className="flex flex-wrap items-center gap-2 mb-3">
              <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/20 text-brand-300 text-xs font-semibold">
                <Sparkles className="w-3.5 h-3.5 text-brand-400 shrink-0" />
                <span>Agentic Career Copilot Active</span>
              </div>
              <button
                onClick={restartTour}
                className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-indigo-500/15 hover:bg-indigo-500/25 border border-indigo-500/30 text-indigo-300 text-xs font-semibold transition hover:scale-105 active:scale-95"
              >
                <Compass className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                <span>Take Product Tour (2 min)</span>
              </button>
            </div>
            <h1 className="text-xl sm:text-3xl font-extrabold text-white tracking-tight">
              Hello, {user?.name || 'Engineer'}!
            </h1>
            <p className="text-xs sm:text-sm text-slate-300 mt-2 leading-relaxed">
              Your autonomous 5-agent pipeline is active. Benchmarking candidate skill vectors against real Indian & global engineering job postings.
            </p>
          </div>

          {/* Overall Readiness Card */}
          <div className="flex items-center space-x-4 sm:space-x-5 bg-slate-900/90 border border-slate-750 p-3.5 sm:p-4 rounded-xl shadow-lg w-full sm:w-auto shrink-0">
            <MatchScoreGauge score={readinessScore} size="lg" />
            <div>
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Readiness Score
              </div>
              <div className="text-sm sm:text-base font-bold text-white mt-0.5">
                {readinessScore >= 75 ? 'Market Ready' : 'Competitive Track'}
              </div>
              <p className="text-[11px] text-brand-400 font-medium mt-0.5">
                Top 20% of 2026 Batch
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Multi-Agent Visual Execution Flow */}
      <MultiAgentFlow activeStage="overview" />

      {/* Quick Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase">Verified Skills</span>
            <div className="w-8 h-8 rounded-lg bg-brand-500/10 text-brand-400 flex items-center justify-center">
              <Sparkles className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-white mt-3">
            {profile?.skill_vector?.total_skills_count || 11}
          </div>
          <p className="text-xs text-slate-400 mt-1">Extracted via Resume NLP & GitHub</p>
        </div>

        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase">Target Postings</span>
            <div className="w-8 h-8 rounded-lg bg-indigo-500/10 text-indigo-400 flex items-center justify-center">
              <Briefcase className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-white mt-3">
            {topJobs.length > 0 ? `${topJobs.length}+ Active` : '6 Active'}
          </div>
          <p className="text-xs text-slate-400 mt-1">LinkedIn, Naukri, & ATS feeds</p>
        </div>

        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase">Market Gaps</span>
            <div className="w-8 h-8 rounded-lg bg-rose-500/10 text-rose-400 flex items-center justify-center">
              <AlertCircle className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-white mt-3">
            {gaps.length} Critical
          </div>
          <p className="text-xs text-slate-400 mt-1">Frequency-ranked from real JDs</p>
        </div>

        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase">Staged Applications</span>
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 text-amber-400 flex items-center justify-center">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-white mt-3">
            {analytics?.application_funnel?.READY_FOR_REVIEW || 0} Awaiting Review
          </div>
          <p className="text-xs text-amber-400/90 font-medium mt-1">Human Approval Gate active</p>
        </div>
      </div>

      {/* Two Column Layout: Top Matched Jobs & Market Upskilling Roadmap */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left 2 Cols: High Match Jobs */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-white tracking-tight">Top Matched Engineering Roles</h2>
              <p className="text-xs text-slate-400">Ranked by cosine vector similarity & required skill overlap</p>
            </div>
            <Link
              to="/jobs"
              className="inline-flex items-center space-x-1 text-xs font-semibold text-brand-400 hover:text-brand-300 transition"
            >
              <span>Explore All Jobs</span>
              <ArrowUpRight className="w-4 h-4" />
            </Link>
          </div>

          <div className="space-y-3">
            {topJobs.map((item) => (
              <div
                key={item.job.id}
                className="p-5 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
              >
                <div className="space-y-2 flex-1">
                  <div className="flex items-center space-x-3">
                    <span className="font-bold text-base text-white">{item.job.title}</span>
                    <span className="text-xs px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300">
                      {item.job.portal}
                    </span>
                  </div>
                  <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-400">
                    <span className="font-semibold text-slate-300">{item.job.company}</span>
                    <span>•</span>
                    <span>{item.job.location}</span>
                    <span>•</span>
                    <span className="text-emerald-400 font-medium">{item.job.salary_range}</span>
                  </div>
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {item.matched_skills.slice(0, 4).map((s) => (
                      <SkillBadge key={s} name={s} type="matched" />
                    ))}
                    {item.missing_skills.slice(0, 2).map((s) => (
                      <SkillBadge key={s} name={s} type="missing" priority="HIGH" />
                    ))}
                  </div>
                </div>

                <div className="flex sm:flex-col items-center sm:items-end justify-between w-full sm:w-auto gap-3 pt-3 sm:pt-0 border-t sm:border-t-0 border-slate-800">
                  <MatchScoreGauge score={item.match_score} size="sm" />
                  <div className="flex items-center space-x-2">
                    <Link
                      to={`/jobs/${item.job.id}`}
                      className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-750 text-slate-300 text-xs font-medium border border-slate-700 transition"
                    >
                      View JD
                    </Link>
                    <Link
                      to={`/tailoring?jobId=${item.job.id}`}
                      className="px-3 py-1.5 rounded-lg bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold shadow-md shadow-brand-500/20 transition"
                    >
                      Tailor
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Col: High-Yield Skill Gap Curation */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-white tracking-tight">Market Skill Gaps</h2>
              <p className="text-xs text-slate-400">Frequency across real active JDs</p>
            </div>
            <Link
              to="/learning"
              className="text-xs font-semibold text-brand-400 hover:text-brand-300"
            >
              View Plan
            </Link>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
            <p className="text-xs text-slate-300 leading-relaxed">
              These technologies appear most frequently across your shortlisted backend & fullstack roles:
            </p>

            <div className="space-y-3">
              {gaps.map((gap) => (
                <div
                  key={gap.skill}
                  className="p-3 rounded-lg bg-slate-950 border border-slate-800/80 space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-sm text-white">{gap.skill}</span>
                    <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-rose-500/15 border border-rose-500/30 text-rose-300">
                      {gap.frequency_percentage}% of Postings
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 leading-snug">
                    {gap.market_context}
                  </p>
                  <div className="flex items-center justify-between pt-1 text-[11px]">
                    <span className="text-slate-500">Est. Time: {gap.estimated_days}</span>
                    <span className="text-brand-400 font-medium">Free Resources (NPTEL/YT) →</span>
                  </div>
                </div>
              ))}
            </div>

            <Link
              to="/learning"
              className="w-full py-2 rounded-lg bg-slate-800 hover:bg-slate-750 text-slate-200 text-xs font-semibold border border-slate-700 flex items-center justify-center space-x-2 transition"
            >
              <GraduationCap className="w-4 h-4 text-brand-400" />
              <span>Open Personalized 4-Week Roadmap</span>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
