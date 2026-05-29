// Minimal ABIs for the read paths the frontend needs. Full ABIs live in
// contracts/out/ after `forge build`; these are hand-trimmed to the views +
// events the UI reads, to keep the bundle small.

export const roundStateAbi = [
  {
    type: "function",
    name: "roundsCount",
    stateMutability: "view",
    inputs: [],
    outputs: [{ type: "uint256" }],
  },
  {
    type: "function",
    name: "getRound",
    stateMutability: "view",
    inputs: [{ name: "roundId", type: "uint256" }],
    outputs: [
      { name: "marketId", type: "bytes32" },
      { name: "opener", type: "address" },
      { name: "openedAt", type: "uint256" },
      { name: "settledAt", type: "uint256" },
      { name: "status", type: "uint8" },
      { name: "ensembleSignal", type: "int256" },
      { name: "realizedPnlBps", type: "int256" },
      { name: "submissionsCount", type: "uint256" },
    ],
  },
  {
    type: "function",
    name: "getSubmission",
    stateMutability: "view",
    inputs: [
      { name: "roundId", type: "uint256" },
      { name: "index", type: "uint256" },
    ],
    outputs: [
      {
        type: "tuple",
        components: [
          { name: "agentId", type: "uint256" },
          { name: "kind", type: "uint8" },
          { name: "directionalSignal", type: "int256" },
          { name: "sizeBps", type: "uint256" },
          { name: "reasoningHash", type: "bytes32" },
          { name: "submittedAt", type: "uint256" },
        ],
      },
    ],
  },
] as const;

export const humanArenaAbi = [
  {
    type: "function",
    name: "submitCall",
    stateMutability: "nonpayable",
    inputs: [
      { name: "roundId", type: "uint256" },
      { name: "direction", type: "int8" },
      { name: "convictionBps", type: "uint16" },
      { name: "reasoningHash", type: "bytes32" },
    ],
    outputs: [],
  },
  {
    type: "function",
    name: "beatAgent",
    stateMutability: "view",
    inputs: [
      { name: "roundId", type: "uint256" },
      { name: "player", type: "address" },
      { name: "submissionIndex", type: "uint256" },
    ],
    outputs: [
      { name: "beat", type: "bool" },
      { name: "human", type: "int256" },
      { name: "agent", type: "int256" },
      { name: "agentId", type: "uint256" },
    ],
  },
  {
    type: "function",
    name: "humanScore",
    stateMutability: "view",
    inputs: [
      { name: "roundId", type: "uint256" },
      { name: "player", type: "address" },
    ],
    outputs: [{ type: "int256" }],
  },
  {
    type: "event",
    name: "CallSubmitted",
    inputs: [
      { name: "roundId", type: "uint256", indexed: true },
      { name: "player", type: "address", indexed: true },
      { name: "direction", type: "int8", indexed: false },
      { name: "convictionBps", type: "uint16", indexed: false },
      { name: "reasoningHash", type: "bytes32", indexed: false },
    ],
  },
] as const;

export const reputationTokenAbi = [
  {
    type: "function",
    name: "totalBalanceOf",
    stateMutability: "view",
    inputs: [{ name: "holder", type: "address" }],
    outputs: [{ type: "uint256" }],
  },
  {
    type: "function",
    name: "balanceOf",
    stateMutability: "view",
    inputs: [
      { name: "holder", type: "address" },
      { name: "tier", type: "uint8" },
    ],
    outputs: [{ type: "uint256" }],
  },
] as const;

export const reasoningAnchorAbi = [
  {
    type: "function",
    name: "commitsCount",
    stateMutability: "view",
    inputs: [],
    outputs: [{ type: "uint256" }],
  },
  {
    type: "function",
    name: "getCommit",
    stateMutability: "view",
    inputs: [
      { name: "agentId", type: "uint256" },
      { name: "decisionIndex", type: "uint256" },
    ],
    outputs: [
      {
        type: "tuple",
        components: [
          { name: "agentId", type: "uint256" },
          { name: "decisionIndex", type: "uint256" },
          { name: "reasoningHash", type: "bytes32" },
          { name: "timestamp", type: "uint256" },
          { name: "committer", type: "address" },
        ],
      },
    ],
  },
] as const;
