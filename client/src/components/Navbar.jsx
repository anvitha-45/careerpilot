import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTour } from '../context/TourContext';
import { Compass, LogOut, ShieldCheck, HelpCircle, Menu } from 'lucide-react';

export const Navbar = ({ onToggleSidebar }) => {
  const { user, profile, logout } = useAuth();
  const { restartTour } = useTour();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="bg-slate-900/80 backdrop-blur border-b border-slate-800 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Left: Mobile Toggle & Logo */}
        <div className="flex items-center space-x-2 sm:space-x-3">
          {user && (
            <button
              onClick={onToggleSidebar}
              className="lg:hidden p-2 rounded-xl bg-slate-800 hover:bg-slate-750 text-slate-300 hover:text-white border border-slate-700 transition"
              aria-label="Toggle navigation menu"
            >
              <Menu className="w-5 h-5" />
            </button>
          )}

          <Link to="/" className="flex items-center space-x-2.5 sm:space-x-3 group min-w-0">
            <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-brand-500/20 group-hover:scale-105 transition-transform shrink-0">
              <Compass className="w-5 h-5 sm:w-6 sm:h-6 text-white animate-pulse" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center space-x-2">
                <span className="font-extrabold text-base sm:text-lg text-white tracking-tight truncate">CareerPilot</span>
                <span className="hidden sm:inline-block text-xs uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-brand-500/20 text-brand-300 border border-brand-500/30 shrink-0">
                  AI Copilot
                </span>
              </div>
              <p className="text-xs text-slate-400 font-medium hidden md:block">Job-Readiness & Staged Automation</p>
            </div>
          </Link>
        </div>

        {/* Status Badges, App Tour & User Info */}
        <div className="flex items-center space-x-2 sm:space-x-3 shrink-0">
          <button
            onClick={restartTour}
            className="hidden md:inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-brand-500/10 hover:bg-brand-500/20 border border-brand-500/30 text-brand-300 text-xs font-semibold transition hover:scale-105 active:scale-95"
            title="Open Interactive Product Tour"
          >
            <HelpCircle className="w-3.5 h-3.5 text-brand-400 shrink-0" />
            <span>Product Tour</span>
          </button>

          <div className="hidden lg:flex items-center space-x-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>HITL Responsible AI Enforced</span>
          </div>

          {user ? (
            <div className="flex items-center space-x-2 sm:space-x-3">
              <Link
                to="/profile"
                className="flex items-center space-x-2 px-2.5 sm:px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-750 border border-slate-700 text-slate-200 text-sm transition"
              >
                <div className="w-7 h-7 rounded-full bg-brand-600 flex items-center justify-center text-white text-xs font-bold shrink-0">
                  {user.name ? user.name[0].toUpperCase() : 'U'}
                </div>
                <span className="font-semibold hidden sm:inline">{user.name}</span>
                {profile?.overall_readiness_score && (
                  <span className="text-xs bg-slate-700 px-2 py-0.5 rounded-full text-brand-300 font-bold">
                    {profile.overall_readiness_score}%
                  </span>
                )}
              </Link>
              <button
                onClick={handleLogout}
                title="Sign out"
                className="p-2 sm:p-2 rounded-lg bg-slate-800 hover:bg-red-500/10 border border-slate-700 hover:border-red-500/30 text-slate-400 hover:text-red-400 transition"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="flex items-center space-x-1.5 sm:space-x-2">
              <Link
                to="/login"
                className="text-xs sm:text-sm px-3 sm:px-4 py-2 text-slate-300 hover:text-white transition font-medium"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                className="text-xs sm:text-sm px-3.5 sm:px-4 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white font-semibold shadow-md shadow-brand-500/20 transition"
              >
                Get Started
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
