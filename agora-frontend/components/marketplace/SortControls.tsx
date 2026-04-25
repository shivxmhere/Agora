export function SortControls({ current, onChange }: { current: string; onChange: (v: string) => void }) {
  return (
    <div className="flex items-center gap-2 mb-6">
      <span className="text-sm text-muted font-mono">Sort by:</span>
      <select 
        className="bg-elevated border border-border text-primary text-sm font-mono p-2 rounded-sm focus:outline-none focus:border-cyan"
        value={current}
        onChange={(e) => onChange(e.target.value)}
      >
        <option value="newest">Newest</option>
        <option value="rating">Rating</option>
        <option value="runs">Most Used</option>
      </select>
    </div>
  );
}
