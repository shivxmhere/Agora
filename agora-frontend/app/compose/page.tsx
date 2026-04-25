"use client";

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Workflow, Plus, X, Rocket, Zap, Link as LinkIcon, CheckCircle2 } from 'lucide-react';
import useSWR from 'swr';
import { api } from '@/lib/api';
import Link from 'next/link';

export default function ComposePage() {
  const { data: agents } = useSWR('agents', () => api.getAgents());
  
  const [steps, setSteps] = useState([{ id: Math.random().toString(), agentId: '' }]);
  const [input, setInput] = useState('');
  
  const [isRunning, setIsRunning] = useState(false);
  const [pipelineRunId, setPipelineRunId] = useState('');
  const [stepRunIds, setStepRunIds] = useState<string[]>([]);
  const [stepData, setStepData] = useState<Record<string, {status: string, output?: string, run_time?: number}>>({});

  const addStep = () => {
    if (steps.length < 4) {
      setSteps([...steps, { id: Math.random().toString(), agentId: agents?.[0]?.id || '' }]);
    }
  };

  const removeStep = (index: number) => {
    setSteps(steps.filter((_, i) => i !== index));
  };

  const updateStep = (index: number, agentId: string) => {
    const newSteps = [...steps];
    newSteps[index].agentId = agentId;
    setSteps(newSteps);
  };

  const PRESETS = [
    { title: "Research → Blog Post", desc: "AutoResearch → ContentWriter", ids: ["autoresearch", "contentwriter"] },
    { title: "Research → Code Spec", desc: "AutoResearch → CodeReview", ids: ["autoresearch", "codereview"] },
    { title: "Market Spy → Report", desc: "MarketSpy → ContentWriter", ids: ["marketspy", "contentwriter"] }
  ];

  const loadPreset = (preset: typeof PRESETS[0]) => {
    if (!agents) return;
    const newSteps = preset.ids.map(slug => {
      const a = agents.find((ag: any) => ag.slug === slug || ag.slug?.includes(slug));
      return { id: Math.random().toString(), agentId: a?.id || agents[0].id };
    });
    setSteps(newSteps);
    setInput("What are the latest AI agents marketplace trends in 2026?");
  };

  useEffect(() => {
    // Polling logic
    if (isRunning && stepRunIds.length > 0) {
      const interval = setInterval(async () => {
        let allDone = true;
        
        for (const runId of stepRunIds) {
          try {
            const data = await api.getRun(runId);
            setStepData(prev => ({...prev, [runId]: data}));
            if (data.status !== 'completed' && data.status !== 'failed') {
              allDone = false;
            }
          } catch (e) {
             // ignoring initial not found errors due to background task latency
             allDone = false; 
          }
        }
        
        if (allDone) {
          setIsRunning(false);
          clearInterval(interval);
        }
      }, 1000);
      
      return () => clearInterval(interval);
    }
  }, [isRunning, stepRunIds]);

  const startPipeline = async () => {
    if (!input.trim() || steps.some(s => !s.agentId) || isRunning) return;
    setIsRunning(true);
    setStepData({});
    setStepRunIds([]);
    
    try {
      const sessionId = Math.random().toString(36).substring(7);
      const res = await api.runCompose(steps.map(s => ({ agent_id: s.agentId })), input, sessionId);
      setPipelineRunId(res.pipeline_run_id);
      setStepRunIds(res.step_run_ids);
    } catch (err: any) {
      alert("Pipeline initialization failed: " + err.message);
      setIsRunning(false);
    }
  };

  return (
    <div className="min-h-screen bg-void flex flex-col font-mono text-primary pt-24 px-4 pb-12 relative">
      <div className="max-w-6xl mx-auto w-full text-center mb-12">
        <div className="flex items-center justify-center gap-4 mb-4">
          <Workflow className="w-10 h-10 text-purple" />
          <h1 className="font-display text-5xl font-bold tracking-tight text-white">AGENT COMPOSE</h1>
          <Workflow className="w-10 h-10 text-purple" />
        </div>
        <p className="text-muted">Chain specialized entities together to form complex cognitive architectures.</p>
      </div>

      <div className="max-w-4xl mx-auto w-full grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        {PRESETS.map((p, i) => (
          <button key={i} onClick={() => loadPreset(p)} className="bg-card border border-border p-4 hover:border-purple transition-all text-left group">
            <h3 className="text-primary font-bold mb-1 group-hover:text-purple">{p.title}</h3>
            <p className="text-muted text-[10px]">{p.desc}</p>
          </button>
        ))}
      </div>

      <div className="max-w-4xl mx-auto w-full">
        {/* INPUT */}
        <div className="mb-8 p-6 bg-card border border-border shadow-[0_0_20px_rgba(123,47,190,0.1)]">
          <h3 className="text-xs text-purple mb-4 flex items-center gap-2"><Zap className="w-4 h-4"/> BASE DIRECTIVE SEQUENCE</h3>
          <textarea 
            className="w-full h-24 bg-elevated border border-border p-4 resize-none focus:outline-none focus:border-purple text-white mb-4"
            placeholder="Initial input payload (feeds into Step 1)..."
            value={input} onChange={e => setInput(e.target.value)}
          />
        </div>

        {/* BUILDER */}
        <div className="space-y-4 mb-12 relative before:absolute before:inset-y-0 before:left-8 before:w-0.5 before:bg-border before:-z-10">
          <AnimatePresence>
            {steps.map((step, idx) => (
              <motion.div key={step.id} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, scale: 0.9 }} className="flex items-start gap-6">
                <div className="w-16 h-16 rounded-full bg-void border border-border flex items-center justify-center font-display text-xl z-10 text-muted shadow-[0_0_10px_rgba(0,0,0,0.5)]">
                  {idx + 1}
                </div>
                <div className="flex-1 bg-card border border-border p-4 flex flex-col sm:flex-row items-center gap-4 relative">
                  <div className="flex-1 w-full">
                    <select className="w-full bg-elevated border border-border p-3 outline-none focus:border-purple text-primary" value={step.agentId} onChange={e => updateStep(idx, e.target.value)}>
                      <option value="" disabled>Select an agent...</option>
                      {agents?.map((a: any) => <option key={a.id} value={a.id}>{a.name} ({a.category})</option>)}
                    </select>
                  </div>
                  {steps.length > 1 && (
                    <button onClick={() => removeStep(idx)} className="w-10 h-10 flex items-center justify-center text-muted hover:text-red-500 border border-transparent hover:border-red-500 bg-elevated transition-colors">
                       <X className="w-4 h-4" />
                    </button>
                  )}
                  {idx < steps.length - 1 && (
                    <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-border">
                      <LinkIcon className="w-4 h-4" />
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          
          {steps.length < 4 && (
            <div className="flex gap-6 pt-4">
              <div className="w-16 flex justify-center text-border"><div className="h-full w-0.5" /></div>
              <button onClick={addStep} className="text-xs text-purple flex items-center gap-1 hover:text-white transition-colors bg-elevated border border-border px-4 py-2">
                <Plus className="w-3 h-3"/> ADD INTERNAL PIPELINE STEP
              </button>
            </div>
          )}
        </div>

        <button 
          onClick={startPipeline} disabled={isRunning || !input.trim() || steps.some(s => !s.agentId)}
          className="w-full bg-void border border-purple text-purple font-display text-2xl font-bold py-6 hover:bg-purple hover:text-void hover:shadow-[0_0_30px_rgba(123,47,190,0.5)] transition-all disabled:opacity-50 flex items-center justify-center gap-4 shadow-[inset_0_0_20px_rgba(123,47,190,0.2)]"
        >
          {isRunning ? <><div className="w-6 h-6 border-4 border-t-transparent border-current rounded-full animate-spin" /> EXECUTING CONTINUOUS PIPELINE...</> : <><Rocket className="w-6 h-6" /> INITIATE COMPOSE RUN</>}
        </button>

        {/* RESULTS PANELS */}
        {(stepRunIds.length > 0) && (
          <div className="mt-16 space-y-8 pb-16">
            <h3 className="font-display text-2xl text-primary border-b border-border pb-4">PIPELINE TELEMETRY</h3>
            {stepRunIds.map((runId, idx) => {
              const data = stepData[runId];
              const isActive = data?.status === 'running';
              const isDone = data?.status === 'completed';
              const isFailed = data?.status === 'failed';
              const isWaiting = !data || data.status === 'queued';
              
              const agentName = agents?.find((a: any) => a.id === steps[idx]?.agentId)?.name || `Step ${idx+1}`;

              return (
                <div key={runId} className={`border ${isActive ? 'border-purple shadow-[0_0_20px_rgba(123,47,190,0.2)]' : isFailed ? 'border-red-500' : isDone ? 'border-lime/30' : 'border-border/50'} bg-[#050508] transition-all`}>
                  <div className="bg-card px-4 py-3 border-b border-border/50 flex justify-between items-center text-xs">
                     <div className="flex items-center gap-3">
                       <span className="text-dim font-bold">STEP {idx + 1}</span>
                       <span className={isActive ? 'text-purple' : isDone ? 'text-lime' : 'text-primary'}>{agentName}</span>
                     </div>
                     <div className="flex items-center gap-4">
                       <span className={isActive ? 'text-purple animate-pulse' : isDone ? 'text-lime' : isFailed ? 'text-red-500' : 'text-dim'}>
                         {isActive ? 'RUNNING...' : isDone ? 'COMPLETED' : isFailed ? 'FAILED' : 'WAITING FOR UPSTREAM...'}
                       </span>
                       {data?.run_time && <span className="text-dim">{data.run_time.toFixed(2)}s</span>}
                     </div>
                  </div>
                  
                  <div className="p-6 text-sm whitespace-pre-wrap font-mono min-h-[150px] relative">
                    {isWaiting ? <div className="absolute inset-0 flex items-center justify-center text-border italic">...</div> : null}
                    {isActive ? <div className="text-purple italic flex items-center gap-2"><div className="w-2 h-2 bg-purple rounded-full animate-bounce" /> Analyzing dataset & executing operations...</div> : null}
                    {isDone && <div className="text-primary/90">{data.output}</div>}
                    {isFailed && <div className="text-red-500">{data.output || "Fatal error in pipeline."}</div>}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
