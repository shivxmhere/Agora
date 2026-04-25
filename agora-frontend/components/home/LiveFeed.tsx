"use client";

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '@/lib/api';
import { ActivityItem } from '@/lib/types';
import useSWR from 'swr';
import { Zap } from 'lucide-react';

export function LiveFeed() {
  const { data: initialFeed } = useSWR<ActivityItem[]>('activityFeed', api.getActivity, {
    refreshInterval: 5000,
    fallbackData: []
  });

  const [feed, setFeed] = useState<ActivityItem[]>([]);

  useEffect(() => {
    // We can also connect to websocket here for instant updates
    const wsUrl = process.env.NEXT_PUBLIC_BACKEND_URL ? 
      process.env.NEXT_PUBLIC_BACKEND_URL.replace('http', 'ws') + '/ws/activity' : 
      'ws://localhost:8000/ws/activity';
      
    const ws = new WebSocket(wsUrl);
    
    ws.onmessage = (event) => {
      try {
        const newEvent = JSON.parse(event.data);
        const item: ActivityItem = {
          id: Math.random().toString(),
          agent_name: newEvent.agent_name,
          action: newEvent.action,
          location: newEvent.location,
          time: newEvent.time,
          created_at: new Date().toISOString()
        };
        setFeed(prev => [item, ...prev].slice(0, 20)); // Keep max 20
      } catch (e) {}
    };

    return () => ws.close();
  }, []);

  // Sync initial feed from SWR on first load if our ws feed is empty
  useEffect(() => {
    if (initialFeed && initialFeed.length > 0 && feed.length === 0) {
      setFeed(initialFeed);
    }
  }, [initialFeed, feed.length]);

  return (
    <div className="w-full bg-card border border-cyan/30 rounded-sm p-4 relative overflow-hidden backdrop-blur-sm">
      <div className="flex items-center gap-2 mb-4 border-b border-border pb-2">
        <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse-glow" />
        <h3 className="font-mono text-sm tracking-widest text-primary">LIVE ACTIVITY</h3>
      </div>

      <div className="h-64 overflow-y-auto no-scrollbar relative">
        <AnimatePresence>
          {feed.map((item) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, x: -20, height: 0 }}
              animate={{ opacity: 1, x: 0, height: 'auto' }}
              exit={{ opacity: 0 }}
              className="flex items-center gap-3 py-3 border-b border-border/50 font-mono text-xs"
            >
              <div className="w-6 h-6 rounded-full bg-elevated border border-border flex items-center justify-center text-cyan flex-shrink-0">
                <Zap className="w-3 h-3" />
              </div>
              <div className="flex-1">
                <span className="text-muted">User from {item.location} </span>
                <span className="text-cyan">{item.action} </span>
                <span className="text-primary">{item.agent_name}</span>
              </div>
              <span className="text-dim whitespace-nowrap">{item.time || 'just now'}</span>
            </motion.div>
          ))}
        </AnimatePresence>
        
        {feed.length === 0 && (
          <div className="text-muted font-mono text-xs py-4 text-center">Waiting for activity...</div>
        )}
      </div>
    </div>
  );
}
