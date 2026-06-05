// ERC-8004 agent-identity shapes + canonical registry addresses on Mantle.
// The hackathon requires every participating agent to hold an ERC-8004 identity NFT;
// bind your agent's token id to its reasoning commits so reputation accrues to the
// identity. (This module ships the addresses and types; reputation writes settle
// against the Reputation Registry once your scoring rule is live.)
import { type Address } from "viem";

/** Canonical ERC-8004 registries (CREATE2-mined `0x8004…` vanity prefix). */
export const ERC8004_REGISTRIES = {
  mantle: {
    identity: "0x8004A169FB4a3325136EB29fA0ceB6D2e539a432" as Address,
    reputation: "0x8004BAa17C55a88189AE136b182e5fdA19dE9b63" as Address,
  },
  mantleSepolia: {
    identity: "0x8004A818BFB912233c491871b3d84c89A494BD9e" as Address,
    reputation: "0x8004B663056A597Dffe9eCcC1965A193B7388713" as Address,
  },
} as const;

/** A participating agent's on-chain identity. `tokenId` is its ERC-8004 NFT id —
 *  the same number you pass as `agentId` when committing reasoning receipts. */
export interface AgentIdentity {
  tokenId: number;
  name: string;
  /** A short, stable description of the agent's reasoning frame. */
  frame: string;
  /** Optional owner/operator address of record. */
  operator?: Address;
}
