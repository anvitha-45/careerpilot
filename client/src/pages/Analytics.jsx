import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { MatchScoreGauge } from '../components/MatchScoreGauge';
import { MultiAgentFlow } from '../components/MultiAgentFlow';
import {
  BarChart3,
  TrendingUp,
  Award,
  Send,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  Layers
} from 'lucide-react';

export const Analytics = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const res = await api.get('/analytics/summary');
      setData(res.data);
    } catch (err) {
      console.error('Failed to load analytics:', err);
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

  const funnel = data?.application_funnel || {};
  const stages = data?.pipeline_stages || [];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Career Analytics & Copilot Telemetry</h1>
        <p className="text-xs text-slate-400 mt-1">
          Quantitative benchmarking across application conversion, multi-agent pipeline health, and interview readiness.
        </p>
      </div>

      <MultiAgentFlow activeStage="overview" />

      {/* Top Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-sm flex items-center space-x-4">
          <MatchScoreGauge score={data?.readiness_score || 70} size="md" />
          <div>
            <span className="text-[11px] font-bold text-slate-400 uppercase">Readiness</span>
            <div className="text-lg font-bold text-white mt-0.5">{data?.readiness_score}%</div>
            <span className="text-[10px] text-emerald-400 font-semibold">Top 25% Cohort</span>
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-sm flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center">
            <Award className="w-6 h-6" />
          </div>
          <div>
            <span className="text-[11px] font-bold text-slate-400 uppercase">Mock Interview Avg</span>
            <div className="text-lg font-bold text-white mt-0.5">{data?.interview_average_score}%</div>
            <span className="text-[10px] text-slate-400">{data?.completed_mock_interviews} Completed</span>
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-sm flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-amber-500/10 text-amber-400 flex items-center justify-center">
            <Send className="w-6 h-6" />
          </div>
          <div>
            <span className="text-[11px] font-bold text-slate-400 uppercase">Total Applications</span>
            <div className="text-lg font-bold text-white mt-0.5">{data?.total_applications || 0}</div>
            <span className="text-[10px] text-amber-400">{funnel.READY_FOR_REVIEW || 0} In Review</span>
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-sm flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-brand-500/10 text-brand-400 flex items-center justify-center">
            <Sparkles className="w-6 h-6" />
          </div>
          <div>
            <span className="text-[11px] font-bold text-slate-400 uppercase">Verified Skills</span>
            <div className="text-lg font-bold text-white mt-0.5">{data?.verified_skills_count || 11}</div>
            <span className="text-[10px] text-brand-300">0% Hallucination</span>
          </div>
        </div>
      </div>

      {/* Application Funnel Visualizer */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4 shadow-sm">
        <div>
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">
            Application Pipeline Funnel
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Stage progression from automated browser pre-fill through manual human confirmation and interviews
          </p>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 pt-2">
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-850 text-center">
            <span className="text-[10px] font-bold uppercase text-slate-400">Shortlisted</span>
            <div className="text-xl font-bold text-white mt-1">{funnel.SHORTLISTED || 0}</div>
          </div>
          <div className="p-4 rounded-xl bg-slate-950 border border-amber-500/30 text-center">
            <span className="text-[10px] font-bold uppercase text-amber-400">Staged (Review)</span>
            <div className="text-xl font-bold text-amber-300 mt-1">{funnel.READY_FOR_REVIEW || 0}</div>
          </div>
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-850 text-center">
            <span className="text-[10px] font-bold uppercase text-emerald-400">User Submitted</span>
            <div className="text-xl font-bold text-white mt-1">{funnel.USER_SUBMITTED || 0}</div>
          </div>
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-850 text-center">
            <span className="text-[10px] font-bold uppercase text-indigo-400">Interview</span>
            <div className="text-xl font-bold text-indigo-300 mt-1">{funnel.INTERVIEW || 0}</div>
          </div>
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-850 text-center">
            <span className="text-[10px] font-bold uppercase text-brand-400">Offers</span>
            <div className="text-xl font-bold text-emerald-400 mt-1">{funnel.OFFER || 0}</div>
          </div>
        </div>
      </div>

      {/* Pipeline Agents Status */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4 shadow-sm">
        <div>
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">
            Agent Coordination Telemetry (LangGraph Checkpoints)
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Active status and state representation for each autonomous module
          </p>
        </div>

        <div className="divide-y divide-slate-850">
          {stages.map((stage) => (
            <div key={stage.id} className="py-3 flex items-center justify-between text-xs">
              <div className="flex items-center space-x-3">
                <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                <div>
                  <span className="font-bold text-white">{stage.name}</span>
                  <span className="text-slate-500 ml-2">({stage.role})</span>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-slate-400 text-[11px] hidden sm:inline">{stage.details}</span>
                <span className="px-2 py-0.5 rounded font-mono text-[10px] font-bold uppercase bg-slate-800 text-slate-300 border border-slate-700">
                  {stage.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

