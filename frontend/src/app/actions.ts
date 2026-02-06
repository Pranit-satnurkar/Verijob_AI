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
    // For demo/dev mode without Supabase, return mock data
    const mockData = [
        { title: "Senior Data Scientist", company: "Meta Platforms", score: 92 },
        { title: "Entry Level QA Tester", company: "Unknown Agency", score: 15 },
        { title: "Marketing Manager", company: "Netflix", score: 88 },
        { title: "Remote Data Entry", company: "Global Services Inc", score: 5 },
    ];

    if (!supabase) return mockData;

    try {
        const { data, error } = await supabase
            .from('verified_jobs')
            .select('*')
            .order('created_at', { ascending: false })
            .limit(5);

        if (error || !data || data.length === 0) {
            return mockData; // Fallback to mock if DB is empty or fails
        }
        return data;
    } catch (e) {
        return mockData;
    }
}
