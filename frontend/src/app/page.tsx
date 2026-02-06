'use client';

import { useState, useEffect } from 'react';
import { submitReport, getVerifiedJobs } from './actions';

export default function Home() {
  const [url, setUrl] = useState('');
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [recentJobs, setRecentJobs] = useState<any[]>([]);

  useEffect(() => {
    getVerifiedJobs().then(setRecentJobs);
  }, []);

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) return;
    setLoading(true);
    setResult(null);

    try {
      const res = await fetch('http://localhost:8000/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, content }),
      });
      const data = await res.json();
      setResult(data);

      // Update feed locally
      const newJob = {
        title: data.metadata?.title || 'Unknown Role',
        company: data.metadata?.company || 'Unknown Company',
        score: data.score
      };
      setRecentJobs(prev => [newJob, ...prev]);
    } catch (error) {
      setResult({ status: 'Error', details: 'Connection Failed' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-black text-zinc-100 font-sans selection:bg-zinc-800 selection:text-white">
      {/* Header */}
      <header className="border-b border-zinc-800 sticky top-0 bg-black z-50">
        <div className="max-w-screen-xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 font-mono text-sm tracking-tighter">
            <span className="w-3 h-3 bg-zinc-100"></span>
            VERIJOB_AI // V1.0
          </div>
          <div className="flex items-center gap-6">
            <a
              href="/verijob-extension.zip"
              download="verijob-extension.zip"
              className="text-xs font-bold border border-white px-4 py-2 hover:bg-white hover:text-black transition-colors uppercase"
            >
              Get Extension
            </a>
            <div className="text-xs font-mono text-zinc-500 hidden md:block">
              SYSTEM_STATUS: ONLINE
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-screen-xl mx-auto px-6 py-12">
        {/* Hero */}
        <div className="max-w-4xl">
          <h1 className="text-6xl md:text-8xl font-black tracking-tighter mb-6 text-white">
            STOP APPLYING<br />TO GHOST JOBS.
          </h1>
          <p className="text-xl text-zinc-400 max-w-2xl font-light border-l border-zinc-800 pl-6 mb-12">
            Deploy autonomous agents to verify job listing integrity. Cross-reference hiring patterns, layoff data, and metadata anomalies in real-time.
          </p>
        </div>

        {/* Input Terminal */}
        <div className="w-full max-w-2xl mb-24">
          <form onSubmit={handleVerify} className="flex flex-col gap-4">
            <div className="flex flex-col md:flex-row gap-0 border border-zinc-800">
              <div className="bg-zinc-900 px-4 py-4 flex items-center justify-center border-r border-zinc-800">
                <span className="material-symbols-outlined text-zinc-500">terminal</span>
              </div>
              <input
                type="url"
                className="flex-1 bg-black text-white px-6 py-4 outline-none font-mono text-sm placeholder-zinc-600 tracking-wide"
                placeholder="ENTER_JOB_URL_HERE..."
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                required
              />
            </div>

            <textarea
              className="w-full bg-black border border-zinc-800 text-white px-6 py-4 outline-none font-mono text-sm placeholder-zinc-600 tracking-wide h-32"
              placeholder="PASTE_JOB_DESCRIPTION_TEXT_HERE (OPTIONAL_BUT_RECOMMENDED_FOR_LINKEDIN_INDEED)..."
              value={content}
              onChange={(e) => setContent(e.target.value)}
            />

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-white text-black px-8 py-4 font-bold text-sm hover:bg-zinc-200 transition-colors border border-zinc-800 uppercase tracking-widest"
            >
              {loading ? 'PROCESSING...' : 'INITIATE SCAN'}
            </button>
          </form>
        </div>

        {/* Results Display */}
        {result && (
          <div className="mb-24 border border-zinc-800 bg-zinc-950 p-8">
            <div className="flex flex-col md:flex-row justify-between items-start gap-8 mb-8 border-b border-zinc-800 pb-8">
              <div>
                <div className="text-xs font-mono text-zinc-500 uppercase mb-2">Target Identifier</div>
                <h2 className="text-2xl font-bold">{result.metadata?.title || 'UNKNOWN_ROLE'}</h2>
                <div className="font-mono text-zinc-400">{result.metadata?.company || 'UNKNOWN_ENTITY'}</div>
              </div>
              <div className="text-right">
                <div className="text-xs font-mono text-zinc-500 uppercase mb-2">Integrity Score</div>
                <div className={`text-6xl font-black tracking-tighter ${result.score > 70 ? 'text-white' : 'text-zinc-600'}`}>
                  {result.score}<span className="text-2xl text-zinc-600">/100</span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <div className="text-xs font-mono text-zinc-500 uppercase mb-4">Analysis Log</div>
                <p className="font-mono text-sm text-zinc-300 leading-relaxed border-l-2 border-zinc-800 pl-4">
                  {result.details}
                </p>
              </div>
              <div>
                <div className="text-xs font-mono text-zinc-500 uppercase mb-4">Intelligence Feed</div>
                <div className="bg-zinc-900 p-4 font-mono text-xs text-zinc-400 overflow-x-auto whitespace-pre-wrap h-32 border border-zinc-800 mb-4">
                  {'>'} HEALTH_CHECK_INIT...
                  {result.health_insights ? `\n> ${result.health_insights}` : '\n> NO_SIGNALS_DETECTED'}
                  {'\n> END_TRANSMISSION'}
                </div>

                {result.references && result.references.length > 0 && (
                  <div>
                    <div className="text-xs font-mono text-zinc-500 uppercase mb-3">Verified Sources</div>
                    <div className="grid grid-cols-1 gap-2">
                      {result.references.map((ref: any, idx: number) => {
                        const isReddit = ref.url.includes('reddit.com');
                        const icon = isReddit ? 'forum' : 'newspaper';

                        return (
                          <a
                            key={idx}
                            href={ref.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-start gap-3 p-3 bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 hover:border-zinc-700 transition-all group"
                          >
                            <span className="material-symbols-outlined text-zinc-500 text-lg group-hover:text-indigo-400 mt-0.5">
                              {icon}
                            </span>
                            <div className="overflow-hidden">
                              <div className="text-xs font-bold text-zinc-300 truncate group-hover:text-indigo-300">
                                {ref.title || 'Source Link'}
                              </div>
                              <div className="text-[10px] font-mono text-zinc-600 truncate mt-0.5">
                                {new URL(ref.url).hostname}
                              </div>
                            </div>
                          </a>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Active Feed */}
        <div className="border-t border-zinc-800 pt-12">
          <h3 className="font-mono text-sm uppercase text-zinc-500 mb-8">Verified_Feed_Stream</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-0 border border-zinc-800">
            {recentJobs.slice(0, 6).map((job, i) => (
              <div key={i} className="p-6 border-b md:border-b-0 md:border-r border-zinc-800 hover:bg-zinc-900 transition-colors group">
                <div className="flex justify-between items-start mb-4">
                  <span className={`font-mono text-xs px-2 py-0.5 border ${job.score > 70 ? 'border-zinc-600 text-zinc-300' : 'border-zinc-800 text-zinc-600'}`}>
                    SCORE: {job.score}
                  </span>
                  <span className="material-symbols-outlined text-zinc-600 text-sm group-hover:text-white transition-colors">arrow_outward</span>
                </div>
                <div className="font-bold text-lg mb-1">{job.title}</div>
                <div className="font-mono text-xs text-zinc-500">{job.company}</div>
              </div>
            ))}
            {recentJobs.length === 0 && (
              <div className="p-6 col-span-3 text-center font-mono text-xs text-zinc-600">
                WAITING FOR DATA STREAM...
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
