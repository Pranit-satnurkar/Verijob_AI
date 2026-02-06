'use client';

import { Suspense, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';

function DashboardContent() {
    const searchParams = useSearchParams();
    const initialUrl = searchParams.get('url');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<any>(null);

    useEffect(() => {
        if (initialUrl) handleAnalyze(initialUrl);
    }, [initialUrl]);

    const handleAnalyze = async (targetUrl: string) => {
        setLoading(true);
        try {
            const res = await fetch('http://localhost:8000/verify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: targetUrl }),
            });
            const data = await res.json();
            setResult(data);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-black text-white font-sans flex flex-col">
            <header className="h-16 border-b border-zinc-800 flex items-center px-6 justify-between bg-black">
                <div className="font-mono font-bold tracking-tighter">GHOST_BUSTER_DASHBOARD</div>
                <div className="text-xs font-mono text-zinc-500">{loading ? 'STATUS: PROCESSING' : 'STATUS: IDLE'}</div>
            </header>

            <main className="flex-1 p-6 md:p-12 overflow-y-auto">
                {result ? (
                    <div className="max-w-6xl mx-auto grid grid-cols-12 gap-6">
                        {/* Score Panel */}
                        <div className="col-span-12 md:col-span-4 border border-zinc-800 p-8 flex flex-col justify-between h-96">
                            <div>
                                <div className="text-xs font-mono text-zinc-500 uppercase tracking-widest mb-2">Verification Index</div>
                                <div className="text-9xl font-black tracking-tighter leading-none">
                                    {result.score}
                                </div>
                            </div>
                            <div className="border-t border-zinc-800 pt-4">
                                <div className="flex justify-between items-center mb-2">
                                    <span className="text-xs font-mono text-zinc-400">THRESHOLD</span>
                                    <span className="text-xs font-mono text-zinc-400">70/100</span>
                                </div>
                                <div className="w-full h-2 bg-zinc-900">
                                    <div className="h-full bg-white" style={{ width: `${result.score}%` }}></div>
                                </div>
                            </div>
                        </div>

                        {/* Metadata Grid */}
                        <div className="col-span-12 md:col-span-8 grid grid-cols-2 gap-6">
                            <div className="col-span-2 border border-zinc-800 p-6">
                                <div className="text-xs font-mono text-zinc-500 uppercase mb-4">Target Metadata</div>
                                <div className="grid grid-cols-2 gap-8">
                                    <div>
                                        <div className="text-xs text-zinc-600 mb-1">ROLE</div>
                                        <div className="font-bold text-xl">{result.metadata?.title || 'N/A'}</div>
                                    </div>
                                    <div>
                                        <div className="text-xs text-zinc-600 mb-1">ENTITY</div>
                                        <div className="font-bold text-xl">{result.metadata?.company || 'N/A'}</div>
                                    </div>
                                    <div>
                                        <div className="text-xs text-zinc-600 mb-1">LOCATION</div>
                                        <div className="font-mono text-sm">{result.metadata?.location || 'N/A'}</div>
                                    </div>
                                    <div>
                                        <div className="text-xs text-zinc-600 mb-1">SOURCE</div>
                                        <div className="font-mono text-sm">{result.metadata?.source || 'WEB_SCRAPER'}</div>
                                    </div>
                                </div>
                            </div>

                            <div className="col-span-2 md:col-span-1 border border-zinc-800 p-6 overflow-y-auto h-48">
                                <div className="text-xs font-mono text-zinc-500 uppercase mb-4">Analysis Vector</div>
                                <p className="text-sm text-zinc-300 font-mono leading-relaxed text-xs">
                                    {result.details}
                                </p>
                            </div>

                            <div className="col-span-2 md:col-span-1 border border-zinc-800 p-6 overflow-y-auto h-48">
                                <div className="text-xs font-mono text-zinc-500 uppercase mb-4">RAG Signals</div>
                                <p className="text-sm text-zinc-300 font-mono text-xs whitespace-pre-wrap">
                                    {result.health_insights || 'NO_DATA_AVAILABLE'}
                                </p>
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="h-full flex flex-col items-center justify-center text-zinc-600 font-mono">
                        <span className="material-symbols-outlined text-4xl mb-4">grid_view</span>
                        <div>NO_ACTIVE_TARGET_SELECTED</div>
                    </div>
                )}
            </main>
        </div>
    );
}

export default function DashboardPage() {
    return (
        <Suspense fallback={<div className="bg-black h-screen text-white p-12 font-mono">LOADING_MODULES...</div>}>
            <DashboardContent />
        </Suspense>
    );
}
