"use client";
import { useState, useRef, useCallback, useEffect } from "react";

export type RunStatus = "idle" | "starting" | "running" | "completed" | "error";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "";

export function useAgentRunner(agentId: string) {
  const [status, setStatus] = useState<RunStatus>("idle");
  const [output, setOutput] = useState("");
  const [runTime, setRunTime] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [elapsed, setElapsed] = useState(0);

  const eventSourceRef = useRef<EventSource | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const elapsedRef = useRef(0);

  const detectStep = useCallback((token: string) => {
    const lower = token.toLowerCase();
    if (lower.includes("searching")) setCurrentStep(1);
    else if (lower.includes("reading") || lower.includes("scraping")) setCurrentStep(2);
    else if (lower.includes("analyz")) setCurrentStep(3);
    else if (lower.includes("fact") || lower.includes("verif")) setCurrentStep(4);
    else if (lower.includes("report") || lower.includes("synthes") || lower.includes("generat")) setCurrentStep(5);
  }, []);

  const reset = useCallback(() => {
    eventSourceRef.current?.close();
    if (timerRef.current) clearInterval(timerRef.current);
    setStatus("idle");
    setOutput("");
    setError(null);
    setCurrentStep(0);
    setElapsed(0);
    elapsedRef.current = 0;
  }, []);

  const run = useCallback(
    async (input: string) => {
      if (!input.trim()) return;
      reset();

      setStatus("starting");

      timerRef.current = setInterval(() => {
        elapsedRef.current += 1;
        setElapsed(elapsedRef.current);
      }, 1000);

      try {
        const sessionId = crypto.randomUUID();

        const res = await fetch(`${BACKEND_URL}/api/agents/${agentId}/run`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ input: input.trim(), session_id: sessionId }),
        });

        if (!res.ok) {
          const err = await res.json().catch(() => ({ detail: "Failed to start agent" }));
          throw new Error(err.detail || `HTTP ${res.status}`);
        }

        const { run_id } = await res.json();
        setStatus("running");

        const streamUrl = `${BACKEND_URL}/api/runs/${run_id}/stream`;
        const es = new EventSource(streamUrl);
        eventSourceRef.current = es;

        es.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.type === "token") {
              setOutput((prev) => prev + data.content);
              detectStep(data.content);
            } else if (data.type === "done") {
              setStatus("completed");
              setRunTime(data.run_time ?? 0);
              setCurrentStep(6);
              if (timerRef.current) clearInterval(timerRef.current);
              es.close();
            } else if (data.type === "error") {
              throw new Error(data.message);
            }
          } catch (parseErr) {
            // Individual event parse failures are non-fatal
          }
        };

        es.onerror = () => {
          // SSE connection closing after done is normal — only flag error if still running
          setStatus((s) => {
            if (s === "running") return "completed";
            return s;
          });
          if (timerRef.current) clearInterval(timerRef.current);
          es.close();
        };
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : "Something went wrong";
        setStatus("error");
        setError(msg);
        if (timerRef.current) clearInterval(timerRef.current);
      }
    },
    [agentId, detectStep, reset]
  );

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      eventSourceRef.current?.close();
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  return { run, reset, status, output, runTime, error, currentStep, elapsed };
}
