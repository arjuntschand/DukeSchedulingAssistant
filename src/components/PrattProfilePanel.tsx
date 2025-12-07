import React from 'react';
import type { PrattProfile } from '../types';

const PRATT_MAJORS = ['Biomedical Engineering', 'Civil Engineering', 'Electrical & Computer Engineering', 'Mechanical Engineering', 'Environmental Engineering'];

const CLASS_YEARS = ['2026', '2027', '2028', '2029'];

const SEMESTERS = ['Fall 2025', 'Spring 2026', 'Fall 2026', 'Spring 2027'];

interface PrattProfilePanelProps {
  profile: PrattProfile;
  onChange: (profile: PrattProfile) => void;
}

export const PrattProfilePanel: React.FC<PrattProfilePanelProps> = ({ profile, onChange }) => {
  const updateField = <K extends keyof PrattProfile>(key: K, value: PrattProfile[K]) => {
    onChange({ ...profile, [key]: value });
  };

  const handleTextAreaListChange = (key: 'currentCourses' | 'completedCourses', value: string) => {
    const items = value
      .split(/[,\n]/)
      .map((v) => v.trim())
      .filter(Boolean);
    updateField(key, items as PrattProfile[typeof key]);
  };

  return (
    <section className="border border-slate-200 rounded-3xl bg-white shadow-[0_10px_30px_rgba(15,23,42,0.06)] px-5 py-4 mb-2">
      <details open className="group">
        <summary className="flex items-center justify-between cursor-pointer select-none">
          <div>
            <h2 className="text-base font-semibold text-slate-900">Your Pratt Profile</h2>
            <p className="text-xs text-slate-600">
              This information will be sent with your questions to improve degree-planning answers.
            </p>
          </div>
          <span className="ml-3 text-[11px] text-slate-500 group-open:hidden">Show</span>
          <span className="ml-3 text-[11px] text-slate-500 hidden group-open:inline">Hide</span>
        </summary>

        <div className="mt-3 grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div className="space-y-1.5">
            <label className="font-semibold text-slate-800" htmlFor="major">
              Major
            </label>
            <select
              id="major"
              value={profile.major}
              onChange={(e) => updateField('major', e.target.value)}
              className="w-full rounded-md border border-slate-300 bg-white px-2.5 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-dukeBlue/70 focus:border-dukeBlue/70"
            >
              <option value="">Select your Pratt major</option>
              {PRATT_MAJORS.map((major) => (
                <option key={major} value={major}>
                  {major}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-1.5">
            <label className="font-semibold text-slate-800" htmlFor="classYear">
              Class year
            </label>
            <select
              id="classYear"
              value={profile.classYear}
              onChange={(e) => updateField('classYear', e.target.value)}
              className="w-full rounded-md border border-slate-300 bg-white px-2.5 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-dukeBlue/70 focus:border-dukeBlue/70"
            >
              <option value="">Select</option>
              {CLASS_YEARS.map((year) => (
                <option key={year} value={year}>
                  {year}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-1.5">
            <label className="font-semibold text-slate-800" htmlFor="semester">
              Current / target semester
            </label>
            <select
              id="semester"
              value={profile.semester}
              onChange={(e) => updateField('semester', e.target.value)}
              className="w-full rounded-md border border-slate-300 bg-white px-2.5 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-dukeBlue/70 focus:border-dukeBlue/70"
            >
              <option value="">Select semester</option>
              {SEMESTERS.map((sem) => (
                <option key={sem} value={sem}>
                  {sem}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div className="space-y-1.5">
            <label className="font-semibold text-slate-800" htmlFor="currentCourses">
              Current classes (course codes)
            </label>
            <textarea
              id="currentCourses"
              rows={3}
              defaultValue={profile.currentCourses.join(', ')}
              onBlur={(e) => handleTextAreaListChange('currentCourses', e.target.value)}
              placeholder="ECE 110L, MATH 218D, CHEM 101DL"
              className="w-full rounded-md border border-slate-300 bg-white px-2.5 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-dukeBlue/70 focus:border-dukeBlue/70 resize-none"
            />
          </div>

          <div className="space-y-1.5">
            <label className="font-semibold text-slate-800" htmlFor="completedCourses">
              Completed core / prerequisite courses
            </label>
            <textarea
              id="completedCourses"
              rows={3}
              defaultValue={profile.completedCourses.join(', ')}
              onBlur={(e) => handleTextAreaListChange('completedCourses', e.target.value)}
              placeholder="ECE 250D, MATH 353, PHYSICS 152L"
              className="w-full rounded-md border border-slate-300 bg-white px-2.5 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-dukeBlue/70 focus:border-dukeBlue/70 resize-none"
            />
          </div>
        </div>
      </details>
    </section>
  );
};
