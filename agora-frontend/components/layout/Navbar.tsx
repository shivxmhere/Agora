"use client";

import Link from 'next/link';
import { motion } from 'framer-motion';

export default function Navbar() {
  return (
    <nav className="sticky top-0 z-50 w-full backdrop-blur-md bg-void/80 border-b border-border">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 group">
          {/* Logo SVG Text */}
          <div className="flex items-center">
            <span className="font-display font-bold text-2xl text-cyan tracking-wider">AGORA</span>
            <div className="w-2 h-2 rounded-full bg-cyan ml-1 animate-pulse-glow" />
          </div>
        </Link>
        
        <div className="hidden md:flex items-center gap-6 text-sm font-mono font-bold">
        <Link href="/marketplace" className="text-muted hover:text-primary transition-colors">[/marketplace]</Link>
        <Link href="/compose" className="text-muted hover:text-cyan transition-colors">[/compose]</Link>
        <Link href="/battle" className="text-muted hover:text-orange transition-colors">[/battle]</Link>
        <Link href="/publish" className="text-muted hover:text-purple transition-colors">[/publish]</Link>
      </div>

        <div>
          <motion.button 
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="font-mono text-sm border border-cyan text-cyan px-4 py-2 rounded-sm hover:bg-cyan hover:text-void transition-colors"
          >
            Launch Agent
          </motion.button>
        </div>
      </div>
    </nav>
  );
}
