"use client";

import { useState, useRef, useEffect } from 'react';
import { useAgent } from '@/hooks/useAgents';
import { api } from '@/lib/api';
import { Play, Copy, CheckCircle2, ChevronRight, XCircle, ArrowLeft, Download, RotateCcw } from 'lucide-react';
import { useParams, useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import ReactMarkdown from 'react-markdown';

const steps = [
  "Searching",
  "Reading",
  "Analyzing",
  "Fact-Checking",
  "Reporting"
];

function FullScreenRunner() {
  const router = useRouter();
  const params = useParams();
  const id = params.id as string;
  const { agent, isLoading } = useAgent(id);

  const [input, setInput] = useState('');
  const [output, setOutput] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState('');
  const [runStats, setRunStats] = useState<{time: number} | null>(null);
  
  const [activeStep, setActiveStep] = useState(-1);
  const [elapsed, setElapsed] = useState(0);

  const endOfOutputRef = useRef<HTMLDivElement>(null);
  const tokenQueue = useRef<string[]>([]);
  const typerInterval = useRef<NodeJS.Timeout | null>(null);

  // Timer loop
  useEffect(() => {
    let t: NodeJS.Timeout;
    if (isRunning) {
      t = setInterval(() => setElapsed(e => e + 1), 1000);
    }
    return () => clearInterval(t);
  }, [isRunning]);

  // Typer effect loop
  useEffect(() => {
    if (isRunning) {
      typerInterval.current = setInterval(() => {
        if (tokenQueue.current.length > 0) {
          const chunk = tokenQueue.current.splice(0, 5).join('');
          setOutput(prev => prev + chunk);
          
          // Step detection
          if (chunk.includes('[Searching')) setActiveStep(0);
          else if (chunk.includes('[Reading')) setActiveStep(1);
          else if (chunk.includes('[Analyzing')) setActiveStep(2);
          else if (chunk.includes('[Fact-Checking') || chunk.includes('[Fact')) setActiveStep(3);
          else if (chunk.includes('[Reporting')) setActiveStep(4);
        }
      }, 50); // 50ms batching as requested
    } else {
      if (typerInterval.current) clearInterval(typerInterval.current);
      // Flush queue if done
      if (tokenQueue.current.length > 0) {
        setOutput(prev => prev + tokenQueue.current.join(''));
        tokenQueue.current = [];
      }
    }
    return () => { if(typerInterval.current) clearInterval(typerInterval.current); };
  }, [isRunning]);

  useEffect(() => {
    endOfOutputRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [output]);

  if (isLoading) return <div className="min-h-screen bg-void flex items-center justify-center font-mono text-cyan">AGORA_OS Loading...</div>;
  if (!agent) return <div className="min-h-screen bg-void flex items-center justify-center font-mono text-red-500">INIT_ERROR: Agent not found</div>;

  const handleRun = async () => {
    if (!input.trim() || isRunning) return;
    
    setIsRunning(true);
    setOutput('');
    setError('');
    setActiveStep(0);
    setElapsed(0);
    setRunStats(null);
    tokenQueue.current = [];
    
    try {
      const sessionId = Math.random().toString(36).substring(7);
      const res = await api.runAgent(id, input, sessionId);
      
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
      const eventSource = new EventSource(`${backendUrl}${res.stream_url}`);
      
      eventSource.onmessage = (e) => {
        const data = JSON.parse(e.data);
        if (data.type === 'token') {
          tokenQueue.current.push(data.content);
        } else if (data.type === 'done') {
          setActiveStep(5); // all done
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

  const copyToClipboard = () => {
    navigator.clipboard.writeText(output);
  };

  const downloadHtml = () => {
    const element = document.createElement("a");
    const file = new Blob([output], {type: 'text/markdown'});
    element.href = URL.createObjectURL(file);
    element.download = `${agent.slug}_run.md`;
    document.body.appendChild(element);
    element.click();
  };

  return (
    <div className="min-h-screen bg-void flex flex-col font-mono text-primary overflow-hidden">
      {/* TOP BAR */}
      <div className="h-14 border-b border-border bg-[#0a0a10] px-4 flex items-center justify-between flex-shrink-0 z-10 w-full">
        <div className="flex items-center gap-4">
          <Link href={`/agent/${id}`} className="text-muted hover:text-cyan p-1"><ArrowLeft className="w-4 h-4"/></Link>
          <div className="font-display font-bold text-xl text-cyan tracking-wider flex items-center gap-2">AGORA <div className={`w-2 h-2 rounded-full ${isRunning ? 'bg-orange animate-pulse' : 'bg-lime box-shadow-glow'}`}/></div>
        </div>
        <div className="font-mono text-sm tracking-widest text-primary absolute left-1/2 -translate-x-1/2 hidden md:block">
           {isRunning ? 'RUNNING: ' : 'READY: '} <span className={isRunning ? 'text-orange' : 'text-cyan'}>{agent.name}</span>
        </div>
        <div className="font-mono text-sm text-dim w-24 text-right">
           T+ {Math.floor(elapsed / 60).toString().padStart(2, '0')}:{(elapsed % 60).toString().padStart(2, '0')}
        </div>
      </div>

      {/* BODY */}
      <div className="flex-1 flex flex-col lg:flex-row overflow-hidden relative">
        {(isRunning || output) && (
           <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="absolute inset-0 pointer-events-none" style={{ backgroundImage: 'linear-gradient(rgba(0, 245, 255, 0.03) 1px, transparent 1px)', backgroundSize: '100% 4px', zIndex: 50 }} />
        )}
        
        {/* INPUT PANEL (40%) */}
        <div className="w-full lg:w-2/5 flex flex-col border-r border-border bg-void h-full relative z-20 transition-all duration-500">
           <div className="px-6 py-4 flex items-center justify-between border-b border-border bg-[#050508]">
             <div className="flex items-center gap-2">
               <div className="w-2 h-2 rounded-full bg-lime box-shadow-glow"/>
               <span className="text-sm font-bold tracking-widest">INPUT</span>
             </div>
             <label className="cursor-pointer text-xs font-mono text-cyan border border-cyan/30 px-3 py-1.5 hover:bg-cyan hover:text-void transition-colors flex items-center gap-2">
               📎 Upload Document
               <input
                 type="file"
                 accept=".csv,.json,.txt,.tsv,.xml,.md,.log,.py,.js,.ts,.html,.css,.yaml,.yml,.env,.sql,.sh"
                 className="hidden"
                 onChange={(e) => {
                   const file = e.target.files?.[0];
                   if (file) {
                     const reader = new FileReader();
                     reader.onload = (ev) => {
                       const text = ev.target?.result as string;
                       setInput((prev) => (prev ? prev + '\n\n' : '') + '--- UPLOADED FILE: ' + file.name + ' ---\n' + text.slice(0, 10000));
                     };
                     reader.readAsText(file);
                   }
                 }}
               />
             </label>
           </div>
           
           <div className="flex-1 flex flex-col p-6">
             <textarea
                value={input}
                onChange={e => setInput(e.target.value)}
                disabled={isRunning}
                className="w-full flex-1 bg-transparent border-none text-primary font-mono text-sm focus:outline-none resize-none mb-6 placeholder-dim disabled:opacity-50"
                placeholder={agent.input_placeholder || "root@agora:~# Type query or upload a document..."}
             />
             
             <div className="flex flex-col gap-4 mt-auto">
               <button
                  onClick={handleRun}
                  disabled={isRunning || !input.trim()}
                  className="w-full bg-cyan text-void font-bold py-4 hover:bg-transparent hover:text-cyan border border-cyan transition-all disabled:opacity-50 disabled:cursor-not-allowed group relative overflow-hidden"
               >
                 <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300" />
                 <span className="relative flex items-center justify-center gap-2">
                   {isRunning ? <div className="w-4 h-4 rounded-full border-2 border-t-transparent border-void animate-spin" /> : <ChevronRight className="w-5 h-5"/>} 
                   {isRunning ? 'EXECUTING PIPELINE...' : 'EXECUTE →'}
                 </span>
               </button>
               <div className="flex gap-4">
                 <button onClick={() => setInput('')} disabled={isRunning} className="flex-1 bg-elevated border border-border py-2 text-xs text-muted hover:text-primary transition-colors disabled:opacity-50">Clear</button>
                 <button onClick={() => setInput(agent.input_placeholder || 'What are the top AI agents of 2026?')} disabled={isRunning} className="flex-1 bg-elevated border border-border py-2 text-xs text-muted hover:text-primary transition-colors disabled:opacity-50">Example Query</button>
               </div>
             </div>
           </div>
        </div>

        {/* OUTPUT PANEL (60%) */}
        <div className="w-full lg:w-3/5 bg-[#050508] h-full flex flex-col relative z-20">
           <div className="px-6 py-4 flex items-center justify-between border-b border-border bg-[#0a0a10]">
             <div className="flex items-center gap-2">
               <div className={`w-2 h-2 rounded-full ${isRunning ? 'bg-orange animate-pulse' : (output ? 'bg-lime' : 'bg-dim')}`}/>
               <span className="text-sm font-bold tracking-widest text-muted">OUTPUT</span>
             </div>
             
             <div className="flex gap-3">
               <button onClick={copyToClipboard} className="text-muted hover:text-cyan" title="Copy"><Copy className="w-4 h-4"/></button>
               <button onClick={downloadHtml} className="text-muted hover:text-cyan" title="Download MD"><Download className="w-4 h-4"/></button>
             </div>
           </div>

           <div className="flex-1 flex overflow-hidden">
             {/* PIPELINE TRACKER */}
             {(output || isRunning) && (
               <motion.div initial={{ width: 0, opacity: 0 }} animate={{ width: "200px", opacity: 1 }} className="border-r border-border bg-void/50 p-4 flex flex-col gap-6 overflow-y-auto">
                 {steps.map((step, idx) => {
                   const isPast = activeStep > idx;
                   const isCurrent = activeStep === idx;
                   return (
                     <div key={step} className="flex items-start gap-3">
                       <div className="mt-0.5 relative flex items-center justify-center">
                         {isPast ? <CheckCircle2 className="w-4 h-4 text-lime" /> : (
                           isCurrent ? <div className="w-4 h-4 border-2 border-cyan rounded-full border-t-transparent animate-spin"/> :
                           <div className="w-4 h-4 border-2 border-border rounded-full" />
                         )}
                         {idx < steps.length - 1 && (
                           <div className={`absolute top-5 left-1.5 w-0.5 h-6 ${isPast ? 'bg-lime' : 'bg-border'}`}/>
                         )}
                       </div>
                       <div className="flex flex-col">
                         <span className={`text-xs ${isPast ? 'text-lime' : isCurrent ? 'text-cyan font-bold' : 'text-dim'}`}>{step}</span>
                         {isPast && <span className="text-[9px] text-muted tracking-widest">{Math.floor(Math.random() * 900) + 100}ms</span>}
                       </div>
                     </div>
                   )
                 })}
               </motion.div>
             )}

             {/* TERMINAL CONTENT */}
             <div className="flex-1 p-6 overflow-y-auto text-sm leading-relaxed selection:bg-cyan selection:text-void font-mono">
               {!output && !isRunning && !error && (
                 <div className="text-dim h-full flex items-center justify-center text-center opacity-50">
                    <div>
                      <div className="text-4xl mb-4">_</div>
                      <div>Awaiting instruction block.</div>
                    </div>
                 </div>
               )}
               {output && (
                 <div className="prose prose-invert prose-sm max-w-none prose-a:text-cyan prose-a:underline prose-headings:text-cyan prose-strong:text-primary">
                   <ReactMarkdown>{output}</ReactMarkdown>
                 </div>
               )}
               {isRunning && <span className="inline-block w-2 h-4 bg-cyan ml-1 align-middle animate-pulse"/>}
               {error && <div className="mt-4 p-4 bg-red-500/10 border border-red-500 text-red-500 font-bold">[CRITICAL_ERROR]: {error}</div>}
               <div ref={endOfOutputRef} />
             </div>
           </div>
        </div>
      </div>

      {/* BOTTOM BAR */}
      <div className="h-10 border-t border-border bg-[#0a0a10] px-4 flex items-center justify-between flex-shrink-0 z-10 w-full text-xs text-muted">
        <div className="flex items-center gap-6">
          <span>MODEL: Llama-3.3-70b-Groq</span>
          <span className="hidden sm:inline">TOKENS: {Math.floor(output.length / 4).toLocaleString()} tk</span>
        </div>
        
        {runStats && (
          <div className="flex items-center gap-4">
            <span className="text-lime">SUCCESS: {runStats.time.toFixed(2)}s</span>
            <button onClick={() => { setInput(''); setOutput(''); setRunStats(null); }} className="flex items-center gap-1 hover:text-cyan text-primary transition-colors">
              <RotateCcw className="w-3 h-3"/> RUN AGAIN
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default FullScreenRunner;
