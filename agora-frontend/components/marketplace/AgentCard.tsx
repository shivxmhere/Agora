"use client";

import { motion } from 'framer-motion';
import Link from 'next/link';
import { Agent } from '@/lib/types';
import { StarRating } from '@/components/shared/StarRating';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { CreatorScore } from '@/components/shared/CreatorScore';

export function AgentCard({ agent, delay = 0 }: { agent: Agent; delay?: number }) {
  // Category colors logic
  const getCatColor = (cat: string) => {
    if (cat === 'Research') return 'text-purple border-purple';
    if (cat === 'Developer Tools') return 'text-cyan border-cyan';
    if (cat === 'Business') return 'text-orange border-orange';
    if (cat === 'Analytics') return 'text-lime border-lime';
    return 'text-muted border-muted';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      whileHover={{ y: -5, boxShadow: '0 0 20px rgba(0, 245, 255, 0.2)' }}
      className="bg-card border border-border flex flex-col group transition-colors duration-300 hover:border-cyan p-5 h-full rounded-sm relative overflow-hidden"
    >
      <div className="flex justify-between items-start mb-4">
        <div className={`px-2 py-0.5 text-[10px] uppercase font-mono border rounded-sm ${getCatColor(agent.category)}`}>
          {agent.category}
        </div>
        <StatusBadge status={agent.status} />
      </div>

      <div className="flex gap-4 items-center mb-4">
        <div className="w-12 h-12 flex-shrink-0 flex items-center justify-center bg-elevated border border-border rounded-sm">
          <span className="font-display text-2xl text-cyan">{agent.name.charAt(0)}</span>
        </div>
        <div>
          <h3 className="font-mono text-lg text-primary leading-tight">{agent.name}</h3>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-xs text-muted">by {agent.creator_name}</span>
            <CreatorScore score={agent.creator_score} />
          </div>
        </div>
      </div>

      <p className="text-sm text-dim mb-6 line-clamp-2 flex-grow">{agent.tagline}</p>

      <div className="flex flex-wrap gap-2 mb-6">
        <div className="bg-elevated px-2 py-1 flex items-center rounded-sm">
          <StarRating rating={agent.rating} />
        </div>
        <div className="bg-elevated px-2 py-1 text-xs font-mono text-muted flex items-center rounded-sm">
          {agent.total_runs.toLocaleString()} runs
        </div>
        <div className="bg-elevated px-2 py-1 text-xs font-mono text-muted flex items-center rounded-sm">
          {agent.avg_run_time}s avg
        </div>
      </div>

      <Link href={`/agent/${agent.id}`} className="mt-auto">
        <div className="w-full py-2 border border-border text-center font-mono text-sm text-primary group-hover:bg-cyan group-hover:text-void group-hover:border-cyan transition-colors duration-300 rounded-sm">
          Run Now →
        </div>
      </Link>
    </motion.div>
  );
}
