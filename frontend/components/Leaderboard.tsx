"use client";

interface LeaderboardRow {
  rank: number;
  name: string;
  isAgent: boolean;
  agentId?: number;
  walletAddress?: string;
  trades: number;
  winRatePct: number;
  pnlPct: number;
}

interface LeaderboardProps {
  rows: LeaderboardRow[];
}

export function Leaderboard({ rows }: LeaderboardProps) {
  return (
    <div className="panel p-4">
      <h2 className="text-sm font-semibold uppercase tracking-wider text-signal-neutral mb-3">
        AI vs Human Leaderboard
      </h2>
      <div className="space-y-1">
        <div className="grid grid-cols-12 gap-2 text-xs text-signal-neutral px-2 pb-1 border-b border-border">
          <span className="col-span-1">#</span>
          <span className="col-span-5">Trader</span>
          <span className="col-span-2 text-right">Trades</span>
          <span className="col-span-2 text-right">Win %</span>
          <span className="col-span-2 text-right">PnL</span>
        </div>
        {rows.length === 0 ? (
          <p className="text-signal-neutral italic text-xs px-2 py-3">
            No trades settled yet.
          </p>
        ) : (
          rows.map((r) => (
            <div
              key={`${r.rank}-${r.name}`}
              className="grid grid-cols-12 gap-2 text-sm px-2 py-1.5 rounded hover:bg-panelHover transition-colors"
            >
              <span className="col-span-1 text-signal-neutral/60">{r.rank}</span>
              <span className="col-span-5 flex items-center gap-2">
                <span className={`badge text-[10px] ${r.isAgent ? "bg-accent/15 text-accent" : "bg-border text-signal-neutral"}`}>
                  {r.isAgent ? "AI" : "HUMAN"}
                </span>
                {r.name}
              </span>
              <span className="col-span-2 text-right font-mono text-signal-neutral/80">{r.trades}</span>
              <span className="col-span-2 text-right font-mono">{r.winRatePct.toFixed(1)}%</span>
              <span
                className={`col-span-2 text-right font-mono ${r.pnlPct >= 0 ? "text-signal-bull" : "text-signal-bear"}`}
              >
                {r.pnlPct >= 0 ? "+" : ""}{r.pnlPct.toFixed(2)}%
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
