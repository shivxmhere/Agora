"use client";

import { motion } from 'framer-motion';
import Link from 'next/link';
import { useEffect, useState } from 'react';

function Counter({ end, duration = 2 }: { end: number; duration?: number }) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let startTime: number | null = null;
    const animate = (time: number) => {
      if (!startTime) startTime = time;
      const progress = Math.min((time - startTime) / (duration * 1000), 1);
      setCount(Math.floor(progress * end));
      if (progress < 1) requestAnimationFrame(animate);
    };
    requestAnimationFrame(animate);
  }, [end, duration]);

  return <span>{count.toLocaleString()}</span>;
}

export function Hero() {
  return (
    <div className="relative min-h-[90vh] flex flex-col justify-center items-center overflow-hidden">
      {/* Grid Background */}
      <div className="absolute inset-0 bg-grid-pattern opacity-60 pointer-events-none" />
      <div className="absolute inset-0 bg-gradient-to-t from-void via-transparent to-transparent pointer-events-none" />

      {/* Hero Content */}
      <div className="relative z-10 container mx-auto px-4 flex flex-col items-center text-center">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-2 bg-lime/10 border border-lime/30 text-lime px-4 py-1.5 rounded-full mb-8"
        >
          <div className="w-2 h-2 rounded-full bg-lime animate-pulse-glow" />
          <span className="font-mono text-xs font-bold tracking-wider">LIVE — 247 AGENTS DEPLOYED TODAY</span>
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="font-display font-bold text-5xl md:text-7xl mb-4 leading-tight"
        >
          The Open Marketplace<br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan to-purple">for AI Agents</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="text-muted text-lg md:text-xl max-w-2xl mb-10"
        >
          Discover. Deploy. Compose. Earn. One platform for every autonomous AI agent on the planet.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="flex flex-col sm:flex-row gap-4 mb-16"
        >
          <Link href="/marketplace">
            <button className="px-8 py-4 bg-cyan text-void font-bold rounded-sm border border-cyan hover:bg-transparent hover:text-cyan transition-colors group relative overflow-hidden">
              Explore Marketplace 
              <span className="inline-block transform group-hover:translate-x-1 transition-transform ml-2">→</span>
            </button>
          </Link>
          <button className="px-8 py-4 bg-transparent text-primary font-bold rounded-sm border border-border hover:border-text-dim transition-colors">
            Publish Your Agent
          </button>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5, duration: 1 }}
          className="font-mono text-sm text-dim bg-elevated/50 px-6 py-3 rounded-sm border border-border/50 backdrop-blur-sm"
        >
          <Counter end={1247} /> agents | <Counter end={48291} /> runs | <Counter end={342} /> creators
        </motion.div>
      </div>

      {/* Floating Decorative Cards */}
      <motion.div 
        className="hidden lg:block absolute right-[10%] top-[40%] w-64 h-32 bg-card/80 border border-cyan/30 backdrop-blur-md rounded-sm p-4 animate-float"
        style={{ animationDelay: '0s' }}
      >
        <div className="w-10 h-10 bg-cyan/20 rounded-sm mb-2" />
        <div className="w-3/4 h-2 bg-border rounded-full mb-2" />
        <div className="w-1/2 h-2 bg-border rounded-full" />
      </motion.div>

      <motion.div 
        className="hidden lg:block absolute left-[15%] top-[20%] w-48 h-48 bg-card/80 border border-purple/30 backdrop-blur-md rounded-sm p-4 animate-float"
        style={{ animationDelay: '1.5s' }}
      >
        <div className="w-full h-1/2 bg-purple/10 border-b border-purple/20 mb-2" />
        <div className="w-full h-2 bg-border rounded-full mb-2" />
        <div className="w-2/3 h-2 bg-border rounded-full" />
      </motion.div>

    </div>
  );
}
