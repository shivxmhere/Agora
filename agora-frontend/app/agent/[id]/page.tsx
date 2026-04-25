"use client";

import { useState, useRef, useEffect } from 'react';
import { useAgent } from '@/hooks/useAgents';
import { api } from '@/lib/api';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { StarRating } from '@/components/shared/StarRating';
import { CreatorScore } from '@/components/shared/CreatorScore';
import { Play } from 'lucide-react';
import { useParams } from 'next/navigation';

export default function AgentPage() {
  const params = useParams();
  const id = params.id as string;
  const { agent, isLoading } = useAgent(id);

  const [input, setInput] = useState('');
  const [output, setOutput] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState('');
  const [runStats, setRunStats] = useState<{time: number} | null>(null);
  
  const endOfOutputRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endOfOutputRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [output]);

  if (isLoading) return <div className="p-20 text-center animate-pulse">Loading agent profile...</div>;
  if (!agent) return <div className="p-20 text-center">Agent not found.</div>;

  const handleRun = async () => {
    if (!input.trim() || isRunning) return;
    
    setIsRunning(true);
    setOutput('');
    setError('');
    setRunStats(null);
    
    try {
      const sessionId = Math.random().toString(36).substring(7);
      const res = await api.runAgent(id, input, sessionId);
      
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
      const eventSource = new EventSource(`${backendUrl}${res.stream_url}`);
      
      eventSource.onmessage = (e) => {
        const data = JSON.parse(e.data);
        if (data.type === 'token') {
          setOutput(prev => prev + data.content);
        } else if (data.type === 'done') {
          setRunStats({ time: data.run_time });
          setIsRunning(false);
          eventSource.close();
        } else if (data.type === 'error') {
          setError(data.message);
          setIsRunning(false);
          eventSource.close();
        }
      };
      
      eventSource.onerror = (err) => {
        console.error("SSE Error:", err);
        setError("Connection lost or stream failed.");
        setIsRunning(false);
        eventSource.close();
      };
    } catch (err: any) {
      setError(err.message || "Failed to start run.");
      setIsRunning(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Agent Header */}
      <div className="bg-card border border-border p-8 rounded-sm mb-8 flex flex-col md:flex-row gap-8 items-start relative overflow-hidden">
        <div className="absolute top-0 right-0 p-8 opacity-5 font-display text-[200px] leading-none pointer-events-none select-none">
          {agent.name.charAt(0)}
        </div>
        
        <div className="w-24 h-24 bg-elevated border border-cyan/50 rounded-sm flex items-center justify-center flex-shrink-0 z-10 box-shadow-glow">
          <span className="font-display font-bold text-5xl text-cyan">{agent.name.charAt(0)}</span>
        </div>
        
        <div className="flex-1 z-10 w-full">
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-4 mb-4">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <StatusBadge status={agent.status} />
                <span className="text-muted font-mono text-xs uppercase border border-border px-2 py-0.5 rounded-sm">{agent.category}</span>
              </div>
              <h1 className="font-display text-4xl font-bold text-primary">{agent.name}</h1>
              <div className="flex items-center gap-2 mt-2">
                <span className="font-mono text-sm text-dim">Created by {agent.creator_name}</span>
                <CreatorScore score={agent.creator_score} />
              </div>
            </div>
            
            <div className="flex gap-4">
              <div className="flex flex-col items-end">
                <span className="text-xs font-mono text-muted">RATING</span>
                <StarRating rating={agent.rating} className="mt-1" />
              </div>
              <div className="flex flex-col items-end">
                <span className="text-xs font-mono text-muted">RUNS</span>
                <span className="font-mono text-primary mt-1">{agent.total_runs.toLocaleString()}</span>
              </div>
              <div className="flex flex-col items-end">
                <span className="text-xs font-mono text-muted">AVG TIME</span>
                <span className="font-mono text-primary mt-1">{agent.avg_run_time}s</span>
              </div>
            </div>
          </div>
          
          <p className="text-muted max-w-3xl leading-relaxed mb-6">{agent.long_description || agent.description}</p>
          
          <div className="flex flex-wrap gap-2">
            {agent.capabilities?.map((cap, i) => (
              <span key={i} className="text-xs font-mono bg-elevated border border-border px-3 py-1 rounded-sm text-cyan">{cap}</span>
            ))}
          </div>
        </div>
      </div>

      {/* Execution Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-20">
        {/* Input panel */}
        <div className="lg:col-span-1 flex flex-col gap-4">
          <div className="bg-card border border-border p-6 rounded-sm h-full flex flex-col">
            <h3 className="font-mono font-bold text-primary mb-4 flex items-center gap-2">
              <span className="text-cyan">_</span>INPUT_PARAMETERS
            </h3>
            
            <textarea
              value={input}
              onChange={e => setInput(e.target.value)}
              className="w-full flex-grow min-h-[200px] bg-elevated border border-border p-4 rounded-sm text-primary font-mono text-sm focus:border-cyan focus:ring-1 focus:ring-cyan outline-none resize-none mb-6"
              placeholder={agent.input_placeholder || "Enter input parameters here..."}
            />
            
            <button
              onClick={handleRun}
              disabled={isRunning || !input.trim()}
              className="w-full bg-cyan text-void font-bold font-mono py-4 flex items-center justify-center gap-2 rounded-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-transparent hover:text-cyan hover:border-cyan border border-cyan transition-all"
            >
              {isRunning ? (
                <>
                  <div className="w-4 h-4 rounded-full border-2 border-t-transparent border-void animate-spin" />
                  EXECUTING...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-current" />
                  INITIALIZE RUN
                </>
              )}
            </button>
          </div>
        </div>
        
        {/* Output Terminal */}
        <div className="lg:col-span-2">
          <div className="bg-[#050508] border border-border rounded-sm h-[600px] flex flex-col overflow-hidden relative shadow-[0_0_30px_rgba(0,0,0,0.5)]">
            <div className="px-4 py-2 border-b border-border bg-[#0a0a10] flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-500/50" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500/50" />
                  <div className="w-3 h-3 rounded-full bg-green-500/50" />
                </div>
                <span className="font-mono text-xs text-muted ml-4">agora_terminal ~ {agent.slug}.sh</span>
              </div>
              <span className="font-mono text-xs text-cyan animate-pulse">
                {isRunning ? 'STATUS: ACTIVE' : 'STATUS: IDLE'}
              </span>
            </div>
            
            <div className="p-6 overflow-y-auto flex-1 font-mono text-sm text-primary whitespace-pre-wrap">
              {!output && !isRunning && !error && (
                <span className="text-dim">Waiting for input... System ready.</span>
              )}
              {output}
              {isRunning && (
                <span className="inline-block w-2 h-4 bg-cyan animate-pulse ml-1 align-middle" />
              )}
              {error && (
                <div className="text-red-500 mt-4 border border-red-500/30 bg-red-500/10 p-4 rounded-sm">
                  [SYSTEM_ERROR]: {error}
                </div>
              )}
              {runStats && (
                <div className="text-lime mt-8 border-t border-dashed border-border pt-4">
                  [PROCESS_COMPLETE] Output generated in {runStats.time.toFixed(2)}s
                </div>
              )}
              <div ref={endOfOutputRef} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
