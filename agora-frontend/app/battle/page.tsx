"use client";

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Swords, Rocket, ChevronDown, CheckCircle2, Zap } from 'lucide-react';
import useSWR from 'swr';
import { api } from '@/lib/api';
import ReactMarkdown from 'react-markdown';

export default function BattlePage() {
  const { data: agents } = useSWR('agents', () => api.getAgents());
  
  const [agent1Id, setAgent1Id] = useState('');
  const [agent2Id, setAgent2Id] = useState('');
  const [input, setInput] = useState('');
  const [isBattling, setIsBattling] = useState(false);
  const [battleComplete, setBattleComplete] = useState(false);
  
  const [out1, setOut1] = useState('');
  const [out2, setOut2] = useState('');
  const [stats1, setStats1] = useState<{time?: number, running: boolean, error?: string}>({ running: false });
  const [stats2, setStats2] = useState<{time?: number, running: boolean, error?: string}>({ running: false });
  const [winner, setWinner] = useState<{fastest?: string, better?: string}>({});

  const agent1 = agents?.find((a: any) => a.id === agent1Id) || agents?.[0];
  const agent2 = agents?.find((a: any) => a.id === agent2Id) || agents?.[1];

  useEffect(() => {
    if (agents && agents.length >= 2) {
      if (!agent1Id) setAgent1Id(agents[0].id);
      if (!agent2Id) setAgent2Id(agents[1].id);
    }
  }, [agents, agent1Id, agent2Id]);

  useEffect(() => {
    if (!stats1.running && !stats2.running && out1 && out2 && isBattling) {
      setIsBattling(false);
      setBattleComplete(true);
      
      const fastest = (stats1.time || 0) < (stats2.time || 0) ? '1' : '2';
      setWinner({ fastest });
    }
  }, [stats1.running, stats2.running, out1, out2, isBattling]);

  const handleVote = (voteFor: '1' | '2') => {
    setWinner(prev => ({ ...prev, better: voteFor }));
    // store in localStorage theoretically
  };

  const startBattle = async () => {
    if (!agent1Id || !agent2Id || !input.trim() || isBattling) return;
    
    setIsBattling(true);
    setBattleComplete(false);
    setOut1('');
    setOut2('');
    setStats1({ running: true });
    setStats2({ running: true });
    setWinner({});

    try {
      const sessionId = Math.random().toString(36).substring(7);
      
      const [res1, res2] = await Promise.all([
        api.runAgent(agent1Id, input, sessionId + '-1'),
        api.runAgent(agent2Id, input, sessionId + '-2')
      ]);

      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
      
      const es1 = new EventSource(`${backendUrl}${res1.stream_url}`);
      es1.onmessage = (e) => {
        const data = JSON.parse(e.data);
        if (data.type === 'token') setOut1(p => p + data.content);
        else if (data.type === 'done') {
          setStats1({ running: false, time: data.run_time });
          es1.close();
        } else if (data.type === 'error') {
          setStats1({ running: false, error: data.message });
          es1.close();
        }
      };
      
      const es2 = new EventSource(`${backendUrl}${res2.stream_url}`);
      es2.onmessage = (e) => {
        const data = JSON.parse(e.data);
        if (data.type === 'token') setOut2(p => p + data.content);
        else if (data.type === 'done') {
          setStats2({ running: false, time: data.run_time });
          es2.close();
        } else if (data.type === 'error') {
          setStats2({ running: false, error: data.message });
          es2.close();
        }
      };

    } catch (err: any) {
      alert("Failed to start battle: " + err.message);
      setIsBattling(false);
      setStats1({ running: false });
      setStats2({ running: false });
    }
  };

  return (
    <div className="min-h-screen bg-void flex flex-col font-mono text-primary pt-24 px-4 pb-12 relative overflow-hidden">
      {/* HEADER */}
      <div className="max-w-6xl mx-auto w-full text-center relative z-10 mb-12">
        <div className="flex items-center justify-center gap-4 mb-4">
          <Swords className="w-10 h-10 text-orange" />
          <h1 className="font-display text-5xl font-bold tracking-tight text-white">AGENT BATTLE</h1>
          <Swords className="w-10 h-10 text-orange" />
        </div>
        <p className="text-muted">Same input. Two autonomous entities. You decide the winner.</p>
      </div>

      <div className="max-w-7xl mx-auto w-full relative z-10 flex-1 flex flex-col">
        {/* AGENT SELECTION ROW */}
        <div className="flex flex-col lg:flex-row items-center justify-between gap-8 mb-8">
          <div className="w-full lg:w-[45%]">
             <div className="text-xs text-cyan mb-2">ENTENDER 1</div>
             <select className="w-full bg-card border-2 border-cyan/30 p-4 text-xl outline-none focus:border-cyan transition-colors" value={agent1Id} onChange={e => setAgent1Id(e.target.value)}>
               {agents?.map((a: any) => <option key={a.id} value={a.id}>{a.name}</option>)}
             </select>
          </div>
          
          <div className="font-display text-4xl font-bold text-orange relative">
             <div className="absolute inset-0 blur-md text-orange opacity-50">VS</div>
             VS
          </div>

          <div className="w-full lg:w-[45%]">
             <div className="text-xs text-purple mb-2 text-right">ENTENDER 2</div>
             <select className="w-full bg-card border-2 border-purple/30 p-4 text-xl outline-none focus:border-purple transition-colors text-right" value={agent2Id} onChange={e => setAgent2Id(e.target.value)}>
               {agents?.map((a: any) => <option key={a.id} value={a.id}>{a.name}</option>)}
             </select>
          </div>
        </div>

        {/* INPUT */}
        <div className="max-w-4xl mx-auto w-full mb-12 flex flex-col gap-4">
          <textarea 
            className="w-full h-32 bg-elevated border border-border p-4 resize-none focus:outline-none focus:border-orange text-white"
            placeholder="Provide a complex prompt, analytical task, or coding challenge to test both agents simultaneously..."
            value={input} onChange={e => setInput(e.target.value)}
          />
          <button 
            onClick={startBattle} disabled={isBattling || !input.trim() || !agent1Id || !agent2Id}
            className="w-full bg-gradient-to-r from-orange to-red-600 text-white font-display text-2xl font-bold py-4 hover:shadow-[0_0_30px_rgba(255,107,53,0.5)] transition-all disabled:opacity-50 disabled:grayscale flex items-center justify-center gap-4"
          >
            {isBattling ? <><div className="w-6 h-6 border-4 border-t-white border-white/30 rounded-full animate-spin" /> EXECUTING BATTLE...</> : <><Swords className="w-6 h-6" /> START BATTLE</>}
          </button>
        </div>

        <AnimatePresence>
          {battleComplete && (
            <motion.div initial={{ y: -50, opacity: 0 }} animate={{ y: 0, opacity: 1 }} className="absolute text-center justify-center container w-full z-50 pointer-events-none mt-[-5rem] mb-[5rem]">
              <div className="inline-block bg-void border border-border px-8 py-3 mb-8 shadow-[0_0_50px_rgba(0,0,0,0.8)] backdrop-blur-md">
                <span className="text-xl font-display text-white font-bold inline-flex items-center gap-3">
                  <CheckCircle2 className="w-6 h-6 text-lime" /> BATTLE COMPLETE
                </span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* BATTLE AREA */}
        <div className="flex flex-col lg:flex-row flex-1 border border-border shadow-[0_0_40px_rgba(0,0,0,0.5)]">
          {/* LEFT PANEL */}
          <div className="w-full lg:w-1/2 border-b lg:border-b-0 lg:border-r border-border bg-[#050508] flex flex-col min-h-[400px]">
            <div className="bg-card px-4 py-3 border-b border-border flex justify-between items-center text-xs">
               <div className="flex items-center gap-2">
                 <Zap className={`w-4 h-4 ${stats1.running ? 'text-orange animate-pulse' : 'text-cyan'}`} />
                 <span className="font-bold">{agent1?.name || 'Agent 1'}</span>
               </div>
               <div className="text-dim">{stats1.time ? `${stats1.time.toFixed(2)}s` : stats1.running ? 'Running...' : 'Ready'}</div>
            </div>
            
            <div className="p-6 flex-1 text-sm text-primary/90 font-mono relative overflow-y-auto">
              {out1 && (
                <div className="prose prose-invert prose-sm max-w-none prose-a:text-cyan prose-a:underline prose-headings:text-cyan">
                  <ReactMarkdown>{out1}</ReactMarkdown>
                </div>
              )}
              {stats1.running && <span className="inline-block w-2 h-4 bg-cyan animate-pulse ml-1 align-middle" />}
              {stats1.error && <div className="text-red-500 mt-4 border border-red-500/30 bg-red-500/10 p-4">{stats1.error}</div>}
              {!out1 && !stats1.running && !stats1.error && <div className="text-dim absolute inset-0 flex items-center justify-center italic">Awaiting initiation sequence...</div>}
            </div>
            
            {battleComplete && (
              <div className="p-4 bg-elevated border-t border-border flex justify-between items-center text-xs">
                <div>{out1.split(/\s+/).length} words internally</div>
                {winner.fastest === '1' && <span className="text-lime bg-lime/10 px-2 py-0.5 border border-lime flex items-center gap-1"><Zap className="w-3 h-3"/> FASTER</span>}
              </div>
            )}
          </div>

          {/* RIGHT PANEL */}
          <div className="w-full lg:w-1/2 bg-[#050508] flex flex-col min-h-[400px]">
            <div className="bg-card px-4 py-3 border-b border-border flex justify-between items-center text-xs">
               <div className="flex items-center gap-2">
                 <Zap className={`w-4 h-4 ${stats2.running ? 'text-orange animate-pulse' : 'text-purple'}`} />
                 <span className="font-bold">{agent2?.name || 'Agent 2'}</span>
               </div>
               <div className="text-dim">{stats2.time ? `${stats2.time.toFixed(2)}s` : stats2.running ? 'Running...' : 'Ready'}</div>
            </div>
            
            <div className="p-6 flex-1 text-sm text-primary/90 font-mono relative overflow-y-auto">
              {out2 && (
                <div className="prose prose-invert prose-sm max-w-none prose-a:text-purple prose-a:underline prose-headings:text-purple">
                  <ReactMarkdown>{out2}</ReactMarkdown>
                </div>
              )}
              {stats2.running && <span className="inline-block w-2 h-4 bg-purple animate-pulse ml-1 align-middle" />}
              {stats2.error && <div className="text-red-500 mt-4 border border-red-500/30 bg-red-500/10 p-4">{stats2.error}</div>}
              {!out2 && !stats2.running && !stats2.error && <div className="text-dim absolute inset-0 flex items-center justify-center italic">Awaiting initiation sequence...</div>}
            </div>
            
            {battleComplete && (
              <div className="p-4 bg-elevated border-t border-border flex justify-between items-center text-xs">
                <div>{out2.split(/\s+/).length} words internally</div>
                {winner.fastest === '2' && <span className="text-lime bg-lime/10 px-2 py-0.5 border border-lime flex items-center gap-1"><Zap className="w-3 h-3"/> FASTER</span>}
              </div>
            )}
          </div>
        </div>

        {/* RESULTS SCENE */}
        {battleComplete && (
          <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} className="mt-8 bg-card border border-border p-8 text-center shadow-[0_0_30px_rgba(0,245,255,0.1)]">
            <h3 className="font-display text-2xl text-primary font-bold mb-6">CAST YOUR VOTE</h3>
            {!winner.better ? (
              <div className="flex justify-center gap-6 text-sm">
                <button onClick={() => handleVote('1')} className="px-8 py-4 bg-void border border-cyan text-cyan hover:bg-cyan hover:text-void transition-colors font-bold w-48 truncate">{agent1?.name} Won</button>
                <div className="flex items-center text-dim font-bold">OR</div>
                <button onClick={() => handleVote('2')} className="px-8 py-4 bg-void border border-purple text-purple hover:bg-purple hover:text-void transition-colors font-bold w-48 truncate">{agent2?.name} Won</button>
              </div>
            ) : (
              <div className="w-full max-w-xl mx-auto">
                <div className="text-lime font-bold mb-4">Vote Recorded. Community Consensus:</div>
                <div className="flex w-full h-8 bg-elevated rounded-sm overflow-hidden mb-2">
                  <motion.div initial={{ width: 0 }} animate={{ width: winner.better === '1' ? '65%' : '35%' }} className="bg-cyan h-full flex items-center pl-2 text-[10px] text-void font-bold">A1</motion.div>
                  <motion.div initial={{ width: 0 }} animate={{ width: winner.better === '2' ? '65%' : '35%' }} className="bg-purple h-full flex items-center justify-end pr-2 text-[10px] text-void font-bold">A2</motion.div>
                </div>
                <div className="flex justify-between text-xs text-muted">
                  <span>{winner.better === '1' ? '65%' : '35%'} - {agent1?.name}</span>
                  <span>{winner.better === '2' ? '65%' : '35%'} - {agent2?.name}</span>
                </div>
              </div>
            )}
          </motion.div>
        )}
      </div>
    </div>
  );
}
