"use client";

import { useState } from 'react';
import { useAgents } from '@/hooks/useAgents';
import { SearchBar } from '@/components/marketplace/SearchBar';
import { CategoryFilter } from '@/components/marketplace/CategoryFilter';
import { SortControls } from '@/components/marketplace/SortControls';
import { AgentGrid } from '@/components/marketplace/AgentGrid';

export default function MarketplacePage() {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("All");
  const [sort, setSort] = useState("newest");

  // Construct query params safely
  const queryParams: Record<string, string> = { sort };
  if (category !== 'All') queryParams.category = category;
  if (search) queryParams.search = search;

  const { agents, isLoading } = useAgents(queryParams);

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="mb-12">
        <h1 className="font-display text-4xl mb-4 font-bold tracking-tight">Marketplace</h1>
        <p className="text-muted max-w-2xl">
          Discover and compose the most powerful autonomous agents. Filter by category, capability, or performance metrics.
        </p>
      </div>

      <SearchBar value={search} onChange={setSearch} />

      <div className="flex flex-col md:flex-row justify-between items-start md:items-center">
        <CategoryFilter current={category} onChange={setCategory} />
        <SortControls current={sort} onChange={setSort} />
      </div>

      <AgentGrid agents={agents} isLoading={isLoading} />
    </div>
  );
}
