import React from 'react';

export const MatchScoreGauge = ({ score = 0, size = 'md' }) => {
  const getColor = (s) => {
    if (s >= 80) return 'text-emerald-400 stroke-emerald-500';
    if (s >= 60) return 'text-brand-400 stroke-brand-500';
    if (s >= 40) return 'text-amber-400 stroke-amber-500';
    return 'text-rose-400 stroke-rose-500';
  };

  const getBgColor = (s) => {
    if (s >= 80) return 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300';
    if (s >= 60) return 'bg-brand-500/10 border-brand-500/30 text-brand-300';
    if (s >= 40) return 'bg-amber-500/10 border-amber-500/30 text-amber-300';
    return 'bg-rose-500/10 border-rose-500/30 text-rose-300';
  };

  if (size === 'sm') {
    return (
      <span className={`px-2.5 py-1 rounded-full text-xs font-bold border ${getBgColor(score)}`}>
        {score}% Match
      </span>
    );
  }

  const isLarge = size === 'lg';

  return (
    <div className="flex flex-col items-center justify-center shrink-0">
      <div className={`relative flex items-center justify-center ${isLarge ? 'w-20 h-20 sm:w-24 sm:h-24' : 'w-16 h-16 sm:w-18 sm:h-18'}`}>
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
          <path
            className="text-slate-800"
            strokeWidth="3"
            stroke="currentColor"
            fill="none"
            d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
          />
          <path
            className={getColor(score)}
            strokeDasharray={`${score}, 100`}
            strokeWidth="3"
            strokeLinecap="round"
            stroke="currentColor"
            fill="none"
            d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
          />
        </svg>
        <div className="absolute flex flex-col items-center">
          <span className={`${isLarge ? 'text-lg sm:text-2xl font-extrabold' : 'text-base sm:text-lg font-bold'} text-white`}>
            {score}%
          </span>
        </div>
      </div>
      <span className={`${isLarge ? 'text-xs sm:text-sm' : 'text-xs'} uppercase font-bold text-slate-400 mt-1 tracking-wider`}>
        Match
      </span>
    </div>
  );
};

