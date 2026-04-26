"use client";

import { useState, useRef, useEffect } from 'react';
import { useAgent } from '@/hooks/useAgents';
import { api } from '@/lib/api';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { CreatorScore } from '@/components/shared/CreatorScore';
import { Rocket, Copy, CheckCircle2, ChevronRight, User, Hash, Play, Terminal, Zap, Star, Calendar, Tag } from 'lucide-react';
import { useParams, useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import ReactMarkdown from 'react-markdown';

export default function AgentDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;
  const { agent, isLoading } = useAgent(id);

  const [activeTab, setActiveTab] = useState<'overview' | 'try' | 'reviews' | 'api'>('overview');
  const [input, setInput] = useState('');
  const [output, setOutput] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState('');
  const [runStats, setRunStats] = useState<{time: number} | null>(null);
  const [copiedUrl, setCopiedUrl] = useState(false);
  
  const endOfOutputRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endOfOutputRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [output]);

  if (isLoading) return <div className="min-h-screen pt-24 px-4 text-center font-mono animate-pulse text-cyan">Initializing agent neural pathways...</div>;
  if (!agent) return <div className="min-h-screen pt-24 px-4 text-center font-mono">Entity not found in AGORA registry.</div>;

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
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* 1. BREADCRUMB */}
      <nav className="flex items-center gap-2 font-mono text-xs text-muted mb-8">
        <Link href="/marketplace" className="hover:text-cyan transition-colors">Marketplace</Link>
        <ChevronRight className="w-3 h-3" />
        <Link href={`/marketplace?category=${agent.category}`} className="hover:text-cyan transition-colors">{agent.category}</Link>
        <ChevronRight className="w-3 h-3" />
        <span className="text-primary">{agent.name}</span>
      </nav>

      <div className="flex flex-col lg:flex-row gap-10 lg:gap-16">
        {/* LEFT COLUMN (70%) */}
        <div className="lg:w-2/3">
          {/* 2. AGENT HEADER */}
          <div className="flex flex-col sm:flex-row gap-6 items-start mb-10">
            <div className="w-20 h-20 bg-elevated border-2 border-cyan/30 flex shadow-[0_0_20px_rgba(0,245,255,0.2)] items-center justify-center flex-shrink-0">
              <span className="font-display font-bold text-4xl text-cyan">{agent.name.charAt(0)}</span>
            </div>
            <div>
              <h1 className="font-display text-4xl font-bold text-white mb-2">{agent.name}</h1>
              <p className="text-lg text-muted italic mb-4">{agent.tagline}</p>
              
              <div className="flex flex-wrap items-center gap-4 mb-3">
                <StatusBadge status={agent.status} />
                <div className="flex items-center gap-1 bg-elevated px-2 py-0.5 border border-border text-xs font-mono rounded-sm">
                  <Star className="w-3 h-3 text-lime fill-lime" />
                  <span className="text-primary">{agent.rating.toFixed(1)}</span>
                  <span className="text-dim">({agent.total_runs * 2})</span>
                </div>
                <div className="text-xs font-mono text-muted pl-2 border-l border-border">
                  {agent.total_runs.toLocaleString()} runs
                </div>
              </div>

              <div className="flex items-center gap-2 font-mono text-xs">
                <User className="w-3 h-3 text-muted" />
                <span className="text-muted">by</span>
                <span className="text-primary font-bold">{agent.creator_name}</span>
                <CreatorScore score={agent.creator_score} />
                {agent.creator_score > 8 && (
                  <span className="bg-purple/10 text-purple border border-purple/30 px-1.5 py-0.5 ml-2">Verified Creator</span>
                )}
              </div>
            </div>
          </div>

          {/* 3. TABS HEADER */}
          <div className="flex gap-6 border-b border-border/50 mb-8 font-mono text-sm overflow-x-auto no-scrollbar">
            {['overview', 'try', 'reviews', 'api'].map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab as any)}
                className={`pb-3 capitalize transition-all relative whitespace-nowrap ${activeTab === tab ? 'text-cyan font-bold' : 'text-muted hover:text-primary'}`}
              >
                {tab === 'try' ? 'Try It' : tab === 'api' ? 'API Docs' : tab}
                {activeTab === tab && (
                  <motion.div layoutId="activeTab" className="absolute bottom-0 left-0 right-0 h-0.5 bg-cyan box-shadow-glow" />
                )}
              </button>
            ))}
          </div>

          <AnimatePresence mode="wait">
            {/* TAB: OVERVIEW */}
            {activeTab === 'overview' && (
              <motion.div key="overview" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
                {/* Metrics */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-10">
                  <div className="bg-elevated border border-border p-4">
                    <div className="text-dim text-[10px] font-mono mb-1 uppercase">Average Rating</div>
                    <div className="text-2xl font-display text-lime flex items-center gap-2">
                       {agent.rating.toFixed(1)}<Star className="w-4 h-4 fill-lime" />
                    </div>
                  </div>
                  <div className="bg-elevated border border-border p-4">
                    <div className="text-dim text-[10px] font-mono mb-1 uppercase">Total Runs</div>
                    <div className="text-2xl font-display text-primary">{agent.total_runs.toLocaleString()}</div>
                  </div>
                  <div className="bg-elevated border border-border p-4">
                    <div className="text-dim text-[10px] font-mono mb-1 uppercase">Success Rate</div>
                    <div className="text-2xl font-display text-primary">99.8%</div>
                  </div>
                  <div className="bg-elevated border border-border p-4">
                    <div className="text-dim text-[10px] font-mono mb-1 uppercase">Avg Run Time</div>
                    <div className="text-2xl font-display text-cyan">{agent.avg_run_time}s</div>
                  </div>
                </div>

                <div className="prose prose-invert prose-p:text-primary/80 max-w-none mb-10">
                  <ReactMarkdown>{agent.long_description || agent.description}</ReactMarkdown>
                </div>

                <h3 className="font-mono font-bold text-cyan mb-4 flex items-center gap-2"><CheckCircle2 className="w-4 h-4"/> PIPELINE CAPABILITIES</h3>
                <ul className="space-y-3 mb-12">
                  {agent.capabilities?.map((cap, i) => (
                    <li key={i} className="flex items-start gap-3 bg-card border border-border p-3 text-sm font-mono text-primary/90">
                      <Zap className="w-4 h-4 text-cyan mt-0.5 flex-shrink-0" />
                      {cap}
                    </li>
                  ))}
                </ul>
              </motion.div>
            )}

            {/* TAB: TRY IT */}
            {activeTab === 'try' && (
              <motion.div key="try" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
                <div className="flex justify-between items-end mb-4">
                  <h3 className="font-mono text-cyan flex items-center gap-2 font-bold"><Terminal className="w-4 h-4"/> DIRECT SANDBOX EXECUTION</h3>
                  <Link href={`/run/${id}`}>
                    <button className="text-xs font-mono text-primary bg-elevated border border-border px-3 py-1.5 hover:bg-cyan hover:text-void transition-colors flex items-center gap-2">
                       ENTER FULLSCREEN MODE <ChevronRight className="w-3 h-3" />
                    </button>
                  </Link>
                </div>
                
                <div className="bg-card border-x border-t border-border p-1 pb-0 flex items-center">
                  <div className="flex gap-2 p-3">
                    <div className="w-3 h-3 rounded-full bg-red-500/50" />
                    <div className="w-3 h-3 rounded-full bg-yellow-500/50" />
                    <div className="w-3 h-3 rounded-full bg-green-500/50" />
                  </div>
                  <div className="flex-1 text-center font-mono text-xs text-dim">terminal ~ {agent.slug}.sh</div>
                  <div className="w-16"></div>
                </div>
                
                <div className="bg-void border border-border flex flex-col mb-8 overflow-hidden shadow-[0_0_20px_rgba(0,0,0,0.5)]">
                  <div className="flex items-center gap-2 p-2 border-b border-border/30 bg-elevated">
                    {id === 'dataanalyst' && (
                      <label className="cursor-pointer text-[10px] font-mono text-cyan border border-cyan/30 px-2 py-1 hover:bg-cyan hover:text-void transition-colors flex items-center gap-1">
                        📎 Upload CSV/JSON
                        <input
                          type="file"
                          accept=".csv,.json,.txt,.tsv,.xml"
                          className="hidden"
                          onChange={(e) => {
                            const file = e.target.files?.[0];
                            if (file) {
                              const reader = new FileReader();
                              reader.onload = (ev) => {
                                const text = ev.target?.result as string;
                                setInput((prev) => prev + '\n\n--- UPLOADED FILE: ' + file.name + ' ---\n' + text.slice(0, 8000));
                              };
                              reader.readAsText(file);
                            }
                          }}
                        />
                      </label>
                    )}
                  </div>
                  <textarea
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    className="w-full h-32 bg-elevated border-b border-border/50 p-4 text-primary font-mono text-sm focus:outline-none resize-none"
                    placeholder={agent.input_placeholder || "Enter input parameters here..."}
                  />
                  
                  <div className="bg-[#050508] h-80 overflow-y-auto p-4 font-mono text-sm text-primary relative scroll-smooth selection:bg-cyan selection:text-void">
                    {!output && !isRunning && !error && (
                      <span className="text-dim">Waiting for payload... execute to begin.</span>
                    )}
                    {output && (
                      <div className="prose prose-invert prose-sm max-w-none prose-a:text-cyan prose-a:underline prose-headings:text-cyan prose-strong:text-primary">
                        <ReactMarkdown>{output}</ReactMarkdown>
                      </div>
                    )}
                    {isRunning && <motion.span animate={{ opacity: [1, 0, 1] }} transition={{ repeat: Infinity, duration: 0.8 }} className="inline-block w-2 h-4 bg-cyan ml-1 align-middle" />}
                    {error && <div className="text-red-500 mt-4 border border-red-500/30 bg-red-500/10 p-4 font-bold">[SYSTEM_ERROR]: {error}</div>}
                    {runStats && <div className="text-lime mt-4 pt-4 border-t border-dashed border-border/50 break-words font-bold">✓ Completed in {(runStats.time).toFixed(2)}s. Connection closed.</div>}
                    <div ref={endOfOutputRef} />
                  </div>
                  
                  <div className="bg-card p-4 border-t border-border flex flex-col sm:flex-row gap-4 items-center justify-between">
                    <div className="text-xs font-mono text-muted flex gap-4">
                      <span>STATUS: <span className={isRunning ? 'text-orange animate-pulse' : 'text-cyan'}>{isRunning ? 'RUNNING...' : (runStats ? 'COMPLETED' : 'IDLE')}</span></span>
                    </div>
                    
                    <button
                      onClick={handleRun}
                      disabled={isRunning || !input.trim()}
                      className="w-full sm:w-auto bg-cyan text-void font-bold font-mono px-8 py-3 flex items-center justify-center gap-2 disabled:opacity-50 hover:bg-transparent hover:text-cyan border border-cyan transition-all"
                    >
                      {isRunning ? <div className="w-4 h-4 rounded-full border-2 border-t-transparent border-void animate-spin" /> : <Rocket className="w-4 h-4 fill-current" />}
                      {isRunning ? 'EXECUTING' : 'RUN AGENT'}
                    </button>
                  </div>
                </div>

                {runStats && (
                  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-elevated border border-border p-6 flex flex-col sm:flex-row items-center justify-between gap-4">
                     <div>
                       <h4 className="font-mono text-primary font-bold mb-1">Rate this run</h4>
                       <p className="text-xs text-muted font-mono">Help improve the network</p>
                     </div>
                     <div className="flex gap-2">
                       {[1, 2, 3, 4, 5].map(star => (
                         <Star key={star} className="w-6 h-6 text-muted hover:text-lime hover:fill-lime cursor-pointer transition-colors" />
                       ))}
                     </div>
                  </motion.div>
                )}
              </motion.div>
            )}

            {/* TAB: REVIEWS */}
            {activeTab === 'reviews' && (
              <motion.div key="reviews" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
                <div className="font-mono text-center text-muted py-20 border border-dashed border-border mb-8">
                   No reviews found locally.
                </div>
              </motion.div>
            )}

            {/* TAB: API DOCS */}
            {activeTab === 'api' && (
              <motion.div key="api" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
                <h3 className="font-mono font-bold text-cyan mb-4">REST API ACCESS</h3>
                <p className="text-sm text-dim mb-6">Execute this agent securely via HTTP utilizing your AGORA API key.</p>
                
                <div className="bg-void border border-border p-4 relative mb-6 font-mono text-sm overflow-x-auto text-primary">
                  <div className="absolute top-4 right-4 bg-elevated border border-border p-1.5 cursor-pointer hover:text-cyan"><Copy className="w-4 h-4"/></div>
                  <div className="text-dim mb-2"># cURL Example / Stream response over SSE</div>
                  <pre>
<span className="text-lime">curl</span> -X POST https://api.agora.marketplace/v1/agents/{agent.id}/run \<br/>
     -H <span className="text-orange">"Authorization: Bearer $AGORA_API_KEY"</span> \<br/>
     -H <span className="text-orange">"Content-Type: application/json"</span> \<br/>
     -d <span className="text-purple">{`'{"input": "Example query", "stream": true}'`}</span>
                  </pre>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* RIGHT SIDEBAR (30%) */}
        <div className="lg:w-1/3">
          <div className="bg-elevated border border-border p-6 sticky top-24">
            <div className="mb-6">
              <span className="text-xs font-mono text-cyan bg-cyan/10 border border-cyan/20 px-2 py-1">DEPLOY NOW</span>
              <div className="mt-4 font-display text-4xl text-primary font-bold">FREE</div>
              <p className="text-muted text-sm mt-1">No signup required • 3 free runs</p>
            </div>
            
            <Link href={`/run/${id}`}>
              <button className="w-full bg-primary text-void font-bold font-mono py-4 flex items-center justify-center gap-2 hover:bg-cyan transition-colors mb-6">
                 <Play className="w-4 h-4 fill-current" /> RUN FULLSCREEN
              </button>
            </Link>

            <div className="space-y-4 border-t border-border pt-6 text-sm">
              <div className="flex justify-between items-center font-mono">
                <span className="text-dim flex items-center gap-2"><Calendar className="w-4 h-4"/> Created</span>
                <span className="text-primary">2026-04-18</span>
              </div>
              <div className="flex justify-between items-center font-mono">
                <span className="text-dim flex items-center gap-2"><Tag className="w-4 h-4"/> Category</span>
                <span className="text-primary">{agent.category}</span>
              </div>
              <div className="flex justify-between items-center font-mono border-t border-border pt-4">
                 <span className="text-dim w-full flex items-center gap-2 mb-2"><Hash className="w-4 h-4"/> Compatibility</span>
              </div>
              <div className="flex gap-2 font-mono text-[10px]">
                <span className="bg-purple/10 border border-purple/30 text-purple px-2 py-1">Compose Mode</span>
                <span className="bg-orange/10 border border-orange/30 text-orange px-2 py-1">Battle Mode</span>
              </div>
            </div>

            <button onClick={() => {
              navigator.clipboard.writeText(window.location.href);
              setCopiedUrl(true);
              setTimeout(() => setCopiedUrl(false), 2000);
            }} className="w-full border border-border bg-void text-primary font-mono text-sm py-3 mt-8 flex items-center justify-center gap-2 hover:border-cyan hover:text-cyan transition-colors">
              {copiedUrl ? <CheckCircle2 className="w-4 h-4" /> : <Copy className="w-4 h-4" />} 
              {copiedUrl ? 'LINK COPIED' : 'COPY SHARE LINK'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
