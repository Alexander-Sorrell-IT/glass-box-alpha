"use client";

import { useIsLive, useRoundsCount, useCommitsCount } from "@/lib/useGlassBox";

/// Header badge: shows whether the UI is reading live on-chain data or running
/// on demo fixtures. Once contracts deploy (Day 7 Sepolia / Day 14 Mainnet),
/// this flips to "LIVE" and surfaces real round + commit counters.
export function LiveStatus() {
  const { isLive } = useIsLive();
  const { roundsCount } = useRoundsCount();
  const { commitsCount } = useCommitsCount();

  if (!isLive) {
    return (
      <div className="flex items-center gap-2 badge bg-border text-signal-neutral">
        <span className="w-2 h-2 rounded-full bg-signal-neutral" />
        Demo Mode — contracts not yet deployed
      </div>
    );
  }

  return (
    <div className="flex items-center gap-4">
      <div className="flex items-center gap-2 badge bg-signal-bull/15 text-signal-bull">
        <span className="w-2 h-2 rounded-full bg-signal-bull animate-pulse" />
        LIVE on Mantle
      </div>
      {roundsCount !== undefined && (
        <span className="text-xs text-signal-neutral font-mono">{roundsCount} rounds</span>
      )}
      {commitsCount !== undefined && (
        <span className="text-xs text-signal-neutral font-mono">{commitsCount} reasoning commits</span>
      )}
    </div>
  );
}
