import React from 'react';
import { ExternalLink, BookOpen, Video, FileText, Code2, Clock } from 'lucide-react';

export const ResourceCard = ({ resource }) => {
  const getIcon = (type) => {
    switch (type) {
      case 'ACADEMIC_COURSE':
        return BookOpen;
      case 'PRACTICAL_VIDEO':
        return Video;
      case 'DOCUMENTATION':
        return FileText;
      default:
        return Code2;
    }
  };

  const Icon = getIcon(resource.resource_type);

  return (
    <div className="p-3.5 rounded-xl bg-slate-850 border border-slate-750 hover:border-slate-650 transition flex flex-col justify-between group">
      <div>
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 rounded-md bg-brand-500/15 text-brand-400 flex items-center justify-center">
              <Icon className="w-3.5 h-3.5" />
            </div>
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
              {resource.provider}
            </span>
          </div>
          <span className="text-[10px] px-2 py-0.5 rounded font-bold uppercase bg-emerald-500/15 text-emerald-400 border border-emerald-500/20">
            {resource.cost}
          </span>
        </div>

        <h5 className="text-xs font-semibold text-white group-hover:text-brand-300 transition line-clamp-2">
          {resource.title}
        </h5>
        {resource.description && (
          <p className="text-[11px] text-slate-400 mt-1 line-clamp-2 leading-relaxed">
            {resource.description}
          </p>
        )}
      </div>

      <div className="mt-3 pt-2.5 border-t border-slate-800 flex items-center justify-between text-xs">
        <div className="flex items-center space-x-1.5 text-slate-400 text-[11px]">
          <Clock className="w-3 h-3" />
          <span>{resource.time_commitment}</span>
        </div>
        <a
          href={resource.url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center space-x-1 text-[11px] font-semibold text-brand-400 hover:text-brand-300 transition"
        >
          <span>Access Free</span>
          <ExternalLink className="w-3 h-3" />
        </a>
      </div>
    </div>
  );
};

