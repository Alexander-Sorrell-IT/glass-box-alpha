// ERC-8004 registries on Mantle Mainnet (chain 5000) — canonical addresses.
export const ERC8004_IDENTITY = "0x8004A169FB4a3325136EB29fA0ceB6D2e539a432" as const;
export const ERC8004_REPUTATION = "0x8004BAa17C55a88189AE136b182e5fdA19dE9b63" as const;

// Glass-Box contracts — LIVE on Mantle Sepolia (chain 5003), deployed 2026-05-30.
// (Names kept as *_MAINNET for the import surface; values are the Sepolia deployment.)
export const REASONING_HASH_ANCHOR_MAINNET = "0xB0319b2e88d95B2d7Ce706feC7E2799d9b93353d" as `0x${string}` | "";
export const GLASSBOX_REGISTRY_MAINNET = "0x52237944151D385222316f446b7a08Cde44b6797" as `0x${string}` | "";
export const ROUND_STATE_MAINNET = "0xe016C12d1D42cc2E4ECaaCE2B0fd5058cC984Ea5" as `0x${string}` | "";
export const SOVEREIGN_REASONING_COIN_MAINNET = "0x72eA3147F126c9F1C797D1E56D8cF65cFA3d69F9" as `0x${string}` | "";
export const HUMAN_ARENA_MAINNET = "0x51eaD31AdA817281bD853a8ab9a011b1BFcAdf99" as `0x${string}` | "";

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
