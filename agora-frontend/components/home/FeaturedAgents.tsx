"use client";

import { useAgents } from '@/hooks/useAgents';
import { AgentCard } from '@/components/marketplace/AgentCard';

export function FeaturedAgents() {
  const { agents, isLoading } = useAgents({ sort: 'rating' });

  // Get top 4 agents
  const topAgents = agents?.slice(0, 4) || [];

  return (
    <div className="w-full">
      <div className="flex justify-between items-end mb-6">
        <div>
          <h2 className="font-display text-2xl font-bold text-primary">Featured Agents</h2>
          <p className="font-mono text-sm text-muted mt-1">Highest rated on the network.</p>
        </div>
      </div>
      
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="h-64 bg-elevated animate-shimmer rounded-sm border border-border" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {topAgents.map((agent, i) => (
            <AgentCard key={agent.id} agent={agent} delay={i * 0.1} />
          ))}
        </div>
      )}
    </div>
  );
}
