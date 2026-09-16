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
    <div className="bg-slate-800/40 border border-slate-800 rounded-2xl p-5 mb-8">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold text-white tracking-wide uppercase flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-brand-400"></span>
            <span>Orchestrated Multi-Agent Execution Graph</span>
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Autonomous specialized agents passing structured state down the recruitment lifecycle
          </p>
        </div>
        <span className="text-[11px] font-mono text-slate-400 bg-slate-850 px-2.5 py-1 rounded-md border border-slate-700">
          LangGraph Workflow
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-6 gap-3 relative">
        {agents.map((agent, idx) => {
          const Icon = agent.icon;
          return (
            <Link
              key={agent.id}
              to={agent.path}
              className={`p-3.5 rounded-xl border transition group relative flex flex-col justify-between ${
                agent.highlight
                  ? 'bg-brand-600/20 border-brand-500/60 shadow-lg shadow-brand-500/10 ring-1 ring-brand-500/50'
                  : agent.hitl
                  ? 'bg-amber-500/5 border-amber-500/30 hover:border-amber-500/60'
                  : 'bg-slate-850/80 border-slate-750 hover:border-slate-600 hover:bg-slate-800'
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div
                    className={`w-7 h-7 rounded-lg flex items-center justify-center ${
                      agent.hitl
                        ? 'bg-amber-500/20 text-amber-400'
                        : 'bg-brand-500/20 text-brand-400'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                  </div>
                  <span className="text-[10px] font-mono text-slate-500 font-bold">0{idx + 1}</span>
                </div>
                <div className="text-xs font-semibold text-white group-hover:text-brand-300 transition">
                  {agent.name}
                </div>
                <div className="text-[11px] text-slate-400 mt-1 leading-snug">{agent.desc}</div>
              </div>

              {agent.hitl && (
                <div className="mt-3 pt-2 border-t border-amber-500/20 flex items-center justify-between text-[10px] text-amber-400 font-semibold">
                  <span>HUMAN APPROVAL GATE</span>
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-ping"></span>
                </div>
              )}
            </Link>
          );
        })}
      </div>
    </div>
  );
};

