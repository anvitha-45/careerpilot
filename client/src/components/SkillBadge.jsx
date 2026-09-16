import React from 'react';
import { Check, AlertCircle } from 'lucide-react';

export const SkillBadge = ({ name, type = 'matched', priority }) => {
  if (type === 'matched') {
    return (
      <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-md bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs font-medium">
        <Check className="w-3 h-3 text-emerald-400" />
        <span>{name}</span>
      </span>
    );
  }

  if (type === 'missing') {
    const isCritical = priority === 'CRITICAL';
    return (
      <span
        className={`inline-flex items-center space-x-1 px-2.5 py-1 rounded-md text-xs font-medium border ${
          isCritical
            ? 'bg-rose-500/15 border-rose-500/30 text-rose-300'
            : 'bg-amber-500/15 border-amber-500/30 text-amber-300'
        }`}
      >
        <AlertCircle className="w-3 h-3 shrink-0" />
        <span>{name}</span>
        {priority && (
          <span className="text-[9px] uppercase font-bold tracking-wider opacity-80">
            ({priority})
          </span>
        )}
      </span>
    );
  }

  return (
    <span className="inline-flex items-center px-2.5 py-1 rounded-md bg-slate-800 border border-slate-750 text-slate-300 text-xs font-medium">
      {name}
    </span>
  );
};

