import React from 'react';
import { ShieldCheck, AlertTriangle, CheckCircle2, ExternalLink, X, FileText, Send } from 'lucide-react';

export const HumanReviewModal = ({ isOpen, onClose, application, onConfirmSubmission, isConfirming }) => {
  if (!isOpen || !application) return null;

  const stagingSession = application.staging_session || {};
  const stagedFields = stagingSession.staged_fields || [];
  const checklist = stagingSession.review_checklist || [
    "Candidate Contact Information Verified",
    "Tailored Resume PDF Attached",
    "Cover Letter Verified Against Factual Data",
    "Work Authorization Disclosures Confirmed",
    "Terms of Service Respected (Manual Final Submit)"
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-3 sm:p-4 overflow-y-auto">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-2xl w-full shadow-2xl overflow-hidden my-auto max-h-[92vh] flex flex-col animate-in fade-in zoom-in duration-200">
        {/* Header */}
        <div className="bg-gradient-to-r from-slate-850 to-slate-800 p-4 sm:p-5 border-b border-slate-700 flex items-center justify-between shrink-0">
          <div className="flex items-center space-x-3 min-w-0">
            <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-amber-400 shrink-0">
              <ShieldCheck className="w-5 h-5 sm:w-6 sm:h-6" />
            </div>
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-1.5 sm:gap-2">
                <h3 className="font-bold text-white text-sm sm:text-base truncate">Mandatory Human Review Gate</h3>
                <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 text-[10px] font-bold uppercase shrink-0">
                  HITL Checkpoint
                </span>
              </div>
              <p className="text-xs text-slate-400 truncate">
                {application.job_title} at <span className="text-white font-medium">{application.company_name}</span> ({application.portal})
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              onClose();
            }}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-700 transition cursor-pointer shrink-0 ml-2"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 sm:p-6 space-y-5 sm:space-y-6 overflow-y-auto flex-1">
          {/* Terms of Service & Responsible AI Notice */}
          <div className="p-3.5 sm:p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-start space-x-3 text-amber-200 text-xs leading-relaxed">
            <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold text-amber-300">Why CareerPilot Never Auto-Submits:</span>
              <p className="mt-1 text-slate-300">
                In strict compliance with <strong>LinkedIn User Agreement (Section 8.2)</strong>, <strong>Naukri Terms of Use</strong>, and <strong>Responsible AI Agent Design</strong>, CareerPilot pre-fills all form fields and stages your application, but intentionally leaves the final confirmation to you. This guarantees your profile is never banned or flagged by platform anti-bot tripwires.
              </p>
            </div>
          </div>

          {/* Staged Form Fields */}
          <div>
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
              Pre-filled Application Data ({stagedFields.length} Fields)
            </h4>
            <div className="bg-slate-950 border border-slate-800 rounded-xl divide-y divide-slate-850">
              {stagedFields.map((field, idx) => (
                <div key={idx} className="p-3 flex items-center justify-between text-xs gap-2">
                  <span className="text-slate-400 font-medium shrink-0">{field.field_name}</span>
                  <div className="flex items-center space-x-2 text-right min-w-0">
                    <span className="text-slate-200 font-mono font-medium max-w-[140px] sm:max-w-xs truncate">
                      {field.staged_value}
                    </span>
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Human Review Checklist */}
          <div>
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Verification Checklist
            </h4>
            <div className="space-y-2">
              {checklist.map((item, idx) => (
                <div key={idx} className="flex items-center space-x-2.5 text-xs text-slate-300">
                  <div className="w-4 h-4 rounded bg-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0">
                    <CheckCircle2 className="w-3 h-3" />
                  </div>
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Modal Actions */}
        <div className="bg-slate-850 p-4 border-t border-slate-800 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 shrink-0">
          {application.apply_url ? (
            <a
              href={application.apply_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center space-x-2 px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition w-full sm:w-auto text-center"
            >
              <span>Inspect Portal URL</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          ) : <div className="hidden sm:block" />}
          <div className="flex flex-col-reverse sm:flex-row items-stretch sm:items-center gap-2 sm:space-x-3 sm:gap-0 sm:ml-auto w-full sm:w-auto">
            <button
              type="button"
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                onClose();
              }}
              className="px-4 py-2.5 sm:py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium transition cursor-pointer text-center"
            >
              Close
            </button>
            <button
              type="button"
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                onConfirmSubmission(application.id || application._id);
              }}
              disabled={isConfirming}
              className="inline-flex items-center justify-center space-x-2 px-4 sm:px-5 py-2.5 sm:py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-md shadow-emerald-500/20 transition disabled:opacity-50 cursor-pointer text-center"
            >
              <Send className="w-3.5 h-3.5 shrink-0" />
              <span>{isConfirming ? 'Confirming...' : 'I Have Reviewed & Submitted'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

