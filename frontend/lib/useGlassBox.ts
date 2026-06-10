"use client";

import { useReadContract, useReadContracts } from "wagmi";
import {
  ROUND_STATE_MAINNET,
  REASONING_HASH_ANCHOR_MAINNET,
  SOVEREIGN_REASONING_COIN_MAINNET,
  AGENT_IDS,
  type AgentKey,
} from "./contracts";
import { roundStateAbi, reputationTokenAbi, reasoningAnchorAbi } from "./abis";

// All hooks gracefully no-op (return undefined) until contract addresses are
// set post-deploy (Day 7 Sepolia / Day 14 Mainnet). Components fall back to
// demo fixtures when data is undefined.

const repTokenAddress = SOVEREIGN_REASONING_COIN_MAINNET; // ReasoningRepToken (renamed)

function isDeployed(addr: string): addr is `0x${string}` {
  return addr.length === 42 && addr.startsWith("0x");
}

/** Total number of rounds opened on-chain. */
export function useRoundsCount() {
  const { data, isLoading } = useReadContract({
    address: isDeployed(ROUND_STATE_MAINNET) ? ROUND_STATE_MAINNET : undefined,
    abi: roundStateAbi,
    functionName: "roundsCount",
    query: { enabled: isDeployed(ROUND_STATE_MAINNET), refetchInterval: 15_000 },
  });
  return { roundsCount: data ? Number(data) : undefined, isLoading };
}

export interface OnChainRound {
  marketId: `0x${string}`;
  opener: `0x${string}`;
  openedAt: number;
  settledAt: number;
  status: number; // 0 Open, 1 Pending, 2 Settled, 3 Cancelled
  ensembleSignal: number; // normalized from 1e18
  realizedPnlBps: number;
  submissionsCount: number;
}

/** Read a single round's state. */
export function useRound(roundId: number | undefined) {
  const { data, isLoading } = useReadContract({
    address: isDeployed(ROUND_STATE_MAINNET) ? ROUND_STATE_MAINNET : undefined,
    abi: roundStateAbi,
    functionName: "getRound",
    args: roundId !== undefined ? [BigInt(roundId)] : undefined,
    query: { enabled: isDeployed(ROUND_STATE_MAINNET) && roundId !== undefined, refetchInterval: 15_000 },
  });

  if (!data) return { round: undefined, isLoading };

  const [marketId, opener, openedAt, settledAt, status, ensembleSignal, realizedPnlBps, submissionsCount] =
    data as readonly [`0x${string}`, `0x${string}`, bigint, bigint, number, bigint, bigint, bigint];

  const round: OnChainRound = {
    marketId,
    opener,
    openedAt: Number(openedAt),
    settledAt: Number(settledAt),
    status,
    ensembleSignal: Number(ensembleSignal) / 1e18,
    realizedPnlBps: Number(realizedPnlBps),
    submissionsCount: Number(submissionsCount),
  };
  return { round, isLoading };
}

/** Total reputation score per agent (tier-weighted). Reads ReasoningRepToken. */
export function useAgentReputations(ownerAddress: `0x${string}` | undefined) {
  const enabled = isDeployed(repTokenAddress) && !!ownerAddress;
  const { data, isLoading } = useReadContract({
    address: isDeployed(repTokenAddress) ? repTokenAddress : undefined,
    abi: reputationTokenAbi,
    functionName: "totalBalanceOf",
    args: ownerAddress ? [ownerAddress] : undefined,
    query: { enabled, refetchInterval: 30_000 },
  });
  return { totalReputation: data ? Number(data) : undefined, isLoading };
}

/** Total reasoning hashes committed on-chain — a "proof of work done" counter. */
export function useCommitsCount() {
  const { data, isLoading } = useReadContract({
    address: isDeployed(REASONING_HASH_ANCHOR_MAINNET) ? REASONING_HASH_ANCHOR_MAINNET : undefined,
    abi: reasoningAnchorAbi,
    functionName: "commitsCount",
    query: { enabled: isDeployed(REASONING_HASH_ANCHOR_MAINNET), refetchInterval: 15_000 },
  });
  return { commitsCount: data ? Number(data) : undefined, isLoading };
}

export interface OnChainCommit {
  agentId: number;
  decisionIndex: number;
  reasoningHash: `0x${string}`;
  timestamp: number;
}

/** Latest on-chain reasoning commits, newest first — a REAL live feed for the
 * Reasoning Stream. Commits from future live rounds appear here automatically. */
export function useOnChainCommits(max = 12) {
  const { commitsCount } = useCommitsCount();
  const total = commitsCount ?? 0;
  const ids = Array.from({ length: Math.min(max, total) }, (_, i) => total - 1 - i).filter((i) => i >= 0);

  const { data, isLoading } = useReadContracts({
    contracts: ids.map((i) => ({
      address: isDeployed(REASONING_HASH_ANCHOR_MAINNET) ? REASONING_HASH_ANCHOR_MAINNET : undefined,
      abi: reasoningAnchorAbi,
      functionName: "commits" as const,
      args: [BigInt(i)],
    })),
    query: { enabled: isDeployed(REASONING_HASH_ANCHOR_MAINNET) && ids.length > 0, refetchInterval: 15_000 },
  });

  type CommitTuple = readonly [bigint, bigint, `0x${string}`, bigint, `0x${string}`];
  const commits: OnChainCommit[] = (data ?? [])
    .map((r) => r.result as CommitTuple | undefined)
    .filter((x): x is CommitTuple => !!x)
    .map(([agentId, decisionIndex, reasoningHash, timestamp]) => ({
      agentId: Number(agentId),
      decisionIndex: Number(decisionIndex),
      reasoningHash,
      timestamp: Number(timestamp),
    }));
  return { commits, isLoading };
}

/** Batch-read the latest N rounds for the leaderboard / activity feed. */
export function useRecentRounds(count: number) {
  const { roundsCount } = useRoundsCount();
  const total = roundsCount ?? 0;
  const ids = Array.from({ length: Math.min(count, total) }, (_, i) => total - 1 - i).filter((i) => i >= 0);

  const { data, isLoading } = useReadContracts({
    contracts: ids.map((id) => ({
      address: isDeployed(ROUND_STATE_MAINNET) ? ROUND_STATE_MAINNET : undefined,
      abi: roundStateAbi,
      functionName: "getRound",
      args: [BigInt(id)],
    })),
    query: { enabled: isDeployed(ROUND_STATE_MAINNET) && ids.length > 0, refetchInterval: 20_000 },
  });

  const rounds = (data ?? [])
    .map((r, idx) => {
      if (r.status !== "success" || !r.result) return null;
      const [marketId, opener, openedAt, settledAt, status, ensembleSignal, realizedPnlBps, submissionsCount] =
        r.result as readonly [`0x${string}`, `0x${string}`, bigint, bigint, number, bigint, bigint, bigint];
      return {
        roundId: ids[idx],
        marketId,
        opener,
        openedAt: Number(openedAt),
        settledAt: Number(settledAt),
        status,
        ensembleSignal: Number(ensembleSignal) / 1e18,
        realizedPnlBps: Number(realizedPnlBps),
        submissionsCount: Number(submissionsCount),
      };
    })
    .filter((x): x is NonNullable<typeof x> => x !== null);

  return { rounds, isLoading };
}

/** Whether the contracts are deployed yet (drives demo-fixture fallback in UI). */
export function useIsLive() {
  return {
    isLive: isDeployed(ROUND_STATE_MAINNET),
    agentIds: AGENT_IDS as Record<AgentKey, number>,
  };
}
