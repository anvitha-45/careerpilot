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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-2xl w-full shadow-2xl overflow-hidden my-8 animate-in fade-in zoom-in duration-200">
        {/* Header */}
        <div className="bg-gradient-to-r from-slate-850 to-slate-800 p-5 border-b border-slate-700 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-amber-400">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="font-bold text-white text-base">Mandatory Human Review Gate</h3>
                <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 text-[10px] font-bold uppercase">
                  HITL Checkpoint
                </span>
              </div>
              <p className="text-xs text-slate-400">
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
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-700 transition cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6 max-h-[70vh] overflow-y-auto">
          {/* Terms of Service & Responsible AI Notice */}
          <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-start space-x-3 text-amber-200 text-xs leading-relaxed">
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
                <div key={idx} className="p-3 flex items-center justify-between text-xs">
                  <span className="text-slate-400 font-medium">{field.field_name}</span>
                  <div className="flex items-center space-x-2 text-right">
                    <span className="text-slate-200 font-mono font-medium max-w-xs truncate">
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
        <div className="bg-slate-850 p-4 border-t border-slate-800 flex items-center justify-between gap-3">
          {application.apply_url && (
            <a
              href={application.apply_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center space-x-2 px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition"
            >
              <span>Inspect Portal URL</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          )}
          <div className="flex items-center space-x-3 ml-auto">
            <button
              type="button"
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                onClose();
              }}
              className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium transition cursor-pointer"
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
              className="inline-flex items-center space-x-2 px-5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-md shadow-emerald-500/20 transition disabled:opacity-50 cursor-pointer"
            >
              <Send className="w-3.5 h-3.5" />
              <span>{isConfirming ? 'Confirming...' : 'I Have Reviewed & Submitted'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

