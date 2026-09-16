import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/client';
import { MatchScoreGauge } from '../components/MatchScoreGauge';
import { SkillBadge } from '../components/SkillBadge';
import {
  Search,
  Filter,
  Plus,
  Briefcase,
  Building,
  MapPin,
  ExternalLink,
  Sparkles,
  CheckCircle2,
  X
} from 'lucide-react';

export const JobExplorer = () => {
  const [jobs, setJobs] = useState([]);
  const [search, setSearch] = useState('');
  const [portal, setPortal] = useState('All');
  const [minScore, setMinScore] = useState(0);
  const [loading, setLoading] = useState(true);

  // Import Job Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newCompany, setNewCompany] = useState('');
  const [newPortal, setNewPortal] = useState('LinkedIn');
  const [newDescription, setNewDescription] = useState('');
  const [importing, setImporting] = useState(false);

  useEffect(() => {
    fetchJobs();
  }, [search, portal, minScore]);

  const fetchJobs = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      if (portal !== 'All') params.append('portal', portal);
      if (minScore > 0) params.append('min_score', minScore);

      const res = await api.get(`/jobs?${params.toString()}`);
      setJobs(res.data);
    } catch (err) {
      console.error('Failed to fetch jobs:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleImportJob = async (e) => {
    e.preventDefault();
    setImporting(true);
    try {
      await api.post('/jobs/import', {
        title: newTitle,
        company: newCompany,
        portal: newPortal,
        description: newDescription,
        location: 'Bengaluru / Remote, India'
      });
      setIsModalOpen(false);
      setNewTitle('');
      setNewCompany('');
      setNewDescription('');
      await fetchJobs();
    } catch (err) {
      console.error('Failed to import job:', err);
    } finally {
      setImporting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Job Explorer & Semantic Matching</h1>
          <p className="text-xs text-slate-400 mt-1">
            Real postings ingested from LinkedIn, Naukri, and ATS portals. Scored by vector cosine similarity.
          </p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold shadow-lg shadow-brand-500/20 transition self-start"
        >
          <Plus className="w-4 h-4" />
          <span>Import Custom JD</span>
        </button>
      </div>

      {/* Filter Bar */}
      <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col md:flex-row items-center gap-4">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by role title, company, or tech stack..."
            className="w-full bg-slate-950 border border-slate-800 focus:border-brand-500 rounded-xl py-2 pl-10 pr-4 text-xs text-white focus:outline-none"
          />
        </div>

        <div className="flex items-center space-x-3 w-full md:w-auto">
          <div className="flex items-center space-x-2">
            <span className="text-xs text-slate-400 font-medium">Portal:</span>
            <select
              value={portal}
              onChange={(e) => setPortal(e.target.value)}
              className="bg-slate-950 border border-slate-800 text-xs text-white rounded-lg py-1.5 px-2.5 focus:outline-none"
            >
              <option value="All">All Portals</option>
              <option value="LinkedIn">LinkedIn</option>
              <option value="Naukri">Naukri</option>
              <option value="Greenhouse">Greenhouse ATS</option>
            </select>
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-xs text-slate-400 font-medium">Min Match:</span>
            <select
              value={minScore}
              onChange={(e) => setMinScore(Number(e.target.value))}
              className="bg-slate-950 border border-slate-800 text-xs text-white rounded-lg py-1.5 px-2.5 focus:outline-none"
            >
              <option value={0}>All Scores</option>
              <option value={60}>60%+ Match</option>
              <option value={75}>75%+ Match</option>
              <option value={85}>85%+ Match</option>
            </select>
          </div>
        </div>
      </div>

      {/* Jobs List */}
      {loading ? (
        <div className="flex items-center justify-center py-16">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-500"></div>
        </div>
      ) : jobs.length === 0 ? (
        <div className="text-center py-16 bg-slate-900 border border-slate-800 rounded-2xl p-8">
          <Briefcase className="w-10 h-10 text-slate-600 mx-auto mb-3" />
          <h3 className="text-sm font-semibold text-white">No jobs found matching criteria</h3>
          <p className="text-xs text-slate-400 mt-1">Try relaxing filters or import a new job description.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {jobs.map((item) => (
            <div
              key={item.job.id}
              className="p-6 rounded-2xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition flex flex-col md:flex-row items-start md:items-center justify-between gap-6 shadow-sm"
            >
              <div className="space-y-3 flex-1">
                <div className="flex items-center space-x-3">
                  <h3 className="text-base font-bold text-white">{item.job.title}</h3>
                  <span className="text-xs px-2.5 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-slate-300 font-medium">
                    {item.job.portal}
                  </span>
                  {item.status && item.status !== 'DISCOVERED' && (
                    <span className="text-[10px] px-2 py-0.5 rounded font-bold uppercase bg-brand-500/20 text-brand-300 border border-brand-500/30">
                      {item.status}
                    </span>
                  )}
                </div>

                <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-400">
                  <span className="font-semibold text-slate-200 flex items-center space-x-1">
                    <Building className="w-3.5 h-3.5 text-slate-500" />
                    <span>{item.job.company}</span>
                  </span>
                  <span>•</span>
                  <span className="flex items-center space-x-1">
                    <MapPin className="w-3.5 h-3.5 text-slate-500" />
                    <span>{item.job.location}</span>
                  </span>
                  <span>•</span>
                  <span className="text-emerald-400 font-medium">{item.job.salary_range}</span>
                  <span>•</span>
                  <span className="text-slate-400">{item.job.work_mode}</span>
                </div>

                <p className="text-xs text-slate-300 line-clamp-2 leading-relaxed">
                  {item.job.description}
                </p>

                <div className="flex flex-wrap items-center gap-1.5 pt-1">
                  {item.matched_skills.map((s) => (
                    <SkillBadge key={s} name={s} type="matched" />
                  ))}
                  {item.missing_skills.map((s) => (
                    <SkillBadge key={s} name={s} type="missing" priority="CRITICAL" />
                  ))}
                </div>

                <div className="text-[11px] text-brand-400/90 font-medium bg-brand-950/30 p-2.5 rounded-lg border border-brand-900/40">
                  <strong>Semantic Match Reason:</strong> {item.explanation}
                </div>
              </div>

              {/* Match Gauge & Actions */}
              <div className="flex md:flex-col items-center md:items-end justify-between w-full md:w-auto gap-4 pt-4 md:pt-0 border-t md:border-t-0 border-slate-800 shrink-0">
                <MatchScoreGauge score={item.match_score} size="md" />

                <div className="flex items-center space-x-2">
                  <Link
                    to={`/jobs/${item.job.id}`}
                    className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-750 text-slate-300 text-xs font-semibold border border-slate-700 transition"
                  >
                    Details
                  </Link>
                  <Link
                    to={`/tailoring?jobId=${item.job.id}`}
                    className="px-3.5 py-1.5 rounded-lg bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold shadow-md shadow-brand-500/20 transition"
                  >
                    Tailor Resume
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Import Job Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 overflow-y-auto">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4 my-8">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-white text-base">Import Custom Job Description</h3>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleImportJob} className="space-y-3.5">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Role Title</label>
                <input
                  type="text"
                  required
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="e.g. SDE-1 Backend"
                  className="w-full bg-slate-950 border border-slate-800 focus:border-brand-500 rounded-lg p-2 text-xs text-white focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Company Name</label>
                <input
                  type="text"
                  required
                  value={newCompany}
                  onChange={(e) => setNewCompany(e.target.value)}
                  placeholder="e.g. Atlassian"
                  className="w-full bg-slate-950 border border-slate-800 focus:border-brand-500 rounded-lg p-2 text-xs text-white focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Portal / Source</label>
                <select
                  value={newPortal}
                  onChange={(e) => setNewPortal(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 text-xs text-white rounded-lg p-2 focus:outline-none"
                >
                  <option value="LinkedIn">LinkedIn</option>
                  <option value="Naukri">Naukri</option>
                  <option value="Greenhouse">Greenhouse ATS</option>
                  <option value="Direct Career Site">Direct Career Site</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Job Description Text</label>
                <textarea
                  required
                  rows={6}
                  value={newDescription}
                  onChange={(e) => setNewDescription(e.target.value)}
                  placeholder="Paste the raw job requirements here. The NLP agent will automatically extract technical skills and compute match vectors..."
                  className="w-full bg-slate-950 border border-slate-800 focus:border-brand-500 rounded-lg p-2 text-xs text-white focus:outline-none resize-none"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300 text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={importing}
                  className="px-5 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold transition"
                >
                  {importing ? 'Analyzing JD...' : 'Import & Compute Match'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

