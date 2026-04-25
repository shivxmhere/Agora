"use client";

import useSWR from 'swr';
import { api } from '@/lib/api';
import { motion } from 'framer-motion';
import { Zap, Briefcase, TrendingUp } from 'lucide-react';
import Link from 'next/link';

export function Leaderboard() {
  const { data, isLoading } = useSWR('leaderboard', api.getLeaderboard);

  if (isLoading) return <div className="h-40 bg-elevated animate-pulse border border-border mt-12"></div>;

  return (
    <div className="mt-20 w-full">
      <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
        <h2 className="font-display text-2xl font-bold text-primary mb-1">Top Creators</h2>
        <p className="font-mono text-sm text-muted mb-6">The masterminds behind the network.</p>

        <div className="flex overflow-x-auto gap-6 pb-4 no-scrollbar">
          {data?.map((creator: any, idx: number) => (
            <Link key={idx} href={`/dashboard?creator=${creator.creator_name}`}>
              <div className="min-w-[280px] bg-card border border-border hover:border-cyan transition-colors p-5 shadow-[0_0_15px_rgba(0,0,0,0.2)] flex flex-col group cursor-pointer">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 flex items-center justify-center font-display text-2xl font-bold text-void" style={{ backgroundColor: ['#00F5FF', '#7B2FBE', '#A8FF3E', '#FF6B35', '#F0F0FF'][idx % 5]}}>
                    {creator.creator_name.charAt(0).toUpperCase()}
                  </div>
                  <div className="text-right">
                    <div className="text-[10px] font-mono text-muted">RANK</div>
                    <div className="font-display text-xl text-primary font-bold">#{idx + 1}</div>
                  </div>
                </div>
                
                <h3 className="font-mono text-lg text-primary truncate max-w-full group-hover:text-cyan transition-colors">{creator.creator_name}</h3>
                
                <div className="flex items-center gap-1 bg-cyan/10 border border-cyan/30 text-cyan text-[10px] w-max px-2 py-0.5 mt-2 mb-4">
                  <Zap className="w-3 h-3 fill-cyan" /> SCORE: {creator.creator_score.toFixed(1)}
                </div>

                <div className="mt-auto border-t border-border pt-4 flex justify-between font-mono text-xs">
                  <div className="flex flex-col gap-1">
                    <span className="text-muted flex items-center gap-1"><Briefcase className="w-3 h-3"/> AGENTS</span>
                    <span className="text-primary">{creator.total_agents}</span>
                  </div>
                  <div className="flex flex-col gap-1 text-right">
                    <span className="text-muted flex items-center gap-1 justify-end"><TrendingUp className="w-3 h-3"/> RUNS</span>
                    <span className="text-lime">{creator.total_runs.toLocaleString()}</span>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
