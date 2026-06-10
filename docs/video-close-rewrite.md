# Video close rewrite

**Change:** insert beat 9.5 + rewrite beat 10

## Beat 9.5

And none of this is a mockup. Five purpose-built contracts are live on Mantle Sepolia: the anchor, the registry, the round-state, a non-transferable reputation token, and the human arena. The same reasoning hash, computed in TypeScript, in Python, and on-chain in Solidity, comes out byte-identical, proven by a live call to the deployed contract, not just asserted in a test.

## Beat 10

Under the hood, a risk engine, built and tested: a five percent size cap, a twenty percent drawdown halt, a Devil's-Advocate veto, designed to grade each agent by its realized results. Open-source, with a publish-ready SDK. Glass-Box Alpha. The AI that shows its work, and lets you check it.

---

**Rationale:**

Three honesty buckets kept strictly separate per the ledger. (1) LIVE on Sepolia (beat 9.5, verb "live/deployed"): the five contracts named individually, plus the TS==Python==Solidity keccak parity "proven by a live call to the deployed contract" — this is the headline depth-flex (verify() recompute, not a test assertion). Said "Mantle Sepolia," never "Mantle"/"mainnet." Did NOT name the 109 tests in 9.5 to keep it to one breath (~14-15s); the test count is strong but the parity claim is the stronger live truth, so I let it carry. (2) BUILT+TESTED, not deployed (beat 10, verb "built and tested"): the risk engine with its exact caps (5% size, 20% drawdown halt, Devil's-Advocate veto). It rides on "built and tested," never on "deployed" — kept off the same clause as the five live contracts. (3) DESIGNED (beat 10, verb "designed to"): the reputation grading flow is phrased "designed to grade each agent by its realized results" — the token is live, but the PnL->reputation grading is design, so the design-verb attaches to the function, not the token.

Inherited violations from the old beat 10 all removed: dropped "verified on Mantle" (source-verification is TO-CONFIRM/banned to assert; the cryptographic "verify" sense already lives in beats 5-8 and isn't reasserted on the contracts); changed "installable SDK" -> "publish-ready SDK" (npm returns 404, artifact is in-repo only); every chain reference is "Mantle Sepolia."

Banned phrasings avoided: no "beats the market"/"beats a plain mean"/"alpha" (I left the Fold/backtest out of the close entirely — the ledger calls it supplementary, not the headline, and it only buys cadence risk); no four-agent anchor or >2 commits implied (9.5 never counts commits or agents); no NFTs minted / ERC-8004 ids bound; no mainnet; no "settled on-chain round" (the simulated arena was already disclaimed in beat 9). MerchantMoe adapter omitted for length — risk engine alone carries the "built and tested" bucket.

Cadence: matches Alex's contrastive, em-dash, second-person close — kept the existing signoff tagline "shows its work, and lets you check it" verbatim. Each beat lands ~14-15s spoken, consistent with the denser beats already in the trailer (beats 3 and 6). "Open-source" retained from the original (repo property, not a ledger claim, but task didn't flag it and it's true). Verify wording lives in /media/phantomcore/AI_DRIVE/hackathons/mantle/glass-box-tools/voiced-trailer-clone.mjs beats array (current beat 10 at L46-48); inserting 9.5 before it and rewriting 10 means re-rendering beat WAVs (voice_kit/gen_beats.py) and renumbering, since beat audio is indexed by array position.
