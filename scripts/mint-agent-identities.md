# Day 2 — Mint 4 Agent Identity NFTs on Mantle Mainnet

Run on Day 2 once `DEPLOYER_PRIVATE_KEY` is funded with ~0.05 MNT on Mantle Mainnet (covers all 4 mints + initial contract deploys).

## ERC-8004 Identity Registry on Mantle Mainnet
- Address: `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432`
- Spec: each registration returns an `agentId` (uint256, monotonically increasing) and mints an ERC-721 token representing the agent's identity.

## Mint each agent

The Identity Registry's `register(string memory agentURI)` function mints an NFT and returns `agentId`. The `agentURI` should be an `https://` or `ipfs://` link to a JSON file describing the agent.

For each of our 4 agents, prepare a small JSON file (hosted on IPFS via web3.storage or pinned to GitHub Pages from this repo) with:

```json
{
  "name": "Chronos",
  "description": "Glass-Box Alpha agent — timeline / cyclical pattern analysis. Reads Nansen historical wallet flows + on-chain TVL/price history.",
  "image": "https://raw.githubusercontent.com/Alexander-Sorrell-IT/glass-box-alpha/main/assets/agents/chronos.png",
  "operator": "Glass-Box Alpha (Mantle Turing Test 2026)",
  "model": "deepseek-reasoner",
  "endpoint": "https://glass-box-alpha.vercel.app/api/agents/chronos"
}
```

(One JSON per agent: Chronos, Devil's Advocate, Web, Mood)

## Mint command (using cast)

```bash
source ../.env

# Repeat for each agent. Capture the agentId from the tx receipt.
cast send \
  --rpc-url $MANTLE_MAINNET_RPC \
  --private-key $DEPLOYER_PRIVATE_KEY \
  $ERC8004_IDENTITY \
  "register(string)(uint256)" \
  "https://raw.githubusercontent.com/Alexander-Sorrell-IT/glass-box-alpha/main/agents/chronos/identity.json"
```

Then decode the returned `agentId` from the tx logs (the Identity Registry emits a `Registered(uint256 agentId, address owner, string agentURI)` event).

## Record results

Update `CONTRACTS.md` with the 4 token IDs:
- Chronos — Token #__
- Devil's Advocate — Token #__
- Web — Token #__
- Mood — Token #__

And use those `agentId` values in `agents/*/agent.py` when instantiating each agent class.

## Cost estimate
~0.01 MNT per registration × 4 = 0.04 MNT. Add 0.02 MNT for contract deploys later in week. Total Day 2 budget: ~0.06 MNT (~$0.05 at current prices, basically free).

## Faucet (if you need Sepolia first)
Mantle Sepolia faucet: https://faucet.testnet.mantle.xyz (get test MNT here for testnet trial run before mainnet)
