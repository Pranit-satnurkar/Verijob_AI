'use client';

import { useState, useEffect, useRef } from 'react';
import { submitReport, getVerifiedJobs } from './actions';

export default function Home() {
  const [url, setUrl] = useState('');
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [recentJobs, setRecentJobs] = useState<any[]>([]);
  const [searchHistory, setSearchHistory] = useState<any[]>([]);
  const resultRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getVerifiedJobs().then(setRecentJobs);
  }, []);

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) return;
    setLoading(true);
    setResult({ status: 'Analyzed', score: 0, details: 'Processing...' });

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://verijob-ai.onrender.com';
      const res = await fetch(`${apiUrl}/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, content }),
      });
      const data = await res.json();
      setResult(data);

      // Add to search history (not hiring signals feed)
      const historyEntry = {
        title: data.metadata?.title || 'Unknown Role',
        company: data.metadata?.company || 'Unknown Company',
        score: data.score,
        timestamp: new Date().toISOString(),
        url: url
      };
      setSearchHistory(prev => [historyEntry, ...prev].slice(0, 10)); // Keep last 10

      // Auto-scroll to results
      setTimeout(() => {
        resultRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 300);
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
            <img src="/logo.png" alt="VeriJob AI" className="w-8 h-8 object-contain" />
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
          <p className="text-xl text-zinc-400 max-w-2xl font-light border-l border-zinc-800 pl-6 mb-8">
            Deploy autonomous agents to verify job listing integrity. Cross-reference hiring patterns, layoff data, and metadata anomalies in real-time.
          </p>

          {/* Transparency Disclaimer */}
          <div className="mx-auto max-w-2xl mb-8 p-4 border-l-2 border-zinc-700 bg-zinc-900/30">
            <p className="text-xs text-zinc-400 leading-relaxed">
              <span className="font-mono text-zinc-300">DISCLAIMER:</span> This analysis provides a <span className="text-zinc-300">probability estimate</span>, not absolute certainty.
              We combine multiple signals (job description quality, company health, Reddit sentiment, temporal patterns) to help freshers
              identify potentially suspicious listings. Always conduct your own research before applying.
            </p>
          </div>

          {/* Extension Platform Support Notice */}
          <div className="mx-auto max-w-2xl mb-12 p-4 border border-zinc-800 bg-zinc-950">
            <p className="text-xs text-zinc-400 leading-relaxed">
              <span className="font-mono text-amber-500">⚠ EXTENSION NOTE:</span> The browser extension works on <span className="text-zinc-300">LinkedIn, Naukri, Indeed, and Internshala</span>.
              For Glassdoor jobs, please use this web app by pasting the job description or searching for the job title + company name.
            </p>
          </div>
          {/* Disclaimer */}
          <div className="max-w-2xl mb-12 border border-zinc-800 bg-zinc-950/50 p-6">
            <div className="flex items-start gap-4">
              <span className="material-symbols-outlined text-yellow-500 text-xl">info</span>
              <div>
                <h3 className="text-sm font-bold text-zinc-300 mb-2 uppercase tracking-wide">Transparency Notice</h3>
                <p className="text-sm text-zinc-400 leading-relaxed mb-3">
                  We analyze job postings using AI and public data to estimate ghost job probability. <strong className="text-zinc-300">This is not 100% accurate</strong> — use it as one signal among many when evaluating opportunities.
                </p>
                <p className="text-xs text-zinc-500 font-mono">
                  TARGET_AUDIENCE: Helping freshers avoid wasting energy on suspicious listings.
                </p>
              </div>
            </div>
          </div>
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

            <div className="mb-8">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-mono text-zinc-500 uppercase">Job Description (Optional)</span>
                <span className={`text-[10px] uppercase font-mono border px-2 py-1 tracking-widest ${content ? 'border-zinc-700 text-zinc-400 bg-zinc-900' : 'border-green-900 text-green-400 bg-green-950/30'}`}>
                  {content ? 'MANUAL_MODE' : 'AUTO_SCRAPE_ENABLED'}
                </span>
              </div>
              <textarea
                className="w-full bg-zinc-950 border-2 border-zinc-800 text-white px-6 py-4 outline-none font-mono text-sm placeholder-zinc-600 tracking-wide h-40 resize-none focus:border-zinc-600 hover:border-zinc-700 transition-all"
                placeholder="Paste job description here or leave empty to auto-scrape from URL..."
                value={content}
                onChange={(e) => setContent(e.target.value)}
              />
            </div>

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
          <div ref={resultRef} className="mb-24 border border-zinc-800 bg-zinc-950 p-8">
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

                {/* Detection Methodology */}
                <div className="mt-6 pt-6 border-t border-zinc-800">
                  <div className="text-xs font-mono text-zinc-500 uppercase mb-3">Detection Signals</div>
                  <div className="space-y-2 text-xs font-mono">
                    <div className="flex items-center gap-2">
                      <span className="text-green-500">✓</span>
                      <span className="text-zinc-400">JD Quality Analysis (AI-gen detection)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-green-500">✓</span>
                      <span className="text-zinc-400">Company Health Check (layoffs, news)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-green-500">✓</span>
                      <span className="text-zinc-400">Reddit Sentiment Analysis</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-green-500">✓</span>
                      <span className="text-zinc-400">Temporal Analysis (stale listings)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-yellow-500">⚠</span>
                      <span className="text-zinc-500">LinkedIn Signals (limited access)</span>
                    </div>
                  </div>
                </div>
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

        {/* Search History */}
        {searchHistory.length > 0 && (
          <div className="mb-16">
            <h3 className="font-mono text-sm uppercase text-zinc-500 mb-6">Your Search History</h3>
            <div className="border border-zinc-800 bg-zinc-950">
              {searchHistory.map((item, i) => (
                <div
                  key={i}
                  className="p-4 border-b border-zinc-800 last:border-b-0 hover:bg-zinc-900 transition-colors flex items-center justify-between gap-4"
                >
                  <div className="flex-1 min-w-0">
                    <div className="font-bold text-sm text-zinc-200 truncate">{item.title}</div>
                    <div className="font-mono text-xs text-zinc-500 truncate">{item.company}</div>
                    <div className="font-mono text-[10px] text-zinc-600 mt-1">
                      {new Date(item.timestamp).toLocaleString()}
                    </div>
                  </div>
                  <div className="flex items-center gap-4 flex-shrink-0">
                    <div className={`text-2xl font-black ${item.score > 70 ? 'text-white' : 'text-zinc-600'}`}>
                      {item.score}
                    </div>
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-zinc-500 hover:text-white transition-colors"
                    >
                      <span className="material-symbols-outlined text-sm">open_in_new</span>
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Active Feed */}
        <div className="border-t border-zinc-800 pt-12">
          <h3 className="font-mono text-sm uppercase text-zinc-500 mb-8">Verified Hiring Signals</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-0 border border-zinc-800">
            {recentJobs.slice(0, 9).map((signal, i) => (
              <a
                key={i}
                href={signal.url || '#'}
                target="_blank"
                rel="noopener noreferrer"
                className="p-6 border-b md:border-b-0 md:border-r border-zinc-800 hover:bg-zinc-900 transition-colors group block h-full flex flex-col justify-between"
              >
                <div>
                  <div className="flex justify-between items-start mb-4">
                    <span className={`font-mono text-[10px] px-2 py-0.5 border uppercase tracking-wider ${signal.type === 'FUNDING' ? 'border-green-900 text-green-400' :
                      signal.type === 'INTERVIEWS' ? 'border-purple-900 text-purple-400' :
                        'border-blue-900 text-blue-400'
                      }`}>
                      {signal.type || 'SIGNAL'}
                    </span>
                    <span className="material-symbols-outlined text-zinc-600 text-sm group-hover:text-white transition-colors">arrow_outward</span>
                  </div>
                  <div className="font-bold text-sm mb-2 line-clamp-3 leading-snug text-zinc-200 group-hover:text-white">
                    {signal.title}
                  </div>
                </div>
                <div className="font-mono text-xs text-zinc-500 mt-4 border-t border-zinc-800 pt-3 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-zinc-700"></span>
                  {signal.company}
                </div>
              </a>
            ))}

            {recentJobs.length === 0 && (
              <div className="p-6 col-span-3 text-center font-mono text-xs text-zinc-600">
                WAITING FOR INTEL FEED...
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
