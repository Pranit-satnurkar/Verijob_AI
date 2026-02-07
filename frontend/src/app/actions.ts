'use server';

import { supabase } from '@/lib/supabaseClient';

export async function submitReport(url: string, reason: string, details: string) {
    if (!supabase) return { error: 'Database not connected' };

    const { error } = await supabase
        .from('reports')
        .insert([
            { job_url: url, reason, details },
        ]);

    if (error) {
        console.error('Supabase Error:', error);
        return { error: 'Failed to submit report.' };
    }

    return { success: true };
}


export async function getVerifiedJobs() {
    const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'https://verijob-ai.onrender.com';

    // 1. Try Supabase first (Stored verified jobs)
    if (supabase) {
        try {
            const { data, error } = await supabase
                .from('verified_jobs')
                .select('*')
                .order('created_at', { ascending: false })
                .limit(5);

            if (!error && data && data.length > 0) {
                return data;
            }
        } catch (e) {
            console.error("Supabase fetch error:", e);
        }
    }

    // 2. Fallback to Live Feed from Backend
    try {
        console.log(`Fetching feed from ${BACKEND_URL}/feed`);
        const res = await fetch(`${BACKEND_URL}/feed`, { next: { revalidate: 3600 } });
        if (!res.ok) throw new Error('Feed fetch failed');
        const feedData = await res.json();
        return feedData;
    } catch (e) {
        console.error("Feed fetch error:", e);
        return []; // Return empty if everything fails
    }
}

