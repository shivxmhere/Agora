"use client";

import { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { AreaChart, Area, XAxis, YAxis, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts';
import { Shield, Zap, TrendingUp, Star, Play, Edit, PauseCircle } from 'lucide-react';
import Link from 'next/link';

function DashboardContent() {
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
          <input type="text" placeholder="e.g. shivxmhere" value={inputVal} onChange={e => setInputVal(e.target.value)} onKeyDown={e => e.key === 'Enter' && setCreator(inputVal)} className="flex-1 bg-elevated border border-border p-3 text-white focus:outline-none focus:border-cyan" />
          <button onClick={() => setCreator(inputVal)} className="bg-cyan border border-cyan text-void font-bold px-6 hover:bg-transparent hover:text-cyan transition-colors">ACCESS</button>
        </div>
        <div className="mt-6 text-xs text-muted">
          Try: <button onClick={() => { setCreator('shivxmhere'); setInputVal('shivxmhere'); }} className="text-cyan hover:underline">shivxmhere</button> · <button onClick={() => { setCreator('aditya_dev'); setInputVal('aditya_dev'); }} className="text-cyan hover:underline">aditya_dev</button>
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
            <div className="flex items-center gap-1 bg-elevated border border-border px-2 py-0.5 text-xs text-muted"> <Zap className="w-3 h-3 text-cyan fill-cyan" /> SCORE: 9.4 </div>
            <span className="bg-purple/10 text-purple border border-purple/30 px-2 py-0.5 text-[10px] tracking-wider font-bold">TOP CREATOR</span>
          </div>
        </div>
        <div className="mt-6 md:mt-0">
          <Link href="/publish"><button className="bg-cyan/10 border border-cyan text-cyan hover:bg-cyan hover:text-void px-6 py-2 transition-colors font-bold text-sm">Deploy New Agent</button></Link>
        </div>
      </div>

      {/* SUMMARY CARDS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        <div className="bg-card border border-border p-6">
          <div className="text-muted text-xs mb-2 flex justify-between">TOTAL RUNS <TrendingUp className="w-4 h-4 text-cyan" /></div>
          <div className="font-display text-4xl text-white">{(data.total_runs || 0).toLocaleString()}</div>
        </div>
        <div className="bg-card border border-border p-6">
          <div className="text-muted text-xs mb-2 flex justify-between">AVG RATING <Star className="w-4 h-4 text-lime" /></div>
          <div className="font-display text-4xl text-white">{(data.avg_rating || 0).toFixed(1)}</div>
        </div>
        <div className="bg-card border border-border p-6">
          <div className="text-muted text-xs mb-2 flex justify-between">TOTAL EARNED <span className="text-orange">$</span></div>
          <div className="font-display text-4xl text-white">${(data.total_earned || 0).toFixed(2)}</div>
        </div>
        <div className="bg-card border border-border p-6">
          <div className="text-muted text-xs mb-2 flex justify-between">AGENTS LIVE <Zap className="w-4 h-4 text-purple" /></div>
          <div className="font-display text-4xl text-white">{data.agents_live || 0}</div>
        </div>
      </div>

      {/* CHARTS */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-12">
        <div className="lg:col-span-2 bg-card border border-border p-6">
          <h3 className="text-sm font-bold text-muted mb-6">NETWORK EXECUTION TRAFFIC (7 DAYS)</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.runs_by_day || []}>
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
              <BarChart data={data.runs_by_agent || []} layout="vertical" margin={{ top: 0, right: 0, left: 30, bottom: 0 }}>
                <XAxis type="number" hide />
                <YAxis dataKey="agent_name" type="category" stroke="#6B7280" fontSize={10} tickLine={false} axisLine={false} />
                <RechartsTooltip contentStyle={{ backgroundColor: '#050508', borderColor: '#1A1A2E' }} cursor={{fill: '#111119'}}/>
                <Bar dataKey="runs" radius={[0, 4, 4, 0]}>
                  {(data.runs_by_agent || []).map((_: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={['#00F5FF', '#7B2FBE', '#A8FF3E', '#FF6B35'][index % 4]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <Suspense fallback={<div className="min-h-screen pt-24 px-4 text-center font-mono text-cyan animate-pulse">Loading dashboard...</div>}>
      <DashboardContent />
    </Suspense>
  );
}
