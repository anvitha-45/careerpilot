import React, { useState } from 'react';
import { X, UserPlus, ArrowRight, Check } from 'lucide-react';

export const GoogleIcon = ({ className = "w-5 h-5" }) => (
  <svg className={className} viewBox="0 0 24 24">
    <path
      fill="#4285F4"
      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
    />
    <path
      fill="#34A853"
      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
    />
    <path
      fill="#FBBC05"
      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
    />
    <path
      fill="#EA4335"
      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
    />
  </svg>
);

const DEMO_GOOGLE_ACCOUNTS = [
  {
    name: 'Aarav Sharma',
    email: 'aarav.sharma@gmail.com',
    avatar_color: 'bg-emerald-600',
    google_id: 'google_1029384756'
  },
  {
    name: 'Padmanabhuni Deepanvitha',
    email: 'deepanvitha.sai@gmail.com',
    avatar_color: 'bg-indigo-600',
    google_id: 'google_9847561029'
  }
];

export const GoogleSignInModal = ({ isOpen, onClose, onSelectGoogleAccount, loading }) => {
  const [showCustomForm, setShowCustomForm] = useState(false);
  const [customName, setCustomName] = useState('');
  const [customEmail, setCustomEmail] = useState('');
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleCustomSubmit = (e) => {
    e.preventDefault();
    if (!customEmail || !customName) {
      setError('Please provide both name and Google email.');
      return;
    }
    if (!customEmail.includes('@')) {
      setError('Please enter a valid Google email address.');
      return;
    }
    setError('');
    onSelectGoogleAccount({
      name: customName.trim(),
      email: customEmail.trim(),
      google_id: `google_${Date.now()}`
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 overflow-y-auto animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-slate-750 rounded-2xl sm:rounded-3xl max-w-md w-full shadow-2xl overflow-hidden my-auto max-h-[92vh] flex flex-col animate-in zoom-in-95 duration-200">
        
        {/* Header */}
        <div className="p-5 sm:p-6 pb-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-white flex items-center justify-center shadow-md">
              <GoogleIcon className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base sm:text-lg font-bold text-white">Sign in with Google</h3>
              <p className="text-xs text-slate-400">to continue to <span className="text-brand-300 font-medium">CareerPilot AI</span></p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-5 sm:p-6 space-y-4 overflow-y-auto flex-1">
          {error && (
            <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs sm:text-sm">
              {error}
            </div>
          )}

          {!showCustomForm ? (
            <>
              <div className="text-xs uppercase tracking-wider font-semibold text-slate-400">
                Choose an account
              </div>

              <div className="space-y-2">
                {DEMO_GOOGLE_ACCOUNTS.map((acc, idx) => (
                  <button
                    key={idx}
                    type="button"
                    disabled={loading}
                    onClick={() => onSelectGoogleAccount(acc)}
                    className="w-full p-3.5 rounded-xl bg-slate-950 hover:bg-slate-850 border border-slate-800 hover:border-slate-700 transition flex items-center space-x-3.5 text-left cursor-pointer group disabled:opacity-50"
                  >
                    <div className={`w-10 h-10 rounded-full ${acc.avatar_color} text-white font-bold flex items-center justify-center text-sm shadow-md shrink-0`}>
                      {acc.name.charAt(0)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-semibold text-white group-hover:text-brand-300 transition truncate">
                        {acc.name}
                      </div>
                      <div className="text-xs text-slate-400 truncate">
                        {acc.email}
                      </div>
                    </div>
                    <GoogleIcon className="w-4 h-4 opacity-50 group-hover:opacity-100 transition shrink-0" />
                  </button>
                ))}

                <button
                  type="button"
                  onClick={() => setShowCustomForm(true)}
                  className="w-full p-3.5 rounded-xl bg-slate-950/60 hover:bg-slate-850 border border-dashed border-slate-750 hover:border-brand-500/50 transition flex items-center space-x-3.5 text-left cursor-pointer text-slate-300 hover:text-white"
                >
                  <div className="w-10 h-10 rounded-full bg-slate-800 text-slate-300 flex items-center justify-center shrink-0">
                    <UserPlus className="w-4 h-4" />
                  </div>
                  <div className="text-sm font-medium">
                    Use another Google account
                  </div>
                </button>
              </div>
            </>
          ) : (
            <form onSubmit={handleCustomSubmit} className="space-y-3.5">
              <div className="flex items-center justify-between">
                <span className="text-xs uppercase tracking-wider font-semibold text-slate-400">
                  Enter Google Credentials
                </span>
                <button
                  type="button"
                  onClick={() => setShowCustomForm(false)}
                  className="text-xs text-brand-400 hover:underline"
                >
                  Back to accounts
                </button>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Your Name</label>
                <input
                  type="text"
                  required
                  value={customName}
                  onChange={(e) => setCustomName(e.target.value)}
                  placeholder="Aarav Sharma"
                  className="w-full bg-slate-950 border border-slate-800 focus:border-brand-500 rounded-xl py-2.5 px-3.5 text-sm text-white focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Gmail / Google Workspace Email</label>
                <input
                  type="email"
                  required
                  value={customEmail}
                  onChange={(e) => setCustomEmail(e.target.value)}
                  placeholder="your.name@gmail.com"
                  className="w-full bg-slate-950 border border-slate-800 focus:border-brand-500 rounded-xl py-2.5 px-3.5 text-sm text-white focus:outline-none"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs sm:text-sm font-semibold shadow-lg shadow-brand-500/20 transition flex items-center justify-center space-x-2 cursor-pointer disabled:opacity-50"
              >
                <span>{loading ? 'Authenticating with Google...' : 'Continue as Google User'}</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </form>
          )}

          {/* Google Consent Disclosure */}
          <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 text-[11px] sm:text-xs text-slate-400 leading-relaxed">
            To continue, Google will share your verified name, email address, and account avatar with <strong className="text-slate-300">CareerPilot AI</strong>. No passwords will ever be shared.
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 bg-slate-950 border-t border-slate-800 flex items-center justify-end">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs sm:text-sm text-slate-400 hover:text-white transition cursor-pointer"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

