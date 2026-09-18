import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';
import {
  Upload,
  FileText,
  Github,
  Code2,
  CheckCircle,
  Sparkles,
  Save,
  AlertCircle
} from 'lucide-react';

export const Profile = () => {
  const { profile, refreshProfile } = useAuth();
  const [fullName, setFullName] = useState('');
  const [phone, setPhone] = useState('');
  const [targetLocation, setTargetLocation] = useState('');
  const [targetRoles, setTargetRoles] = useState('');
  const [githubUsername, setGithubUsername] = useState('');
  const [leetcodeUsername, setLeetcodeUsername] = useState('');
  const [newSkill, setNewSkill] = useState('');
  const [skillsList, setSkillsList] = useState([]);
  
  const [uploading, setUploading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    if (profile) {
      setFullName(profile.full_name || '');
      setPhone(profile.phone || '');
      setTargetLocation(profile.target_location || 'India (Bengaluru, Hyderabad, Remote)');
      setTargetRoles(profile.target_roles ? profile.target_roles.join(', ') : 'Software Engineer, Backend Developer');
      setGithubUsername(profile.github_username || '');
      setLeetcodeUsername(profile.leetcode_username || '');
      setSkillsList(profile.skill_vector?.all_skills || []);
    }
  }, [profile]);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setUploading(true);
    setMessage('');
    setError('');

    try {
      const res = await api.post('/profile/upload-resume', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setMessage(`Resume uploaded! Extracted ${res.data.extracted_skills_count} skills. Readiness score updated.`);
      await refreshProfile();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload and parse resume.');
    } finally {
      setUploading(false);
    }
  };

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage('');
    setError('');

    const rolesArray = targetRoles.split(',').map((r) => r.trim()).filter(Boolean);

    try {
      await api.put('/profile', {
        full_name: fullName,
        phone,
        target_location: targetLocation,
        target_roles: rolesArray,
        github_username: githubUsername,
        leetcode_username: leetcodeUsername,
        self_reported_skills: skillsList
      });
      setMessage('Profile and Assessment Agent signals successfully updated!');
      await refreshProfile();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update profile.');
    } finally {
      setSaving(false);
    }
  };

  const addSkill = () => {
    if (newSkill.trim() && !skillsList.includes(newSkill.trim())) {
      setSkillsList([...skillsList, newSkill.trim()]);
      setNewSkill('');
    }
  };

  const removeSkill = (skillToRemove) => {
    setSkillsList(skillsList.filter((s) => s !== skillToRemove));
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">Candidate Profile & Ground Truth</h1>
        <p className="text-xs sm:text-sm text-slate-400 mt-1">
          The Assessment Agent uses your resume and public profiles as the strict ground-truth dataset.
        </p>
      </div>

      {message && (
        <div className="p-3.5 sm:p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs sm:text-sm flex items-center space-x-2">
          <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{message}</span>
        </div>
      )}

      {error && (
        <div className="p-3.5 sm:p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs sm:text-sm flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Resume Upload Box */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 sm:p-6 shadow-sm">
        <h3 className="text-sm sm:text-base font-semibold text-white uppercase tracking-wider mb-2 flex items-center space-x-2">
          <FileText className="w-4 h-4 text-brand-400" />
          <span>Step 1: Upload Resume (PDF)</span>
        </h3>
        <p className="text-xs sm:text-sm text-slate-400 mb-4">
          Our NLP Parser extracts technical skills, education, and bullet points without fabricating information.
        </p>

        <div className="border-2 border-dashed border-slate-750 hover:border-brand-500/50 rounded-xl p-4 sm:p-6 text-center transition bg-slate-950/50">
          <input
            type="file"
            id="resume-upload"
            accept=".pdf"
            onChange={handleFileUpload}
            disabled={uploading}
            className="hidden"
          />
          <label htmlFor="resume-upload" className="cursor-pointer flex flex-col items-center">
            <div className="w-12 h-12 rounded-xl bg-brand-500/10 text-brand-400 flex items-center justify-center mb-3">
              <Upload className="w-6 h-6 animate-bounce" />
            </div>
            <span className="text-sm sm:text-base font-semibold text-white">
              {uploading ? 'Parsing Resume with NLP...' : 'Click to Upload Resume PDF'}
            </span>
            <span className="text-xs sm:text-sm text-slate-500 mt-1">Supports standard PDF resumes up to 10MB</span>
          </label>
        </div>

        {profile?.resume_filename && (
          <div className="mt-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 p-3 rounded-lg bg-slate-850 border border-slate-750 text-xs sm:text-sm text-slate-300">
            <span className="font-medium text-white flex items-center space-x-2 min-w-0 truncate">
              <FileText className="w-4 h-4 text-brand-400 shrink-0" />
              <span className="truncate">Current file: {profile.resume_filename}</span>
            </span>
            <span className="text-emerald-400 font-semibold flex items-center space-x-1 shrink-0">
              <CheckCircle className="w-3.5 h-3.5" />
              <span>Verified Ground Truth</span>
            </span>
          </div>
        )}
      </div>

      {/* Main Profile & Public Handles Form */}
      <form onSubmit={handleSaveProfile} className="bg-slate-900 border border-slate-800 rounded-2xl p-4 sm:p-6 space-y-6">
        <h3 className="text-sm sm:text-base font-semibold text-white uppercase tracking-wider flex items-center space-x-2">
          <Sparkles className="w-4 h-4 text-brand-400" />
          <span>Step 2: Candidate Details & Public Profiles</span>
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs sm:text-sm font-semibold text-slate-300 mb-1.5">Full Name</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 focus:border-brand-500 rounded-xl py-2.5 px-3 text-sm text-white focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs sm:text-sm font-semibold text-slate-300 mb-1.5">Phone Number</label>
            <input
              type="text"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 focus:border-brand-500 rounded-xl py-2.5 px-3 text-sm text-white focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs sm:text-sm font-semibold text-slate-300 mb-1.5 flex items-center space-x-1.5">
              <Github className="w-3.5 h-3.5 text-slate-400" />
              <span>GitHub Username</span>
            </label>
            <input
              type="text"
              value={githubUsername}
              onChange={(e) => setGithubUsername(e.target.value)}
              placeholder="e.g. torvalds"
              className="w-full bg-slate-950 border border-slate-800 focus:border-brand-500 rounded-xl py-2.5 px-3 text-sm text-white focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs sm:text-sm font-semibold text-slate-300 mb-1.5 flex items-center space-x-1.5">
              <Code2 className="w-3.5 h-3.5 text-amber-400" />
              <span>LeetCode Username</span>
            </label>
            <input
              type="text"
              value={leetcodeUsername}
              onChange={(e) => setLeetcodeUsername(e.target.value)}
              placeholder="e.g. neetcode"
              className="w-full bg-slate-950 border border-slate-800 focus:border-brand-500 rounded-xl py-2.5 px-3 text-sm text-white focus:outline-none"
            />
          </div>

          <div className="sm:col-span-2">
            <label className="block text-xs sm:text-sm font-semibold text-slate-300 mb-1.5">
              Target Engineering Roles (comma-separated)
            </label>
            <input
              type="text"
              value={targetRoles}
              onChange={(e) => setTargetRoles(e.target.value)}
              placeholder="Software Engineer, Backend Developer, SDE-1"
              className="w-full bg-slate-950 border border-slate-800 focus:border-brand-500 rounded-xl py-2.5 px-3 text-sm text-white focus:outline-none"
            />
          </div>

          <div className="sm:col-span-2">
            <label className="block text-xs sm:text-sm font-semibold text-slate-300 mb-1.5">
              Target Geographic Region / Work Mode
            </label>
            <input
              type="text"
              value={targetLocation}
              onChange={(e) => setTargetLocation(e.target.value)}
              placeholder="India (Bengaluru, Hyderabad, Pune, Remote)"
              className="w-full bg-slate-950 border border-slate-800 focus:border-brand-500 rounded-xl py-2.5 px-3 text-sm text-white focus:outline-none"
            />
          </div>
        </div>

        {/* Verified Skills Pill Box */}
        <div className="pt-4 border-t border-slate-800">
          <label className="block text-xs sm:text-sm font-semibold text-slate-300 mb-2">
            Verified Skill Vector ({skillsList.length} Skills)
          </label>
          <div className="flex flex-wrap gap-2 mb-3">
            {skillsList.map((skill) => (
              <span
                key={skill}
                className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-xs sm:text-sm text-slate-200 font-medium"
              >
                <span>{skill}</span>
                <button
                  type="button"
                  onClick={() => removeSkill(skill)}
                  className="text-slate-400 hover:text-rose-400 transition ml-1 text-base leading-none"
                >
                  ×
                </button>
              </span>
            ))}
          </div>

          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5">
            <input
              type="text"
              value={newSkill}
              onChange={(e) => setNewSkill(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill())}
              placeholder="Add skill (e.g. Redis, Kubernetes, Next.js)"
              className="bg-slate-950 border border-slate-800 focus:border-brand-500 rounded-xl py-2.5 px-3 text-xs sm:text-sm text-white focus:outline-none flex-1 max-w-full sm:max-w-xs"
            />
            <button
              type="button"
              onClick={addSkill}
              className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-750 text-slate-200 text-xs sm:text-sm font-semibold border border-slate-700 transition text-center"
            >
              Add Skill
            </button>
          </div>
        </div>

        <div className="pt-4 flex flex-col sm:flex-row justify-end">
          <button
            type="submit"
            disabled={saving}
            className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 px-6 py-3 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs sm:text-sm font-semibold shadow-lg shadow-brand-500/20 transition disabled:opacity-50 text-center"
          >
            <Save className="w-4 h-4" />
            <span>{saving ? 'Updating Signals...' : 'Save & Refresh Assessment'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};

