import React from 'react';
import { useLocation } from 'react-router-dom';
import { useTour } from '../context/TourContext';
import {
  Compass,
  Sparkles,
  Cpu,
  GraduationCap,
  FileCheck,
  ShieldCheck,
  MessageSquareCode,
  ArrowRight,
  X
} from 'lucide-react';

export const ProductTourOfferModal = () => {
  const { isOfferOpen, startTour, dismissOffer } = useTour();
  const location = useLocation();

  if (!isOfferOpen || location.pathname === '/register') return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-3 sm:p-4 overflow-y-auto animate-in fade-in duration-300">
      <div className="bg-slate-900 border border-slate-750 rounded-2xl sm:rounded-3xl max-w-xl w-full shadow-2xl overflow-hidden relative my-auto max-h-[92vh] flex flex-col animate-in zoom-in-95 duration-200">
        {/* Glow ambient effect */}
        <div className="absolute top-0 right-0 -mr-16 -mt-16 w-48 h-48 bg-brand-500/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 -ml-16 -mb-16 w-48 h-48 bg-indigo-500/20 rounded-full blur-3xl pointer-events-none" />

        {/* Close Button */}
        <button
          onClick={dismissOffer}
          className="absolute top-4 right-4 p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-850 transition z-10"
          aria-label="Dismiss tour"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Header */}
        <div className="p-5 sm:p-8 pb-3 sm:pb-4 relative z-10 shrink-0">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/20 text-brand-300 text-xs font-semibold mb-3">
            <Sparkles className="w-3.5 h-3.5 text-brand-400" />
            <span>Welcome to CareerPilot AI</span>
          </div>

          <div className="flex items-start space-x-4">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-brand-600 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-brand-500/20 shrink-0">
              <Compass className="w-7 h-7" />
            </div>
            <div>
              <h2 className="text-xl sm:text-2xl font-extrabold text-white tracking-tight">
                Would you like a quick product tour?
              </h2>
              <p className="text-xs sm:text-sm text-slate-300 mt-1 leading-relaxed">
                Take a 2-minute interactive walkthrough to see how our orchestrated multi-agent copilot prepares graduating engineers for placement success.
              </p>
            </div>
          </div>
        </div>

        {/* Agent Capabilities Preview Grid */}
        <div className="px-5 sm:px-8 py-3 space-y-2.5 relative z-10 overflow-y-auto flex-1">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
            What You'll Discover in the Tour:
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 flex items-center space-x-3">
              <div className="w-9 h-9 rounded-lg bg-purple-500/10 text-purple-400 flex items-center justify-center shrink-0">
                <Cpu className="w-4.5 h-4.5" />
              </div>
              <div className="text-xs sm:text-sm">
                <div className="font-semibold text-white">Assessment Agent</div>
                <div className="text-slate-400 text-xs">Resume NLP & GitHub stats</div>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 flex items-center space-x-3">
              <div className="w-9 h-9 rounded-lg bg-amber-500/10 text-amber-400 flex items-center justify-center shrink-0">
                <GraduationCap className="w-4.5 h-4.5" />
              </div>
              <div className="text-xs sm:text-sm">
                <div className="font-semibold text-white">Market Upskilling</div>
                <div className="text-slate-400 text-xs">Free NPTEL & YouTube links</div>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 flex items-center space-x-3">
              <div className="w-9 h-9 rounded-lg bg-blue-500/10 text-blue-400 flex items-center justify-center shrink-0">
                <FileCheck className="w-4.5 h-4.5" />
              </div>
              <div className="text-xs sm:text-sm">
                <div className="font-semibold text-white">Tailoring Agent</div>
                <div className="text-slate-400 text-xs">STAR bullets + zero hallucinations</div>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 flex items-center space-x-3">
              <div className="w-9 h-9 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center shrink-0">
                <ShieldCheck className="w-4.5 h-4.5" />
              </div>
              <div className="text-xs sm:text-sm">
                <div className="font-semibold text-white">Ethical Automation</div>
                <div className="text-slate-400 text-xs">Human-in-the-Loop review gate</div>
              </div>
            </div>
          </div>
        </div>

        {/* Modal Action Buttons */}
        <div className="p-5 sm:p-8 pt-4 sm:pt-5 bg-slate-950/70 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3 relative z-10 shrink-0">
          <button
            onClick={dismissOffer}
            className="w-full sm:w-auto px-4 py-3 sm:py-2.5 rounded-xl text-xs sm:text-sm font-semibold text-slate-400 hover:text-slate-200 hover:bg-slate-850 transition order-2 sm:order-1 text-center cursor-pointer"
          >
            I'll Explore on My Own
          </button>

          <button
            onClick={startTour}
            className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 px-6 py-3 sm:py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs sm:text-sm font-bold shadow-lg shadow-brand-500/25 hover:shadow-brand-500/40 transition order-1 sm:order-2 cursor-pointer"
          >
            <span>Start Product Tour (2 min)</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

