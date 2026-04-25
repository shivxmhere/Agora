"use client";
import { Component, ReactNode } from "react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}
interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <div className="flex flex-col items-center justify-center min-h-[300px] text-center p-8 border border-red-500/20 bg-red-500/5">
            <div className="text-4xl mb-4">⚡</div>
            <h3 className="text-cyan font-mono text-xl mb-2">
              Agent Encountered an Error
            </h3>
            <p className="text-muted text-sm mb-6 font-mono">
              {this.state.error?.message || "Something went wrong. The agent will recover."}
            </p>
            <button
              onClick={() => this.setState({ hasError: false })}
              className="border border-cyan text-cyan px-6 py-2 font-mono hover:bg-cyan/10 transition-colors"
            >
              TRY AGAIN
            </button>
          </div>
        )
      );
    }
    return this.props.children;
  }
}
