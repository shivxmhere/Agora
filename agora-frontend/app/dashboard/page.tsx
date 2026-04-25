"use client";

import { useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { AreaChart, Area, XAxis, YAxis, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts';
import { Shield, Zap, TrendingUp, Star, Play, Edit, PauseCircle } from 'lucide-react';
import Link from 'next/link';

export default function DashboardPage() {
  const searchParams = useSearchParams();
  const [creator, setCreator] = useState(searchParams.get('creator') || '');
  const [inputVal, setInputVal] = useState(creator);
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!creator) return;
    setIsLoading(true);
    api.getAnalytics(creator)
      .then(res => { setData(res); setIsLoading(false); })
      .catch(err => { console.error(err); setIsLoading(false); });
  }, [creator]);

  if (!creator) {
    return (
      <div className="min-h-screen container mx-auto px-4 py-20 flex flex-col items-center justify-center font-mono">
        <Shield className="w-16 h-16 text-cyan mb-6" />
        <h1 className="font-display text-3xl font-bold text-white mb-4">CREATOR AUTHENTICATION</h1>
        <p className="text-muted mb-8 text-center max-w-md">Enter your registry handle to access telemetry and financial data for your deployed agents.</p>
        <div className="flex w-full max-w-sm">
          <input type="text" placeholder="e.g. @0xDeveloper" value={inputVal} onChange={e => setInputVal(e.target.value)} onKeyDown={e => e.key === 'Enter' && setCreator(inputVal)} className="flex-1 bg-elevated border border-border p-3 text-white focus:outline-none focus:border-cyan" />
          <button onClick={() => setCreator(inputVal)} className="bg-cyan border border-cyan text-void font-bold px-6 hover:bg-transparent hover:text-cyan transition-colors">ACCESS</button>
        </div>
      </div>
    );
  }

  if (isLoading || !data) return <div className="min-h-screen pt-24 px-4 text-center font-mono text-cyan animate-pulse">Syncing telemetry data...</div>;

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl font-mono">
      {/* HEADER */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-12 border-b border-border pb-6">
        <div>
          <h1 className="font-display text-4xl mb-2 text-primary font-bold">AGORA CREATOR DASHBOARD</h1>
          <div className="flex items-center gap-4">
            <span className="text-cyan text-xl">[{creator}]</span>
            <div className="flex items-center gap-1 bg-elevated border border-border px-2 py-0.5 text-xs text-muted"> <Zap className="w-3 h-3 text-cyan fill-cyan" /> SCORE: 9.8 </div>
            <span className="bg-purple/10 text-purple border border-purple/30 px-2 py-0.5 text-[10px] tracking-wider font-bold">TOP CREATOR</span>
          </div>
        </div>
        <div className="mt-6 md:mt-0">
          <Link href="/publish"><button className="bg-cyan/10 border border-cyan text-cyan hover:bg-cyan hover:text-void px-6 py-2 transition-colors font-bold text-sm">Deploy New Agent</button></Link>
        </div>
      </div>

      {/* SUMMARY CARDS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        <div className="bg-card border border-border p-6 shadow-[0_0_15px_rgba(0,0,0,0.3)]">
          <div className="text-muted text-xs mb-2 flex justify-between">TOTAL RUNS <TrendingUp className="w-4 h-4 text-cyan" /></div>
          <div className="font-display text-4xl text-white">{data.total_runs.toLocaleString()}</div>
        </div>
        <div className="bg-card border border-border p-6 shadow-[0_0_15px_rgba(0,0,0,0.3)]">
          <div className="text-muted text-xs mb-2 flex justify-between">AVG RATING <Star className="w-4 h-4 text-lime" /></div>
          <div className="font-display text-4xl text-white">{data.avg_rating.toFixed(1)}</div>
        </div>
        <div className="bg-card border border-border p-6 shadow-[0_0_15px_rgba(0,0,0,0.3)]">
          <div className="text-muted text-xs mb-2 flex justify-between">TOTAL EARNED <span className="text-orange">$</span></div>
          <div className="font-display text-4xl text-white">${data.total_earned.toFixed(2)}</div>
        </div>
        <div className="bg-card border border-border p-6 shadow-[0_0_15px_rgba(0,0,0,0.3)]">
          <div className="text-muted text-xs mb-2 flex justify-between">AGENTS LIVE <Zap className="w-4 h-4 text-purple" /></div>
          <div className="font-display text-4xl text-white">{data.agents_live}</div>
        </div>
      </div>

      {/* CHARTS */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-12">
        <div className="lg:col-span-2 bg-card border border-border p-6">
          <h3 className="text-sm font-bold text-muted mb-6">NETWORK EXECUTION TRAFFIC (7 DAYS)</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.runs_by_day}>
                <defs>
                  <linearGradient id="cyanGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00F5FF" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#00F5FF" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="date" stroke="#374151" fontSize={10} tickMargin={10} />
                <YAxis stroke="#374151" fontSize={10} />
                <RechartsTooltip contentStyle={{ backgroundColor: '#050508', borderColor: '#1A1A2E', color: '#F0F0FF' }} />
                <Area type="monotone" dataKey="runs" stroke="#00F5FF" strokeWidth={2} fillOpacity={1} fill="url(#cyanGradient)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        <div className="bg-card border border-border p-6">
          <h3 className="text-sm font-bold text-muted mb-6">RUNS BY AGENT</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.runs_by_agent} layout="vertical" margin={{ top: 0, right: 0, left: 30, bottom: 0 }}>
                <XAxis type="number" hide />
                <YAxis dataKey="agent_name" type="category" stroke="#6B7280" fontSize={10} tickLine={false} axisLine={false} />
                <RechartsTooltip contentStyle={{ backgroundColor: '#050508', borderColor: '#1A1A2E' }} cursor={{fill: '#111119'}}/>
                <Bar dataKey="runs" radius={[0, 4, 4, 0]}>
                  {data.runs_by_agent.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={['#00F5FF', '#7B2FBE', '#A8FF3E', '#FF6B35'][index % 4]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* BOTTOM SECTION */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-16">
        <div>
           <h3 className="font-display text-xl text-primary font-bold mb-4 border-b border-border pb-2">Recent Agent Activity</h3>
           <div className="space-y-3">
             {data.recent_runs.length === 0 ? <div className="text-dim text-sm h-32 flex items-center justify-center border border-dashed border-border">No recent runs recorded.</div> : null}
             {data.recent_runs.map((r: any, i: number) => (
               <div key={i} className="flex flex-col sm:flex-row justify-between sm:items-center bg-elevated border border-border p-3 text-xs gap-4">
                 <div>
                   <div className="text-cyan font-bold mb-1">{r.agent_name}</div>
                   <div className="text-muted truncate max-w-xs">&gt; {r.input_preview}</div>
                 </div>
                 <div className="flex flex-row sm:flex-col items-center sm:items-end justify-between gap-1">
                   <span className="text-lime">{r.status.toUpperCase()}</span>
                   <span className="text-dim">{r.created_at}</span>
                 </div>
               </div>
             ))}
           </div>
        </div>

        <div>
           <h3 className="font-display text-xl text-primary font-bold mb-4 border-b border-border pb-2">Instance Management</h3>
           <div className="bg-card border border-border overflow-x-auto">
             <table className="w-full text-left text-sm whitespace-nowrap">
               <thead className="bg-[#0a0a10] border-b border-border text-dim text-xs">
                 <tr>
                   <th className="font-normal px-4 py-3">NAME</th>
                   <th className="font-normal px-4 py-3">STATUS</th>
                   <th className="font-normal px-4 py-3">ACTIONS</th>
                 </tr>
               </thead>
               <tbody>
                 {data.runs_by_agent.map((r: any, i: number) => (
                   <tr key={i} className="border-b border-border border-dashed hover:bg-elevated/50 transition-colors">
                     <td className="px-4 py-3 text-cyan">{r.agent_name}</td>
                     <td className="px-4 py-3"><span className="text-[10px] bg-lime/10 border border-lime text-lime px-2 py-0.5">LIVE</span></td>
                     <td className="px-4 py-3 flex gap-4">
                       <button className="text-muted hover:text-white flex items-center gap-1 text-[10px] uppercase"><Edit className="w-3 h-3"/> Edit</button>
                       <button className="text-muted hover:text-orange flex items-center gap-1 text-[10px] uppercase"><PauseCircle className="w-3 h-3"/> Suspend</button>
                     </td>
                   </tr>
                 ))}
                 {data.runs_by_agent.length === 0 && <tr><td colSpan={3} className="text-center p-8 text-dim">No deployed agents found.</td></tr>}
               </tbody>
             </table>
           </div>
        </div>
      </div>
    </div>
  );
}
