import React from 'react';
import { Link } from 'react-router-dom';
import { Cpu, Search, GraduationCap, FileCheck, ShieldAlert, MessageSquareCode, ArrowRight } from 'lucide-react';

export const MultiAgentFlow = ({ activeStage = 'overview' }) => {
  const agents = [
    {
      id: 'assessment',
      name: 'Assessment Agent',
      icon: Cpu,
      path: '/assessment',
      desc: 'Resume NLP + GitHub/LeetCode',
      highlight: activeStage === 'assessment',
    },
    {
      id: 'jobs',
      name: 'Job Matching',
      icon: Search,
      path: '/jobs',
      desc: 'Semantic Vector Benchmarking',
      highlight: activeStage === 'jobs',
    },
    {
      id: 'learning',
      name: 'Gap & Learning',
      icon: GraduationCap,
      path: '/learning',
      desc: 'Market-Frequency Upskilling',
      highlight: activeStage === 'learning',
    },
    {
      id: 'tailoring',
      name: 'Tailoring Agent',
      icon: FileCheck,
      path: '/tailoring',
      desc: 'CAR/STAR Bullets + Letter',
      highlight: activeStage === 'tailoring',
    },
    {
      id: 'application',
      name: 'Application Agent',
      icon: ShieldAlert,
      path: '/applications',
      desc: 'Browser Staging & HITL Gate',
      highlight: activeStage === 'application',
      hitl: true,
    },
    {
      id: 'interview',
      name: 'Interview Prep',
      icon: MessageSquareCode,
      path: '/interview',
      desc: 'JD-Specific Mock Q&A',
      highlight: activeStage === 'interview',
    },
  ];

  return (
    <div className="bg-slate-800/40 border border-slate-800 rounded-2xl p-4 sm:p-6 mb-6 sm:mb-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5">
        <div>
          <h3 className="text-base sm:text-lg font-bold text-white tracking-wide uppercase flex items-center space-x-2">
            <span className="w-2.5 h-2.5 rounded-full bg-brand-400"></span>
            <span>Orchestrated Multi-Agent Execution Graph</span>
          </h3>
          <p className="text-xs sm:text-sm text-slate-300 mt-1">
            Autonomous specialized agents passing structured state down the recruitment lifecycle
          </p>
        </div>
        <span className="self-start sm:self-auto text-xs font-mono font-semibold text-slate-300 bg-slate-850 px-3 py-1.5 rounded-lg border border-slate-700">
          LangGraph Workflow
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3.5 relative">
        {agents.map((agent, idx) => {
          const Icon = agent.icon;
          return (
            <Link
              key={agent.id}
              to={agent.path}
              className={`p-4 rounded-xl border transition group relative flex flex-col justify-between ${
                agent.highlight
                  ? 'bg-brand-600/20 border-brand-500/60 shadow-lg shadow-brand-500/10 ring-1 ring-brand-500/50'
                  : agent.hitl
                  ? 'bg-amber-500/5 border-amber-500/30 hover:border-amber-500/60'
                  : 'bg-slate-850/80 border-slate-750 hover:border-slate-600 hover:bg-slate-800'
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div
                    className={`w-9 h-9 sm:w-10 sm:h-10 rounded-xl flex items-center justify-center ${
                      agent.hitl
                        ? 'bg-amber-500/20 text-amber-400'
                        : 'bg-brand-500/20 text-brand-400'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className="text-xs font-mono text-slate-400 font-bold">0{idx + 1}</span>
                </div>
                <div className="text-sm sm:text-base font-bold text-white group-hover:text-brand-300 transition">
                  {agent.name}
                </div>
                <div className="text-xs sm:text-sm text-slate-300 mt-1.5 leading-relaxed">{agent.desc}</div>
              </div>

              {agent.hitl && (
                <div className="mt-3.5 pt-2 border-t border-amber-500/20 flex items-center justify-between text-xs text-amber-400 font-bold">
                  <span>HUMAN APPROVAL GATE</span>
                  <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping"></span>
                </div>
              )}
            </Link>
          );
        })}
      </div>
    </div>
  );
};

