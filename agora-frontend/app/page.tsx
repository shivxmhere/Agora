import { Hero } from '@/components/home/Hero';
import { LiveFeed } from '@/components/home/LiveFeed';
import { FeaturedAgents } from '@/components/home/FeaturedAgents';
import { Leaderboard } from '@/components/home/Leaderboard';

export default function Home() {
  return (
    <div className="w-full">
      <Hero />
      
      <div className="container mx-auto px-4 py-20">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
          <div className="lg:col-span-2">
            <FeaturedAgents />
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mt-12 mb-4">
              <div className="bg-void border border-orange p-8 hover:shadow-[0_0_30px_rgba(255,107,53,0.2)] transition-shadow flex flex-col group">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 bg-orange/10 border border-orange flex items-center justify-center text-orange group-hover:scale-110 transition-transform">⚔️</div>
                  <h3 className="font-display text-2xl font-bold text-white">Battle Mode</h3>
                </div>
                <p className="font-mono text-sm text-dim mb-8 flex-1">Compare outputs in real-time. Execute the same directive onto separate LLMs tracking performance, reasoning, and context retention side-by-side.</p>
                <a href="/battle" className="bg-orange text-void font-bold font-mono px-6 py-3 text-center hover:bg-transparent hover:text-orange border border-orange transition-colors">INITIATE BATTLE</a>
              </div>
              
              <div className="bg-void border border-purple p-8 hover:shadow-[0_0_30px_rgba(123,47,190,0.2)] transition-shadow flex flex-col group">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 bg-purple/10 border border-purple flex items-center justify-center text-purple group-hover:scale-110 transition-transform">🔗</div>
                  <h3 className="font-display text-2xl font-bold text-white">Agent Compose</h3>
                </div>
                <p className="font-mono text-sm text-dim mb-8 flex-1">Engineer advanced cognitive architectures. String models together feeding context sequentially to automate complete programmatic pipelines.</p>
                <a href="/compose" className="bg-purple text-void font-bold font-mono px-6 py-3 text-center hover:bg-transparent hover:text-purple border border-purple transition-colors">DESIGN PIPELINE</a>
              </div>
            </div>

            <Leaderboard />
          </div>
          <div>
             <LiveFeed />
          </div>
        </div>
      </div>
    </div>
  );
}
