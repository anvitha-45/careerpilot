import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Compass, LogOut, User, ShieldCheck, Sparkles, HelpCircle } from 'lucide-react';
import { AppTourModal } from './AppTourModal';

export const Navbar = () => {
  const { user, profile, logout } = useAuth();
  const [isTourOpen, setIsTourOpen] = useState(false);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <>
      <header className="bg-slate-900/80 backdrop-blur border-b border-slate-800 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-brand-500/20 group-hover:scale-105 transition-transform">
              <Compass className="w-6 h-6 text-white animate-pulse" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg text-white tracking-tight">CareerPilot</span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-brand-500/20 text-brand-300 border border-brand-500/30">
                  AI Copilot
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-medium">Job-Readiness & Staged Automation</p>
            </div>
          </Link>

          {/* Status Badges, App Tour & User Info */}
          <div className="flex items-center space-x-3 sm:space-x-4">
            <button
              onClick={() => setIsTourOpen(true)}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-brand-500/10 hover:bg-brand-500/20 border border-brand-500/30 text-brand-300 text-xs font-semibold transition"
            >
              <HelpCircle className="w-3.5 h-3.5 text-brand-400" />
              <span>App Tour</span>
            </button>

            <div className="hidden lg:flex items-center space-x-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>HITL Responsible AI Enforced</span>
            </div>

            {user ? (
              <div className="flex items-center space-x-3">
                <Link
                  to="/profile"
                  className="flex items-center space-x-2.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-750 border border-slate-700 text-slate-200 text-sm transition"
                >
                  <div className="w-6 h-6 rounded-full bg-brand-600 flex items-center justify-center text-white text-xs font-bold">
                    {user.name ? user.name[0].toUpperCase() : 'U'}
                  </div>
                  <span className="font-medium hidden sm:inline">{user.name}</span>
                  {profile?.overall_readiness_score && (
                    <span className="text-xs bg-slate-700 px-2 py-0.5 rounded-full text-brand-300 font-semibold">
                      {profile.overall_readiness_score}%
                    </span>
                  )}
                </Link>
                <button
                  onClick={handleLogout}
                  title="Sign out"
                  className="p-2 rounded-lg bg-slate-800 hover:bg-red-500/10 border border-slate-700 hover:border-red-500/30 text-slate-400 hover:text-red-400 transition"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Link
                  to="/login"
                  className="text-sm px-4 py-2 text-slate-300 hover:text-white transition"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="text-sm px-4 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white font-medium shadow-md shadow-brand-500/20 transition"
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* App Tour Modal */}
      <AppTourModal isOpen={isTourOpen} onClose={() => setIsTourOpen(false)} />
    </>
  );
};

