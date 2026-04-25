import { cn } from '@/lib/utils';

const CATEGORIES = ["All", "Research", "Developer Tools", "Creative", "Business", "Analytics", "Automation"];

export function CategoryFilter({ current, onChange }: { current: string; onChange: (c: string) => void }) {
  return (
    <div className="flex overflow-x-auto pb-4 gap-2 no-scrollbar mb-6">
      {CATEGORIES.map((cat) => (
        <button
          key={cat}
          onClick={() => onChange(cat)}
          className={cn(
            "px-4 py-2 font-mono text-sm whitespace-nowrap border rounded-sm transition-colors",
            current === cat 
              ? "bg-cyan text-void border-cyan" 
              : "bg-elevated text-muted border-border hover:border-muted hover:text-primary"
          )}
        >
          {cat}
        </button>
      ))}
    </div>
  );
}
