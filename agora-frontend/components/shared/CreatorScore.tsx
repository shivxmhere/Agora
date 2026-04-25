import { Zap } from 'lucide-react';
import { cn } from '@/lib/utils';

export function CreatorScore({ score, className }: { score: number; className?: string }) {
  return (
    <div className={cn("flex items-center gap-1 text-cyan", className)}>
      <Zap className="w-3 h-3 fill-cyan" />
      <span className="font-mono text-xs">{score.toFixed(1)}</span>
    </div>
  );
}
