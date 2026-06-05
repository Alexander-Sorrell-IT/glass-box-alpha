// glassbox-agent-kit — ship a verifiable, transparent AI agent on Mantle.
//
// The reasoning-receipt primitive (canonicalReceipt / receiptHash), a transparent
// agent base class (GlassBoxAgent) + the Fold ensemble, on-chain commit/verify
// helpers for the ReasoningHashAnchor contract, and ERC-8004 identity shapes.
export {
  type ReasoningChain,
  type ReasoningStep,
  canonicalReceipt,
  receiptHash,
  hashCanonical,
} from "./receipt.js";

export {
  type DecisionKind,
  type Decision,
  type RawReasoning,
  type ReasoningResult,
  GlassBoxAgent,
  foldEnsemble,
} from "./agent.js";

export {
  REASONING_HASH_ANCHOR_SEPOLIA,
  reasoningHashAnchorAbi,
  commitReasoning,
  verifyReasoning,
} from "./anchor.js";

export { ERC8004_REGISTRIES, type AgentIdentity } from "./erc8004.js";

export { mantle, mantleSepolia } from "./chains.js";
