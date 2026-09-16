import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import api from '../api/client';
import { MultiAgentFlow } from '../components/MultiAgentFlow';
import { MatchScoreGauge } from '../components/MatchScoreGauge';
import {
  MessageSquareCode,
  Sparkles,
  Award,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  ArrowRight,
  Send,
  RefreshCw,
  BookOpen
} from 'lucide-react';

export const InterviewPrep = () => {
  const [searchParams] = useSearchParams();
  const initialJobId = searchParams.get('jobId') || '';

  const [jobs, setJobs] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState(initialJobId);
  const [session, setSession] = useState(null);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchJobs();
  }, []);

  useEffect(() => {
    if (initialJobId && jobs.length > 0) {
      setSelectedJobId(initialJobId);
      startInterviewSession(initialJobId);
    } else if (jobs.length > 0 && !selectedJobId) {
      setSelectedJobId(jobs[0].job.id);
    }
  }, [initialJobId, jobs]);

  const fetchJobs = async () => {
    try {
      const res = await api.get('/jobs');
      setJobs(res.data);
    } catch (err) {
      console.error('Failed to load jobs:', err);
    }
  };

  const startInterviewSession = async (jobIdToUse) => {
    const targetId = jobIdToUse || selectedJobId;
    if (!targetId) return;

    setLoading(true);
    try {
      const res = await api.post('/interview/start', { job_id: targetId });
      setSession(res.data);
      setAnswers({});
    } catch (err) {
      console.error('Failed to start interview:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (questionId, text) => {
    setAnswers({ ...answers, [questionId]: text });
  };

  const handleSubmitInterview = async (e) => {
    e.preventDefault();
    if (!session) return;

    setSubmitting(true);
    try {
      const res = await api.post(`/interview/${session.id}/submit`, { answers });
      setSession(res.data);
    } catch (err) {
      console.error('Failed to submit mock interview:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const questions = session?.questions || [];
  const evaluation = session?.evaluation;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-2">
          <h1 className="text-2xl font-bold text-white tracking-tight">Interview Prep Agent & Mock Simulator</h1>
          <span className="px-2 py-0.5 rounded bg-brand-500/20 text-brand-300 border border-brand-500/30 text-[10px] font-bold uppercase">
            Agent 06
          </span>
        </div>
        <p className="text-xs text-slate-400 mt-1">
          JD-derived technical & behavioral questions with simulated senior hiring manager evaluation.
        </p>
      </div>

      <MultiAgentFlow activeStage="interview" />

      {/* Target Job Selector & Start */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-sm">
        <div className="flex-1 w-full">
          <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
            Target Job for Mock Interview
          </label>
          <select
            value={selectedJobId}
            onChange={(e) => {
              setSelectedJobId(e.target.value);
              startInterviewSession(e.target.value);
            }}
            className="w-full bg-slate-950 border border-slate-750 text-white rounded-xl py-2.5 px-3 text-sm focus:outline-none focus:border-brand-500"
          >
            {jobs.map((item) => (
              <option key={item.job.id} value={item.job.id}>
                {item.job.title} at {item.job.company}
              </option>
            ))}
          </select>
        </div>

        <button
          onClick={() => startInterviewSession(selectedJobId)}
          disabled={loading || !selectedJobId}
          className="w-full md:w-auto px-6 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold shadow-lg shadow-brand-500/20 transition flex items-center justify-center space-x-2 disabled:opacity-50 shrink-0 self-end"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>{loading ? 'Synthesizing Questions...' : 'Start New Mock Session'}</span>
        </button>
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center py-20 space-y-3">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-500"></div>
          <p className="text-xs text-slate-400">
            Analyzing target job description and engineering hiring rubrics...
          </p>
        </div>
      ) : session ? (
        <div className="space-y-8">
          {/* Evaluation Report (If Completed) */}
          {evaluation && (
            <div className="p-6 rounded-2xl bg-slate-900 border border-brand-500/40 space-y-6 shadow-xl">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
                <div>
                  <span className="text-xs font-bold text-brand-400 uppercase tracking-wider">
                    Mock Interview Assessment Report
                  </span>
                  <h2 className="text-xl font-bold text-white mt-1">
                    Overall Performance Evaluation
                  </h2>
                  <p className="text-xs text-slate-400 mt-0.5">{evaluation.summary}</p>
                </div>
                <div className="flex items-center space-x-4 bg-slate-950 px-5 py-3 rounded-xl border border-slate-800">
                  <MatchScoreGauge score={evaluation.overall_score} size="md" />
                  <div>
                    <span className="text-[10px] uppercase font-bold text-slate-400">Readiness</span>
                    <div className="text-sm font-bold text-emerald-400">
                      {evaluation.readiness_level}
                    </div>
                  </div>
                </div>
              </div>

              {/* Strengths and Gaps */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 rounded-xl bg-slate-950 border border-slate-850 space-y-2">
                  <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center space-x-1.5">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Identified Strengths</span>
                  </h4>
                  <ul className="space-y-1.5 text-xs text-slate-300">
                    {evaluation.strengths?.map((s, idx) => (
                      <li key={idx}>• {s}</li>
                    ))}
                  </ul>
                </div>

                <div className="p-4 rounded-xl bg-slate-950 border border-slate-850 space-y-2">
                  <h4 className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center space-x-1.5">
                    <AlertCircle className="w-4 h-4" />
                    <span>Critical Improvement Points</span>
                  </h4>
                  <ul className="space-y-1.5 text-xs text-slate-300">
                    {evaluation.critical_gaps?.map((g, idx) => (
                      <li key={idx}>• {g}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* Interactive Q&A Form */}
          <form onSubmit={handleSubmitInterview} className="space-y-6">
            {questions.map((q, idx) => {
              const qFeedback = evaluation?.question_feedbacks?.find((f) => f.question_id === q.id);

              return (
                <div
                  key={q.id}
                  className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4 shadow-sm"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2.5">
                      <span className="w-6 h-6 rounded-full bg-brand-500/20 text-brand-400 flex items-center justify-center text-xs font-bold">
                        {idx + 1}
                      </span>
                      <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                        {q.category}
                      </span>
                    </div>

                    {qFeedback && (
                      <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-slate-800 border border-slate-700 text-brand-300">
                        Score: {qFeedback.score} / 10
                      </span>
                    )}
                  </div>

                  <h3 className="text-base font-semibold text-white leading-snug">
                    {q.question}
                  </h3>

                  <div className="text-xs text-slate-400 bg-slate-950/60 p-3 rounded-lg border border-slate-850 flex items-start space-x-2">
                    <HelpCircle className="w-4 h-4 text-brand-400 shrink-0 mt-0.5" />
                    <span><strong>Interviewer Intent:</strong> {q.context}</span>
                  </div>

                  {/* Candidate Input */}
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                      Your Response:
                    </label>
                    <textarea
                      rows={4}
                      value={answers[q.id] || ''}
                      onChange={(e) => handleAnswerChange(q.id, e.target.value)}
                      placeholder="Type your structured answer here (e.g. STAR method for behavioral, architectural trade-offs for technical)..."
                      className="w-full bg-slate-950 border border-slate-800 focus:border-brand-500 rounded-xl p-3 text-xs text-white focus:outline-none resize-none leading-relaxed"
                    />
                  </div>

                  {/* Feedback Details (if evaluated) */}
                  {qFeedback && (
                    <div className="pt-3 border-t border-slate-800 space-y-3">
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                        <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-850">
                          <span className="text-[10px] uppercase font-bold text-slate-500">Technical Accuracy</span>
                          <p className="text-slate-300 mt-0.5">{qFeedback.technical_accuracy}</p>
                        </div>
                        <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-850">
                          <span className="text-[10px] uppercase font-bold text-slate-500">Clarity & Depth</span>
                          <p className="text-slate-300 mt-0.5">{qFeedback.depth_of_explanation}</p>
                        </div>
                      </div>

                      {q.sample_ideal_answer && (
                        <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-850 text-xs space-y-1">
                          <span className="text-[10px] uppercase font-bold text-emerald-400">
                            Senior Benchmark Answer
                          </span>
                          <p className="text-slate-300 leading-relaxed">{q.sample_ideal_answer}</p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}

            <div className="flex justify-end pt-4">
              <button
                type="submit"
                disabled={submitting}
                className="inline-flex items-center space-x-2 px-8 py-3 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold shadow-lg shadow-brand-500/20 transition disabled:opacity-50"
              >
                <Send className="w-4 h-4" />
                <span>{submitting ? 'Evaluating Responses with AI...' : 'Submit Answers & Receive Score'}</span>
              </button>
            </div>
          </form>
        </div>
      ) : (
        <div className="text-center py-16 bg-slate-900 border border-slate-800 rounded-2xl p-8">
          <MessageSquareCode className="w-10 h-10 text-slate-600 mx-auto mb-3" />
          <h3 className="text-sm font-semibold text-white">Select a job to initiate mock interview prep</h3>
          <p className="text-xs text-slate-400 mt-1">
            The agent will synthesize technical, project-based, and behavioral questions.
          </p>
        </div>
      )}
    </div>
  );
};

