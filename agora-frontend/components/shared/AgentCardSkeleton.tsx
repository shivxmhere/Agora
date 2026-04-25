export function AgentCardSkeleton() {
  return (
    <div className="border border-border bg-card rounded-none p-5 animate-pulse">
      <div className="flex justify-between mb-4">
        <div className="h-5 w-24 bg-elevated rounded" />
        <div className="h-5 w-12 bg-elevated rounded" />
      </div>
      <div className="h-12 w-12 bg-elevated rounded mb-3" />
      <div className="h-5 w-3/4 bg-elevated rounded mb-2" />
      <div className="h-4 w-full bg-elevated rounded mb-1" />
      <div className="h-4 w-2/3 bg-elevated rounded mb-4" />
      <div className="flex gap-2 mb-4">
        <div className="h-6 w-16 bg-elevated rounded" />
        <div className="h-6 w-16 bg-elevated rounded" />
        <div className="h-6 w-16 bg-elevated rounded" />
      </div>
      <div className="h-9 w-full bg-elevated rounded" />
    </div>
  );
}
