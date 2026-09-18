import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTour } from '../context/TourContext';
import { useAuth } from '../context/AuthContext';
import {
  Compass,
  FileText,
  Cpu,
  Search,
  GraduationCap,
  FileCheck,
  ShieldCheck,
  MessageSquareCode,
  ArrowRight,
  ArrowLeft,
  X,
  Sparkles,
  CheckCircle2,
  ExternalLink
} from 'lucide-react';

const TOUR_STEPS = [
  {
    step: 1,
    title: 'Welcome to CareerPilot AI 🧭',
    subtitle: 'From AI Anxiety to AI Empowerment',
    icon: Compass,
    color: 'from-brand-600 to-indigo-600',
    path: '/',
    actionLabel: 'Go to Dashboard',
    whatYouDo: 'Use CareerPilot as your personal career copilot that coordinates 5 specialized AI agents to guide your job-hunt from start to finish.',
    whatAIDoes: 'Orchestrates a stateful multi-agent pipeline using LangGraph, keeping track of your skills, applications, and readiness progress.',
    whyItMatters: 'Instead of fearing that "AI is taking our jobs", CareerPilot puts an orchestrated multi-agent system in your corner to fight for your career.'
  },
  {
    step: 2,
    title: 'Candidate Profile & Ground Truth 👤',
    subtitle: 'Step 1: Uploading Your Real Experience',
    icon: FileText,
    color: 'from-blue-600 to-cyan-600',
    path: '/profile',
    actionLabel: 'Open Profile & Upload Resume',
    whatYouDo: 'Upload your PDF resume and enter your public GitHub and LeetCode usernames.',
    whatAIDoes: 'Extracts skills, education, and bullet points using NLP (pypdf). Gathers public GitHub repositories and LeetCode problem counts.',
    whyItMatters: 'Establishes your immutable "Ground Truth". The AI is strictly forbidden from inventing fake degrees, employment, or skills.'
  },
  {
    step: 3,
    title: 'Assessment Agent & Skill Vector 🧠',
    subtitle: 'Step 2: Empirical Profiling',
    icon: Cpu,
    color: 'from-purple-600 to-pink-600',
    path: '/assessment',
    actionLabel: 'View Skill Assessment',
    whatYouDo: 'Inspect your multi-category skill vector (Languages, Frameworks, Databases, Tools, and CS Foundations).',
    whatAIDoes: 'Combines resume NLP with live GitHub languages and LeetCode DSA stats to compute your Empirical Readiness Score (0–100%).',
    whyItMatters: 'Gives recruiters and examiners concrete proof of your technical depth backed by real public developer telemetry.'
  },
  {
    step: 4,
    title: 'Job Explorer & Semantic Matching 💼',
    subtitle: 'Step 3: Finding High-Probability Roles',
    icon: Search,
    color: 'from-emerald-600 to-teal-600',
    path: '/jobs',
    actionLabel: 'Explore Matched Jobs',
    whatYouDo: 'Browse real fresher/SDE-1 job postings from LinkedIn, Naukri, and ATS portals, or paste any custom JD from the web.',
    whatAIDoes: 'Computes high-dimensional cosine vector similarity, scoring your fit from 0 to 100% and providing human-readable explanations.',
    whyItMatters: 'Stops you from blindly mass-applying to roles where your resume would be discarded by ATS keyword filters.'
  },
  {
    step: 5,
    title: 'Market Upskilling & Free Curation 🎓',
    subtitle: 'Step 4: Closing Real Gaps (Zero Generic Lists)',
    icon: GraduationCap,
    color: 'from-amber-600 to-orange-600',
    path: '/learning',
    actionLabel: 'Open Learning Plan',
    whatYouDo: 'View your missing skills ranked by true market frequency (e.g. "Spring Boot appears in 73% of your target backend roles").',
    whatAIDoes: 'Maps each gap to 100% free accredited resources: NPTEL (IIT video courses), curated developer YouTube playlists, and official documentation.',
    whyItMatters: 'Focuses your valuable study time on high-yield technologies that will actually move the needle for campus placements.'
  },
  {
    step: 6,
    title: 'Tailoring Agent & CAR/STAR Bullets ✍️',
    subtitle: 'Step 5: Resume Bullet Transformations',
    icon: FileCheck,
    color: 'from-brand-600 to-violet-600',
    path: '/tailoring',
    actionLabel: 'Try Resume Tailoring',
    whatYouDo: 'Pick a shortlisted job and click "Tailor Resume".',
    whatAIDoes: 'Rewrites your existing bullet points into high-impact Context-Action-Result (CAR/STAR) statements with quantifiable metrics and drafts a cover letter.',
    whyItMatters: 'Programmatic Zero-Hallucination guarantee: Verifies every technical term against your original profile so you can defend every word in an interview.'
  },
  {
    step: 7,
    title: 'Application Staging & Human Review 🛡️',
    subtitle: 'Step 6: Responsible Browser Automation',
    icon: ShieldCheck,
    color: 'from-amber-600 to-rose-600',
    path: '/applications',
    actionLabel: 'View Application Staging',
    whatYouDo: 'Click "Launch Browser Staging". Watch Playwright pre-fill fields, then inspect the staged form and confirm the final submission.',
    whatAIDoes: 'Navigates to the portal, fills name, contact, GitHub, and attaches the tailored resume PDF, but INTENTIONALLY STOPS at the review gate.',
    whyItMatters: 'Fully autonomous bots violate LinkedIn Section 8.2 & Naukri ToS, getting accounts banned. CareerPilot’s HITL design keeps you 100% safe and in control.'
  },
  {
    step: 8,
    title: 'JD-Specific Mock Interview Simulator 🎙️',
    subtitle: 'Step 7: Real-Time Practice & Scoring',
    icon: MessageSquareCode,
    color: 'from-indigo-600 to-blue-600',
    path: '/interview',
    actionLabel: 'Practice Mock Interview',
    whatYouDo: 'Answer 4 role-specific interview questions (Technical, Project Deep Dive, CS Foundations, and Behavioral).',
    whatAIDoes: 'Evaluates your answers using senior hiring manager rubrics, assigning an overall readiness score and providing sample benchmark answers.',
    whyItMatters: 'Walk into your placement interview confident, having already practiced the exact questions the interviewer is likely to ask.'
  }
];

export const AppTourModal = ({ isOpen: propIsOpen, onClose: propOnClose }) => {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const navigate = useNavigate();
  const tour = useTour();
  const { user, login, register } = useAuth();

  // Support both context-driven and prop-driven visibility
  const isOpen = propIsOpen !== undefined ? propIsOpen : tour?.isTourOpen;
  const handleClose = propOnClose || (tour ? tour.closeTour : () => {});

  if (!isOpen) return null;

  const current = TOUR_STEPS[currentStepIndex];
  const Icon = current.icon;
  const isFirst = currentStepIndex === 0;
  const isLast = currentStepIndex === TOUR_STEPS.length - 1;

  const handleNext = () => {
    if (!isLast) {
      setCurrentStepIndex(currentStepIndex + 1);
    } else {
      handleClose();
    }
  };

  const handlePrev = () => {
    if (!isFirst) {
      setCurrentStepIndex(currentStepIndex - 1);
    }
  };

  const handleJumpToPage = async () => {
    // If not logged in and navigating to a protected route, auto-login with demo account
    if (!user && current.path !== '/login') {
      try {
        try {
          await login('candidate@example.com', 'password123');
        } catch {
          await register('Aarav Sharma', 'candidate@example.com', 'password123');
        }
      } catch (e) {
        console.warn('Auto-login demo skipped:', e);
      }
    }
    navigate(current.path);
    handleClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-3 sm:p-4 overflow-y-auto">
      <div className="bg-slate-900 border border-slate-750 rounded-2xl sm:rounded-3xl max-w-2xl w-full shadow-2xl overflow-hidden my-auto max-h-[92vh] flex flex-col animate-in fade-in zoom-in-95 duration-200">
        {/* Top Progress & Close Bar */}
        <div className="p-3.5 sm:p-4 px-4 sm:px-6 border-b border-slate-800 flex items-center justify-between bg-slate-950/60 shrink-0">
          <div className="flex items-center space-x-2 min-w-0">
            <span className="text-xs font-mono font-bold text-brand-400 uppercase tracking-wider shrink-0">
              Tour Step {current.step}/{TOUR_STEPS.length}
            </span>
            <div className="flex space-x-1 ml-1 sm:ml-2 overflow-hidden">
              {TOUR_STEPS.map((_, idx) => (
                <div
                  key={idx}
                  onClick={() => setCurrentStepIndex(idx)}
                  className={`h-1.5 sm:h-2 rounded-full cursor-pointer transition-all ${
                    idx === currentStepIndex
                      ? 'w-5 sm:w-6 bg-brand-500'
                      : idx < currentStepIndex
                      ? 'w-1.5 sm:w-2 bg-emerald-500/80'
                      : 'w-1.5 sm:w-2 bg-slate-750 hover:bg-slate-600'
                  }`}
                />
              ))}
            </div>
          </div>
          <button
            onClick={handleClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition shrink-0 ml-2"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Step Banner */}
        <div className="p-4 sm:p-6 lg:p-8 bg-gradient-to-r from-slate-900 to-slate-850 border-b border-slate-800 flex items-start space-x-3 sm:space-x-4 shrink-0">
          <div
            className={`w-10 h-10 sm:w-12 sm:h-12 rounded-xl sm:rounded-2xl bg-gradient-to-tr ${current.color} flex items-center justify-center text-white shadow-lg shrink-0 mt-0.5`}
          >
            <Icon className="w-5 h-5 sm:w-6 sm:h-6" />
          </div>
          <div className="flex-1 min-w-0">
            <span className="text-xs font-bold text-brand-400 uppercase tracking-wider block truncate">
              {current.subtitle}
            </span>
            <h2 className="text-lg sm:text-2xl font-extrabold text-white tracking-tight mt-0.5">
              {current.title}
            </h2>
          </div>
        </div>

        {/* 3 Core Blocks: What you do, What AI does, Why it matters */}
        <div className="p-4 sm:p-6 lg:p-8 space-y-3 sm:space-y-4 overflow-y-auto flex-1">
          {/* Block 1: What You Do */}
          <div className="p-3.5 sm:p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
            <div className="flex items-center space-x-2 text-xs sm:text-sm font-bold text-slate-300 uppercase tracking-wider">
              <span className="w-2 h-2 rounded-full bg-brand-400 shrink-0"></span>
              <span>What You Do (Candidate Action)</span>
            </div>
            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed pl-4">
              {current.whatYouDo}
            </p>
          </div>

          {/* Block 2: What the AI Does */}
          <div className="p-3.5 sm:p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
            <div className="flex items-center space-x-2 text-xs sm:text-sm font-bold text-brand-300 uppercase tracking-wider">
              <Sparkles className="w-3.5 h-3.5 text-brand-400 shrink-0" />
              <span>What the AI Does Under the Hood</span>
            </div>
            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed pl-5">
              {current.whatAIDoes}
            </p>
          </div>

          {/* Block 3: Why It Matters */}
          <div className="p-3.5 sm:p-4 rounded-xl bg-brand-950/20 border border-brand-800/40 space-y-1">
            <div className="flex items-center space-x-2 text-xs sm:text-sm font-bold text-emerald-400 uppercase tracking-wider">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
              <span>Why It Matters (Key Differentiator)</span>
            </div>
            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed pl-5">
              {current.whyItMatters}
            </p>
          </div>
        </div>

        {/* Modal Footer Controls */}
        <div className="p-3.5 sm:p-4 px-4 sm:px-6 bg-slate-950 border-t border-slate-800 flex flex-col-reverse sm:flex-row items-stretch sm:items-center justify-between gap-2.5 sm:gap-3 shrink-0">
          <div className="flex items-center space-x-2">
            {!isFirst && (
              <button
                onClick={handlePrev}
                className="inline-flex items-center justify-center space-x-1.5 px-3.5 py-2.5 sm:py-2 rounded-xl bg-slate-850 hover:bg-slate-800 text-slate-300 text-xs sm:text-sm font-semibold border border-slate-750 transition"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>Previous</span>
              </button>
            )}

            {current.path && (
              <button
                onClick={handleJumpToPage}
                className="inline-flex items-center justify-center space-x-1.5 px-3.5 py-2.5 sm:py-2 rounded-xl bg-slate-800 hover:bg-slate-750 text-brand-300 text-xs sm:text-sm font-semibold border border-slate-700 transition"
              >
                <span>{current.actionLabel}</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          <div className="flex items-center justify-between sm:justify-end space-x-2">
            <button
              onClick={handleClose}
              className="px-3.5 py-2.5 sm:py-2 rounded-xl text-xs sm:text-sm text-slate-400 hover:text-white transition"
            >
              Skip Tour
            </button>
            <button
              onClick={handleNext}
              className="inline-flex items-center justify-center space-x-2 px-4 sm:px-5 py-2.5 sm:py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs sm:text-sm font-bold shadow-lg shadow-brand-500/20 transition flex-1 sm:flex-initial"
            >
              <span>{isLast ? 'Finish Tour' : 'Next Step'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
