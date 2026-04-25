import { Hero } from '@/components/home/Hero';
import { LiveFeed } from '@/components/home/LiveFeed';
import { FeaturedAgents } from '@/components/home/FeaturedAgents';

export default function Home() {
  return (
    <div className="w-full">
      <Hero />
      
      <div className="container mx-auto px-4 py-20">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
          <div className="lg:col-span-2">
            <FeaturedAgents />
          </div>
          <div>
             <LiveFeed />
          </div>
        </div>
      </div>
    </div>
  );
}
