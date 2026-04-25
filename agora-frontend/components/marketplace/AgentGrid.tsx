import { Agent } from '@/lib/types';
import { AgentCard } from './AgentCard';

export function AgentGrid({ agents, isLoading }: { agents?: Agent[], isLoading: boolean }) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div key={i} className="h-64 bg-elevated animate-shimmer rounded-sm border border-border"></div>
        ))}
      </div>
    );
  }

  if (!agents || agents.length === 0) {
    return (
      <div className="py-20 text-center flex flex-col items-center">
        <span className="text-4xl mb-4">🤖</span>
        <h3 className="font-mono text-xl text-primary mb-2">No agents found</h3>
        <p className="text-muted">Try a different search or category.</p>
      </div>
    );
  }

  return (
    <div>
      <p className="text-sm text-muted font-mono mb-6">Showing {agents.length} agents</p>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {agents.map((agent, i) => (
          <AgentCard key={agent.id} agent={agent} delay={i * 0.05} />
        ))}
      </div>
    </div>
  );
}
