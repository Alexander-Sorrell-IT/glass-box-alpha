"use client";

import { AGENT_META, type AgentKey } from "@/lib/contracts";

export interface ReasoningStep {
  agent: AgentKey;
  step: number;
  thought: string;
  ts: number;
}

interface ReasoningStreamProps {
  steps: ReasoningStep[];
  maxRows?: number;
}

export function ReasoningStream({ steps, maxRows = 12 }: ReasoningStreamProps) {
  const visible = steps.slice(-maxRows);

  return (
    <div className="panel p-4">
      <div className="flex items-baseline justify-between mb-3">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-signal-neutral">
          Reasoning Stream
        </h2>
        <span className="badge bg-border text-signal-neutral">{steps.length} steps</span>
      </div>
      <div className="space-y-2 font-mono text-xs">
        {visible.length === 0 ? (
          <p className="text-signal-neutral/50 italic">Waiting for first signal…</p>
        ) : (
          visible.map((s, i) => (
            <div key={`${s.agent}-${s.step}-${i}`} className="flex gap-2 animate-reasoning-fade">
              <span className={`shrink-0 ${AGENT_META[s.agent].color}`}>{AGENT_META[s.agent].name}</span>
              <span className="text-signal-neutral/50">·</span>
              <span className="text-signal-neutral/40 w-6">{s.step}</span>
              <span className="text-signal-neutral/90 leading-relaxed">{s.thought}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
