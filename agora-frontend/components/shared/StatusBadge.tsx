import { cn } from '@/lib/utils';

export function StatusBadge({ status, className }: { status: 'live' | 'beta' | 'deprecated'; className?: string }) {
  const isLive = status === 'live';
  return (
    <div className={cn(
      "px-2 py-0.5 text-xs font-mono border rounded-sm flex items-center gap-1.5",
      isLive ? "border-lime text-lime" : "border-orange text-orange",
      className
    )}>
      <div className={cn("w-1.5 h-1.5 rounded-full animate-pulse-glow", isLive ? "bg-lime" : "bg-orange")} />
      {status.toUpperCase()}
    </div>
  );
}
