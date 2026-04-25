import { Search } from 'lucide-react';

export function SearchBar({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  return (
    <div className="relative w-full max-w-2xl mx-auto mb-8">
      <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
        <Search className="h-5 w-5 text-muted" />
      </div>
      <input
        type="text"
        className="block w-full pl-12 pr-4 py-4 bg-elevated border border-border rounded-sm text-primary placeholder-muted focus:outline-none focus:ring-1 focus:ring-cyan focus:border-cyan transition-all"
        placeholder="Search agents, capabilities, or tags..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
}
