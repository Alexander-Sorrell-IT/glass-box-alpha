# Mantle Contract Addresses

## ERC-8004 Registries (canonical, deployed by erc-8004 team via CREATE2)

### Mantle Mainnet (chain ID 5000)
| Registry | Address | Source |
|---|---|---|
| Identity Registry | `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432` | [erc-8004/erc-8004-contracts](https://github.com/erc-8004/erc-8004-contracts) |
| Reputation Registry | `0x8004BAa17C55a88189AE136b182e5fdA19dE9b63` | [erc-8004/erc-8004-contracts](https://github.com/erc-8004/erc-8004-contracts) |
| Validation Registry | **NOT DEPLOYED** — spec still under TEE-community revision per repo README | — |

### Mantle Sepolia Testnet (chain ID 5003)
| Registry | Address |
|---|---|
| Identity Registry | `0x8004A818BFB912233c491871b3d84c89A494BD9e` |
| Reputation Registry | `0x8004B663056A597Dffe9eCcC1965A193B7388713` |
| Validation Registry | not deployed |

Vanity prefix `0x8004…` comes from CREATE2 mining — same prefix across chains.

## Our project contracts (to be deployed)

| Contract | Purpose | Status |
|---|---|---|
| `RoundState.sol` | Per-round state (question, agents, settlements) | Day 7 |
| `ReasoningHashAnchor.sol` | Commits agent reasoning chain hash on-chain (Verity primitive) | Day 7 |
| `AgentExecutor.sol` | Routes ensemble decision to Mantle DEX swap/LP | Day 8-9 |
| `BroadcastSchema.sol` (kit) | Standard interface other teams implement to appear on broadcast leaderboard | Day 15 |

Agent Identity NFTs (4 mints on mainnet, Day 2):
- [ ] Chronos — Token #__
- [ ] Devil's Advocate — Token #__
- [ ] Web — Token #__
- [ ] Mood — Token #__

## Mantle infrastructure references
- Mainnet RPC: `https://rpc.mantle.xyz`
- Sepolia RPC: `https://rpc.sepolia.mantle.xyz`
- Mainnet explorer: `https://mantlescan.xyz`
- Sepolia explorer: `https://sepolia.mantlescan.xyz`
- DevHub: `https://devhub.mantle.xyz`

## Mantle DEXes for agent execution
- Merchant Moe (V3 concentrated): `https://merchantmoe.com/`
- Agni Finance: `https://agni.finance/`
- Fluxion: `https://fluxion.fi/`
- Swapsicle (perps): `https://swapsicle.io/`
- Demex (spot + perps): `https://demex.nitron.network/`

## Sponsor APIs
- Nansen: `https://docs.nansen.ai/api/smart-money` — pay-per-call (~$0.01 basic, $0.05 advanced)
- Elfa AI: `https://www.elfa.ai/api` — 1K free calls/mo, premium tier ~$100/mo
- Surf AI / Orbit AI: TBD (CONTEST.md mentions but APIs are less documented)

## Fallback for Validation Registry
Since Validation Registry isn't deployed canonically yet, we will either:
1. Deploy our own copy of `ValidationRegistryUpgradeable.sol` from the erc-8004 repo to Mantle Sepolia and document it as "project-local instance pending canonical deployment", OR
2. Stub the validation interface so we can swap in the canonical address when it ships post-hackathon

Default plan: stub, no self-deploy (avoids confusion about "official" addresses).
