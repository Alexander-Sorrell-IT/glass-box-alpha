// ERC-8004 registries on Mantle Mainnet (chain 5000) — canonical addresses.
export const ERC8004_IDENTITY = "0x8004A169FB4a3325136EB29fA0ceB6D2e539a432" as const;
export const ERC8004_REPUTATION = "0x8004BAa17C55a88189AE136b182e5fdA19dE9b63" as const;

// Glass-Box contracts — filled after Day 7 (Sepolia deploy) / Day 14 (Mainnet deploy).
export const REASONING_HASH_ANCHOR_MAINNET = "" as `0x${string}` | "";
export const GLASSBOX_REGISTRY_MAINNET = "" as `0x${string}` | "";
export const ROUND_STATE_MAINNET = "" as `0x${string}` | "";
export const SOVEREIGN_REASONING_COIN_MAINNET = "" as `0x${string}` | "";
export const HUMAN_ARENA_MAINNET = "" as `0x${string}` | "";

// Agent ERC-8004 token IDs — set after Day 4 mints on mainnet.
export const AGENT_IDS = {
  chronos: 0,
  devils_advocate: 0,
  web: 0,
  mood: 0,
} as const;

export const AGENT_META = {
  chronos: {
    name: "Chronos",
    role: "Timeline / historical analog mining",
    frame: "Expansion — possibility trees through historical time",
    color: "text-agent-chronos",
  },
  devils_advocate: {
    name: "Devil's Advocate",
    role: "Contradiction / risk frame",
    frame: "Collapse — counter-hypothesis on peer assumptions",
    color: "text-agent-devilsAdvocate",
  },
  web: {
    name: "Web",
    role: "Cross-asset correlation",
    frame: "Collapse — linked-variable compression",
    color: "text-agent-web",
  },
  mood: {
    name: "Mood",
    role: "Sentiment orthogonal to price",
    frame: "Collapse — orthogonal-dimension signal",
    color: "text-agent-mood",
  },
} as const;

export type AgentKey = keyof typeof AGENT_META;
