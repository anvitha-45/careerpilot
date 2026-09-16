import React from 'react';
import { Link } from 'react-router-dom';
import { Compass, ArrowRight, Sparkles, CheckCircle2, ChevronRight } from 'lucide-react';

export const NextStepBanner = ({
  stepNumber,
  totalSteps = 7,
  badgeText = "Next Recommended Action",
  title = "What's My Next Step?",
  description,
  primaryLabel,
  primaryPath,
  secondaryLabel,
  secondaryPath
}) => {
  return (
    <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-slate-850 to-brand-950/40 border border-slate-750 p-5 sm:p-6 shadow-xl animate-in fade-in slide-in-from-bottom-2 duration-300">
      {/* Ambient background glow */}
      <div className="absolute top-0 right-0 -mr-12 -mt-12 w-36 h-36 bg-brand-500/10 rounded-full blur-2xl pointer-events-none" />

      <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-5">
        {/* Left Info & Guidance */}
        <div className="flex items-start space-x-4 max-w-2xl">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-brand-500/20 shrink-0 mt-0.5">
            <Compass className="w-5 h-5 animate-pulse" />
          </div>

          <div className="space-y-1">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-[10px] font-bold font-mono uppercase tracking-wider px-2 py-0.5 rounded bg-brand-500/15 border border-brand-500/30 text-brand-300">
                {stepNumber ? `Step ${stepNumber} of ${totalSteps}` : 'Guided Journey'}
              </span>
              <span className="text-xs text-slate-400 flex items-center space-x-1">
                <Sparkles className="w-3 h-3 text-brand-400" />
                <span className="font-semibold text-slate-300">{badgeText}</span>
              </span>
            </div>

            <h3 className="text-base sm:text-lg font-bold text-white tracking-tight">
              {title}
            </h3>
            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
              {description}
            </p>
          </div>
        </div>

        {/* Right Navigation Actions */}
        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto self-end md:self-center shrink-0">
          {secondaryLabel && secondaryPath && (
            <Link
              to={secondaryPath}
              className="flex-1 sm:flex-initial inline-flex items-center justify-center space-x-1.5 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-750 text-slate-300 hover:text-white border border-slate-700 text-xs font-semibold transition"
            >
              <span>{secondaryLabel}</span>
            </Link>
          )}

          {primaryLabel && primaryPath && (
            <Link
              to={primaryPath}
              className="flex-1 sm:flex-initial inline-flex items-center justify-center space-x-2 px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-bold shadow-lg shadow-brand-500/25 hover:shadow-brand-500/40 transition hover:scale-105 active:scale-95"
            >
              <span>{primaryLabel}</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          )}
        </div>
      </div>
    </div>
  );
};
