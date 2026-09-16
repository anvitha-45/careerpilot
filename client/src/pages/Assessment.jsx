import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { MultiAgentFlow } from '../components/MultiAgentFlow';
import { MatchScoreGauge } from '../components/MatchScoreGauge';
import { SkillBadge } from '../components/SkillBadge';
import {
  Cpu,
  Github,
  Code2,
  RefreshCw,
  Award,
  Layers,
  CheckCircle2,
  Sparkles
} from 'lucide-react';

export const Assessment = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchAssessment();
  }, []);

  const fetchAssessment = async () => {
    try {
      const res = await api.get('/assessment');
      setData(res.data);
    } catch (err) {
      console.error('Failed to load assessment data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await api.post('/assessment/refresh');
      await fetchAssessment();
    } catch (err) {
      console.error('Failed to refresh assessment:', err);
    } finally {
      setRefreshing(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-500"></div>
      </div>
    );
  }

  const skillVector = data?.skill_vector || {};
  const github = data?.github_data || {};
  const leetcode = data?.leetcode_data || {};
  const benchmark = data?.market_benchmark || {};

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-bold text-white tracking-tight">Assessment Agent</h1>
            <span className="px-2 py-0.5 rounded bg-brand-500/20 text-brand-300 border border-brand-500/30 text-[10px] font-bold uppercase">
              Agent 01
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Empirical skill vectorization across multi-format resume NLP, GitHub repositories, and LeetCode metrics.
          </p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-750 text-slate-200 text-xs font-semibold border border-slate-700 transition self-start disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin text-brand-400' : ''}`} />
          <span>{refreshing ? 'Re-evaluating Vector...' : 'Refresh Assessment'}</span>
        </button>
      </div>

      <MultiAgentFlow activeStage="assessment" />

      {/* Top Banner: Overall Score & Market Benchmark */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 flex items-center space-x-6 shadow-sm">
          <MatchScoreGauge score={data?.readiness_score || 70} size="lg" />
          <div>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Empirical Readiness
            </span>
            <div className="text-lg font-bold text-white mt-1">
              {data?.readiness_score >= 75 ? 'Job Market Ready' : 'Competitive Track'}
            </div>
            <p className="text-xs text-emerald-400 font-medium mt-0.5">
              {benchmark.fresher_competitiveness_tier}
            </p>
          </div>
        </div>

        <div className="md:col-span-2 p-6 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col justify-between shadow-sm">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center space-x-1.5">
                <Award className="w-4 h-4 text-brand-400" />
                <span>Target Market Benchmark</span>
              </span>
              <span className="text-xs font-bold text-brand-400">
                {benchmark.market_alignment_percentage}% Alignment
              </span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              Based on empirical analysis of {benchmark.total_jobs_analyzed} active engineering job postings in {data?.target_location}.
            </p>
          </div>
          <div className="mt-4 p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300 flex items-center space-x-2">
            <Sparkles className="w-4 h-4 text-amber-400 shrink-0" />
            <span><strong>Agent Recommendation:</strong> {benchmark.recommended_focus}</span>
          </div>
        </div>
      </div>

      {/* Public Signals: GitHub & LeetCode */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* GitHub Card */}
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-lg bg-slate-800 text-white flex items-center justify-center">
                <Github className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">GitHub Public Signal</h3>
                <span className="text-xs text-slate-400">@{github.username || 'connected'}</span>
              </div>
            </div>
            <span className="text-xs font-bold text-slate-300 bg-slate-800 px-2.5 py-1 rounded-md border border-slate-700">
              {github.public_repos || 0} Repositories
            </span>
          </div>

          <div className="grid grid-cols-2 gap-3 pt-2">
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-[11px] text-slate-500 uppercase font-semibold">Total Stars</span>
              <div className="text-lg font-bold text-white mt-1">{github.stars_count || 0} ★</div>
            </div>
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-[11px] text-slate-500 uppercase font-semibold">Top Languages</span>
              <div className="text-xs font-bold text-brand-300 mt-1 truncate">
                {github.top_languages?.join(', ') || 'Python, JS'}
              </div>
            </div>
          </div>

          <p className="text-xs text-slate-400 leading-relaxed pt-1">
            {github.contributions_summary}
          </p>
        </div>

        {/* LeetCode Card */}
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-lg bg-amber-500/15 text-amber-400 flex items-center justify-center">
                <Code2 className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">LeetCode Problem Solving</h3>
                <span className="text-xs text-slate-400">@{leetcode.username || 'connected'}</span>
              </div>
            </div>
            <span className="text-xs font-bold text-amber-300 bg-amber-500/10 px-2.5 py-1 rounded-md border border-amber-500/20">
              {leetcode.total_solved || 0} Solved
            </span>
          </div>

          <div className="grid grid-cols-3 gap-2 pt-2">
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-center">
              <span className="text-[10px] text-emerald-400 uppercase font-bold">Easy</span>
              <div className="text-base font-bold text-white mt-0.5">{leetcode.easy_solved || 0}</div>
            </div>
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-center">
              <span className="text-[10px] text-amber-400 uppercase font-bold">Medium</span>
              <div className="text-base font-bold text-white mt-0.5">{leetcode.medium_solved || 0}</div>
            </div>
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-center">
              <span className="text-[10px] text-rose-400 uppercase font-bold">Hard</span>
              <div className="text-base font-bold text-white mt-0.5">{leetcode.hard_solved || 0}</div>
            </div>
          </div>

          <div className="flex items-center justify-between pt-1 text-xs text-slate-400">
            <span>Global Ranking: #{leetcode.ranking?.toLocaleString() || '140,000'}</span>
            <span className="text-emerald-400 font-medium">DSA Verified</span>
          </div>
        </div>
      </div>

      {/* Categorized Skill Vector Breakdown */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center space-x-2">
              <Layers className="w-4 h-4 text-brand-400" />
              <span>Multi-Dimensional Skill Vector ({skillVector.total_skills_count || 0} Skills)</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Extracted from verified resume bullet points and public developer repositories
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Languages */}
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-850 space-y-2.5">
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Core Languages
            </h4>
            <div className="flex flex-wrap gap-2">
              {skillVector.core_languages?.map((s) => (
                <SkillBadge key={s} name={s} type="matched" />
              ))}
            </div>
          </div>

          {/* Frameworks */}
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-850 space-y-2.5">
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Frameworks & Libraries
            </h4>
            <div className="flex flex-wrap gap-2">
              {skillVector.frameworks?.map((s) => (
                <SkillBadge key={s} name={s} type="matched" />
              ))}
            </div>
          </div>

          {/* Databases */}
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-850 space-y-2.5">
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Databases & Storage
            </h4>
            <div className="flex flex-wrap gap-2">
              {skillVector.databases?.map((s) => (
                <SkillBadge key={s} name={s} type="matched" />
              ))}
            </div>
          </div>

          {/* DevOps & Tools */}
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-850 space-y-2.5">
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Tools, DevOps & Cloud
            </h4>
            <div className="flex flex-wrap gap-2">
              {skillVector.tools_devops?.map((s) => (
                <SkillBadge key={s} name={s} type="matched" />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

