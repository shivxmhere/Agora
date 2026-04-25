import useSWR from 'swr';
import { api } from '@/lib/api';
import { Agent } from '@/lib/types';

export function useAgents(params?: Record<string, string>) {
  const { data, error, isLoading, mutate } = useSWR<Agent[]>(
    ['agents', params],
    ([, p]) => api.getAgents(p as Record<string, string>)
  );

  return {
    agents: data,
    isLoading,
    isError: error,
    mutate
  };
}

export function useAgent(id: string) {
  const { data, error, isLoading, mutate } = useSWR<Agent>(
    id ? `agent-${id}` : null,
    () => api.getAgent(id)
  );

  return {
    agent: data,
    isLoading,
    isError: error,
    mutate
  };
}
