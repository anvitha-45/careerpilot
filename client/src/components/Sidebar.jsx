import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Cpu,
  Briefcase,
  GraduationCap,
  FileCheck,
  Send,
  MessageSquareCode,
  BarChart3,
  UserCheck,
  X
} from 'lucide-react';

const NAV_ITEMS = [
  { path: '/', label: 'Overview', icon: LayoutDashboard },
  { path: '/assessment', label: '1. Skill Assessment', icon: Cpu, badge: 'Agent' },
  { path: '/jobs', label: '2. Job Explorer', icon: Briefcase },
  { path: '/learning', label: '3. Market Upskilling', icon: GraduationCap, badge: 'Agent' },
  { path: '/tailoring', label: '4. Resume & Cover Letter', icon: FileCheck, badge: 'Agent' },
  { path: '/applications', label: '5. Application Staging', icon: Send, badge: 'HITL' },
  { path: '/interview', label: '6. Mock Interview', icon: MessageSquareCode, badge: 'Agent' },
  { path: '/analytics', label: 'Career Analytics', icon: BarChart3 },
  { path: '/profile', label: 'Candidate Profile', icon: UserCheck },
];

export const Sidebar = ({ isOpen, onClose }) => {
  const renderNavLinks = (isMobile = false) => (
    <nav className="space-y-1">
      {NAV_ITEMS.map((item) => {
        const Icon = item.icon;
        return (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/'}
            onClick={() => {
              if (isMobile && onClose) {
                onClose();
              }
            }}
            className={({ isActive }) =>
              `flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs sm:text-sm font-medium transition ${
                isActive
                  ? 'bg-brand-600/20 text-brand-300 border border-brand-500/40 shadow-sm font-semibold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`
            }
          >
            <div className="flex items-center space-x-3">
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.label}</span>
            </div>
            {item.badge && (
              <span
                className={`text-[10px] px-1.5 py-0.5 rounded font-bold uppercase ${
                  item.badge === 'HITL'
                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                    : 'bg-brand-500/20 text-brand-300 border border-brand-500/30'
                }`}
              >
                {item.badge}
              </span>
            )}
          </NavLink>
        );
      })}
    </nav>
  );

  const renderComplianceCard = () => (
    <div className="p-4 border-t border-slate-800">
      <div className="p-3 rounded-xl bg-slate-850/60 border border-slate-750/60">
        <div className="flex items-center space-x-2 text-xs font-semibold text-emerald-400 mb-1">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
          <span>Platform Safe</span>
        </div>
        <p className="text-[11px] text-slate-400 leading-relaxed">
          Stops at Human Review Checkpoint. Compliant with LinkedIn Section 8.2 & Naukri ToS.
        </p>
      </div>
    </div>
  );

  return (
    <>
      {/* Mobile Drawer (Off-Canvas overlay) */}
      {isOpen && (
        <div className="fixed inset-0 z-50 lg:hidden flex animate-in fade-in duration-200">
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black/75 backdrop-blur-sm"
            onClick={onClose}
            aria-hidden="true"
          />

          {/* Drawer Content */}
          <div className="relative w-72 max-w-[85vw] bg-slate-900 border-r border-slate-800 h-full flex flex-col shadow-2xl z-10 animate-in slide-in-from-left duration-200">
            <div className="p-4 border-b border-slate-800 flex items-center justify-between">
              <div className="text-xs uppercase tracking-wider font-bold text-white flex items-center space-x-2">
                <span className="w-2 h-2 rounded-full bg-brand-400"></span>
                <span>Multi-Agent Pipeline</span>
              </div>
              <button
                type="button"
                onClick={onClose}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition cursor-pointer"
                aria-label="Close menu"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-4 flex-1 overflow-y-auto">
              {renderNavLinks(true)}
            </div>

            {renderComplianceCard()}
          </div>
        </div>
      )}

      {/* Desktop Persistent Sidebar */}
      <aside className="w-64 bg-slate-900 border-r border-slate-800 hidden lg:flex flex-col shrink-0 min-h-[calc(100vh-4rem)]">
        <div className="p-4 flex-1 overflow-y-auto">
          <div className="text-[11px] uppercase tracking-wider font-semibold text-slate-500 mb-3 px-3">
            Multi-Agent Pipeline
          </div>
          {renderNavLinks(false)}
        </div>
        {renderComplianceCard()}
      </aside>
    </>
  );
};

