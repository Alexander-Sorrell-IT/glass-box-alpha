#!/usr/bin/env python3
"""Blinded historical backtest of the 4 reasoning frames on REAL price data.

The point: test whether the AGENTS' REASONING predicts forward direction —
while CONTROLLING for LLM training-hindsight. We strip every identifier the model
could recognize (asset name, dates, absolute price) and feed only the normalized
recent pattern. A tripwire flags any answer that names a real asset (= possible
hindsight leak). Walk-forward / out-of-sample only; realistic round-trip costs.

Usage:
  python3 scripts/blinded_backtest.py --asset BTC --points 3      # smoke (~12 calls)
  python3 scripts/blinded_backtest.py --asset all --points 50     # full run
"""
from __future__ import annotations
import os, re, csv, json, time, random, argparse, statistics
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "runs" / "edge-data"
MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro")
client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"],
                base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))

LOOKBACK = 30          # bars of context shown to the agent
HORIZON = 5            # forward bars we score the call against
COST = 0.012           # 1.2% round-trip (fee+slippage+MEV haircut)
IS_FRAC = 0.55         # first 55% is "seen" history; decisions only on the OOS tail

# Reasoning frames — derived from the 4 agent system prompts, with asset/source
# identifiers REMOVED so the model must reason from numbers, not recall the period.
FRAMES = {
 "chronos": "You analyze a single anonymized asset's recent normalized price path for timeline / cyclical analog patterns, then project the NEXT move.",
 "web": "You analyze cross-series linkage between an anonymized asset and a correlated 'market' series; judge whether the linkage implies the next move.",
 "mood": "You judge momentum vs exhaustion: is the recent move likely to continue or revert?",
 "devils_advocate": "You are the Devil's Advocate — argue the COUNTER case to the obvious read, and decide whether the contrarian view should win.",
}
INSTR = ("Reason briefly from the numbers ONLY (no asset names or dates are given — there are none to know). "
         "End with EXACTLY one line:\nDECISION: <LONG|SHORT|FLAT> signal=<-1..1> confidence=<0..1>\n"
         "signal>0 means you expect the price to RISE next, <0 means FALL.")
LEAK_RE = re.compile(r"bitcoin|btc|ethereum|\beth\b|mantle|\bmnt\b|\bmeth\b|solana|\bsol\b|usdc|defi|crypto", re.I)


def load_series(asset: str):
    rows = list(csv.DictReader(open(DATA / f"{asset}.csv")))
    return [float(r["close"]) for r in rows]


def blinded_ctx(closes, t, market=None):
    win = closes[t - LOOKBACK:t]; b = win[0]
    ctx = {"normalized_recent_closes": [round(c / b, 4) for c in win]}
    if market is not None:
        mw = market[t - LOOKBACK:t]; mb = mw[0]
        ctx["correlated_market_normalized"] = [round(c / mb, 4) for c in mw]
    return ctx


def call_frame(frame_key, ctx):
    prompt = f"{FRAMES[frame_key]}\n\nData (normalized to 1.0 at the window start):\n{json.dumps(ctx)}\n\n{INSTR}"
    # v4-pro burns thousands of tokens on reasoning_content before the final answer —
    # give it room, and parse the DECISION from EITHER channel (content or reasoning).
    r = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}],
                                       max_tokens=6000, temperature=0.3)
    msg = r.choices[0].message
    txt = ((msg.content or "") + "\n" + (getattr(msg, "reasoning_content", "") or "")).strip()
    sm = re.findall(r"signal\s*=\s*(-?\d+(?:\.\d+)?)", txt)
    cm = re.findall(r"confidence\s*=\s*(\d+(?:\.\d+)?)", txt)
    sig = max(-1.0, min(1.0, float(sm[-1]))) if sm else 0.0   # last mention = the final call
    conf = max(0.0, min(1.0, float(cm[-1]))) if cm else 0.0
    return sig, conf, bool(LEAK_RE.search(txt))


def fold(sigs, confs):
    w = sum(confs)
    return (sum(s * c for s, c in zip(sigs, confs)) / w) if w else 0.0


from concurrent.futures import ThreadPoolExecutor, as_completed


def decision_indices(asset, n_points, seed=7):
    n = len(load_series(asset))
    start = max(LOOKBACK, int(n * IS_FRAC)); end = n - HORIZON
    idxs = list(range(start, end)); random.Random(seed).shuffle(idxs)
    return sorted(idxs[:n_points])


def summarize(asset, recs, leaks):
    traded = [r for r in recs if r["pos"] != 0]
    wins = [r for r in traded if r["pos"] * r["fwd_ret"] > 0]
    pnls = [r["pnl"] for r in traded]
    mean = statistics.mean(pnls) if pnls else 0.0
    sd = statistics.pstdev(pnls) if len(pnls) > 1 else 0.0
    sharpe = (mean / sd * (252 / HORIZON) ** 0.5) if sd else 0.0
    return {"asset": asset, "n_decisions": len(recs), "n_traded": len(traded),
            "hit_rate_pct": round(len(wins) / len(traded) * 100, 1) if traded else 0.0,
            "mean_pnl_per_trade_pct": round(mean * 100, 3), "after_cost_sharpe": round(sharpe, 2),
            "hindsight_leak_calls": leaks, "records": recs}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--asset", default="BTC")
    ap.add_argument("--points", type=int, default=3)
    ap.add_argument("--workers", type=int, default=10)
    a = ap.parse_args()
    pairs = {"BTC": "ETH", "ETH": "BTC", "mETH": "ETH", "MNT": "BTC"}
    assets = ["BTC", "ETH", "mETH", "MNT"] if a.asset == "all" else [a.asset]
    series = {x: load_series(x) for x in set(assets) | {pairs[x] for x in assets}}
    pts = {x: decision_indices(x, a.points) for x in assets}
    tasks = [(x, t, fk) for x in assets for t in pts[x] for fk in FRAMES]
    print(f"Blinded backtest · model={MODEL} · {a.points} pts/asset · {len(tasks)} agent calls · {a.workers} parallel")

    def work(task):
        x, t, fk = task
        return task, call_frame(fk, blinded_ctx(series[x], t, series[pairs[x]]))

    results, done = {}, 0
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        for fut in as_completed([ex.submit(work, t) for t in tasks]):
            task, res = fut.result(); results[task] = res; done += 1
            if done % 20 == 0:
                print(f"  ... {done}/{len(tasks)} calls done")

    out = []
    for x in assets:
        recs, leaks = [], 0
        for t in pts[x]:
            sigs, confs = [], []
            for fk in FRAMES:
                s, c, lk = results[(x, t, fk)]; sigs.append(s); confs.append(c); leaks += int(lk)
            ens = fold(sigs, confs)
            fwd = series[x][t + HORIZON] / series[x][t] - 1.0
            pos = 1 if ens > 0.05 else (-1 if ens < -0.05 else 0)
            recs.append({"t": t, "ensemble": round(ens, 3), "pos": pos,
                         "fwd_ret": round(fwd, 4), "pnl": round(pos * fwd - (COST if pos else 0.0), 4)})
        out.append(summarize(x, recs, leaks))

    print("\n=== SUMMARY (after-cost, out-of-sample, BLINDED — real agents) ===")
    for r in out:
        print(f"  {r['asset']:5} hit={r['hit_rate_pct']}%  mean/trade={r['mean_pnl_per_trade_pct']}%  "
              f"Sharpe={r['after_cost_sharpe']}  traded={r['n_traded']}/{r['n_decisions']}  leaks={r['hindsight_leak_calls']}")
    rep = DATA / f"blinded-{int(time.time())}.json"
    json.dump(out, open(rep, "w"), indent=2)
    print(f"\nReport: {rep}")
    tl = sum(r["hindsight_leak_calls"] for r in out)
    print(f"⚠ HINDSIGHT TRIPWIRE: {tl} call(s) named a real asset — inspect." if tl
          else "✓ Hindsight tripwire clean: no answer named a real asset.")


if __name__ == "__main__":
    main()
