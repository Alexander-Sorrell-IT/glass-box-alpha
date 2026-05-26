# Glass-Box Alpha Frontend

Next.js 14 (App Router) · RainbowKit + wagmi · Tailwind · Mantle Mainnet + Sepolia.

## Quickstart
```bash
pnpm install            # or npm install
cp ../.env.example .env.local
# Fill in NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID at minimum
pnpm dev                # http://localhost:3000
```

## Layout
```
app/
  layout.tsx       # RainbowKit + wagmi + react-query providers
  page.tsx         # Hero: 4 agent cards + Fold ensemble + leaderboard + reasoning stream
  globals.css     # Tailwind + theme tokens
  providers.tsx   # Client-side providers
components/
  AgentCard.tsx        # Per-agent signal + confidence + reasoning preview
  ReasoningStream.tsx  # Live reasoning chain (animated)
  Leaderboard.tsx      # AI vs Human PnL ranking
lib/
  wagmi.ts        # Mantle chain config
  contracts.ts    # Contract addresses + agent metadata
```

## Deploy
Vercel one-click — set `NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID` env var.

## TODO (post-Day 11)
- Wire `Leaderboard` to actual ERC-8004 Reputation Registry reads (wagmi `useReadContract`)
- Wire `ReasoningStream` to live backend SSE / WebSocket
- Add settlement modal showing on-chain tx + Mantlescan link
- OG image card route for share moments
