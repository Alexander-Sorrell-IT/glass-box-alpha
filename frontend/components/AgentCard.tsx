"use client";

import { AGENT_META, type AgentKey } from "@/lib/contracts";

interface AgentCardProps {
  agentKey: AgentKey;
  signal: number; // -1 to 1
  confidence: number; // 0 to 1
  reasoningPreview?: string;
  pnlBps?: number;
}

export function AgentCard({ agentKey, signal, confidence, reasoningPreview, pnlBps }: AgentCardProps) {
  const meta = AGENT_META[agentKey];
  const signalColor =
    signal > 0.05 ? "text-signal-bull" : signal < -0.05 ? "text-signal-bear" : "text-signal-neutral";
  const signalText = signal > 0 ? `+${signal.toFixed(2)}` : signal.toFixed(2);

  return (
    <div className="panel p-4 space-y-3">
      <div className="flex items-baseline justify-between">
        <h3 className={`text-lg font-semibold ${meta.color}`}>{meta.name}</h3>
        <span className="badge bg-border text-signal-neutral">{meta.operator}</span>
      </div>
      <p className="text-sm text-signal-neutral">{meta.role}</p>

      <div className="flex items-baseline gap-3 pt-1">
        <span className={`text-2xl font-mono ${signalColor}`}>{signalText}</span>
        <span className="text-xs text-signal-neutral">
          conf {(confidence * 100).toFixed(0)}%
        </span>
        {pnlBps !== undefined && (
          <span
            className={`badge ml-auto ${pnlBps >= 0 ? "bg-signal-bull/15 text-signal-bull" : "bg-signal-bear/15 text-signal-bear"}`}
          >
            PnL {pnlBps >= 0 ? "+" : ""}{(pnlBps / 100).toFixed(2)}%
          </span>
        )}
      </div>

      {reasoningPreview && (
        <p className="text-xs text-signal-neutral/80 line-clamp-3 font-mono leading-relaxed">
          {reasoningPreview}
        </p>
      )}
    </div>
  );
}
