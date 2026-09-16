import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { MultiAgentFlow } from '../components/MultiAgentFlow';
import { ResourceCard } from '../components/ResourceCard';
import {
  GraduationCap,
  Calendar,
  Layers,
  Sparkles,
  CheckCircle2,
  Clock,
  BookOpen,
  ArrowRight
} from 'lucide-react';

export const LearningPlan = () => {
  const [gapsData, setGapsData] = useState(null);
  const [activeTab, setActiveTab] = useState('gaps'); // 'gaps' | 'roadmap'
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLearningData();
  }, []);

  const fetchLearningData = async () => {
    try {
      const res = await api.get('/learning/gaps');
      setGapsData(res.data);
    } catch (err) {
      console.error('Failed to load learning data:', err);
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

  const gaps = gapsData?.gaps || [];
  const weeks = gapsData?.weeks || [];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-2">
          <h1 className="text-2xl font-bold text-white tracking-tight">Market-Driven Upskilling Agent</h1>
          <span className="px-2 py-0.5 rounded bg-brand-500/20 text-brand-300 border border-brand-500/30 text-[10px] font-bold uppercase">
            Agent 03
          </span>
        </div>
        <p className="text-xs text-slate-400 mt-1">
          Missing skills ranked strictly by empirical frequency across real target job postings. Zero generic lists.
        </p>
      </div>

      <MultiAgentFlow activeStage="learning" />

      {/* Tabs */}
      <div className="flex items-center space-x-2 border-b border-slate-800 pb-3">
        <button
          onClick={() => setActiveTab('gaps')}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${
            activeTab === 'gaps'
              ? 'bg-brand-600 text-white shadow-md shadow-brand-500/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          Frequency-Ranked Market Gaps ({gaps.length})
        </button>
        <button
          onClick={() => setActiveTab('roadmap')}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${
            activeTab === 'roadmap'
              ? 'bg-brand-600 text-white shadow-md shadow-brand-500/20'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          Personalized 4-Week Study Roadmap
        </button>
      </div>

      {activeTab === 'gaps' ? (
        <div className="space-y-6">
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300 flex items-start space-x-3 leading-relaxed">
            <Sparkles className="w-4 h-4 text-brand-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-bold text-white">Empirical Market Philosophy:</span>
              <p className="mt-0.5 text-slate-400">
                Priorities are computed directly from real job descriptions in your region. Critical gaps appear in over 50% of verified postings. Each gap is paired with free academic courses (NPTEL) and practical developer playlists.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {gaps.map((gap) => (
              <div
                key={gap.skill}
                className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4 shadow-sm flex flex-col justify-between"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="text-base font-bold text-white">{gap.skill}</h3>
                    <span
                      className={`text-[10px] uppercase font-bold px-2.5 py-1 rounded-full border ${
                        gap.priority === 'CRITICAL'
                          ? 'bg-rose-500/15 border-rose-500/30 text-rose-300'
                          : 'bg-amber-500/15 border-amber-500/30 text-amber-300'
                      }`}
                    >
                      {gap.priority} GAP • {gap.frequency_percentage}% OF JDS
                    </span>
                  </div>

                  <p className="text-xs text-slate-400 leading-relaxed">
                    {gap.market_context}
                  </p>

                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-850 text-xs space-y-1">
                    <span className="text-[10px] uppercase font-bold text-slate-500">Recommended Action</span>
                    <p className="text-slate-200 font-medium">{gap.suggested_action}</p>
                    <span className="text-[11px] text-brand-400 block pt-1">
                      Estimated Completion: {gap.estimated_days}
                    </span>
                  </div>
                </div>

                {/* Free Resources List */}
                <div className="space-y-2 pt-3 border-t border-slate-800/80">
                  <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">
                    Curated Free Learning Resources (NPTEL / YouTube / Docs)
                  </span>
                  <div className="grid grid-cols-1 gap-2">
                    {gap.resources?.map((res, rIdx) => (
                      <ResourceCard key={rIdx} resource={res} />
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        /* 4-Week Study Roadmap Tab */
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {weeks.map((week) => (
              <div
                key={week.week_number}
                className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4 shadow-sm"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 rounded-xl bg-brand-500/10 text-brand-400 flex items-center justify-center font-bold text-xs">
                      W{week.week_number}
                    </div>
                    <div>
                      <h3 className="text-sm font-bold text-white">{week.focus_topic}</h3>
                      <span className="text-[11px] text-slate-400">
                        Target Skills: {week.skills?.join(', ')}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="space-y-2 pt-2">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                    Key Deliverables
                  </span>
                  <ul className="space-y-2">
                    {week.tasks?.map((task, tIdx) => (
                      <li key={tIdx} className="flex items-start space-x-2 text-xs text-slate-300">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                        <span>{task}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {week.resources && week.resources.length > 0 && (
                  <div className="pt-3 border-t border-slate-800 space-y-2">
                    <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">
                      Assigned Resource
                    </span>
                    <ResourceCard resource={week.resources[0]} />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

