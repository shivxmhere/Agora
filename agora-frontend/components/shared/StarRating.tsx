import { Star } from 'lucide-react';
import { cn } from '@/lib/utils';

export function StarRating({ rating, className }: { rating: number; className?: string }) {
  return (
    <div className={cn("flex items-center gap-1", className)}>
      <Star className="w-3 h-3 fill-lime text-lime" />
      <span className="font-mono text-sm text-lime">{rating.toFixed(1)}</span>
    </div>
  );
}
