import { ImageResponse } from "next/og";

export const runtime = "edge";

// Share-card generator for round results.
// Usage: /api/og?market=mETH/USDC&signal=0.41&confidence=66&pnl=2.3&round=17
//   &chronos=0.62&da=-0.15&web=0.48&mood=0.38
// Produces a 1200×630 card auto-posted to @GlassBoxAlpha when a round settles.

const COLORS = {
  bg: "#0a0a0f",
  panel: "#13131a",
  border: "#26262f",
  accent: "#7c5cff",
  bull: "#3eea8c",
  bear: "#ff5c7c",
  neutral: "#8a8a99",
  text: "#e5e5ea",
};

function fmtSignal(v: number): string {
  return v >= 0 ? `+${v.toFixed(2)}` : v.toFixed(2);
}

function signalColor(v: number): string {
  return v > 0.05 ? COLORS.bull : v < -0.05 ? COLORS.bear : COLORS.neutral;
}

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const market = searchParams.get("market") ?? "mETH/USDC";
  const signal = parseFloat(searchParams.get("signal") ?? "0");
  const confidence = parseFloat(searchParams.get("confidence") ?? "0");
  const pnl = searchParams.get("pnl") ? parseFloat(searchParams.get("pnl")!) : null;
  const round = searchParams.get("round") ?? "—";

  // Optional human-vs-agent result overlay (the "AI vs Human" share card).
  const humanScore = searchParams.get("human");
  const agentScore = searchParams.get("agent");
  const vsName = searchParams.get("vs") ?? "the AI";
  const beat = searchParams.get("beat") === "1";
  const hasMatchup = humanScore !== null && agentScore !== null;
  const fmtB = (v: string) => (parseFloat(v) >= 0 ? `+${v}` : v);

  const agents = [
    { name: "Chronos", value: parseFloat(searchParams.get("chronos") ?? "0"), color: "#5dade2" },
    { name: "Devil's Advocate", value: parseFloat(searchParams.get("da") ?? "0"), color: "#ff8c5a" },
    { name: "Web", value: parseFloat(searchParams.get("web") ?? "0"), color: "#a78bfa" },
    { name: "Mood", value: parseFloat(searchParams.get("mood") ?? "0"), color: "#ffd966" },
  ];

  return new ImageResponse(
    (
      <div
        style={{
          width: "1200px",
          height: "630px",
          display: "flex",
          flexDirection: "column",
          backgroundColor: COLORS.bg,
          padding: "56px",
          fontFamily: "monospace",
        }}
      >
        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ display: "flex", flexDirection: "column" }}>
            <span style={{ fontSize: 44, fontWeight: 700, color: COLORS.text }}>Glass-Box Alpha</span>
            <span style={{ fontSize: 24, color: COLORS.neutral, marginTop: 6 }}>
              Round #{round} · {market} · AI reasoning attested on Mantle
            </span>
          </div>
          <div
            style={{
              display: "flex",
              padding: "10px 20px",
              backgroundColor: COLORS.accent,
              borderRadius: 12,
              fontSize: 24,
              color: "white",
              fontWeight: 600,
            }}
          >
            Mantle Turing Test
          </div>
        </div>

        {/* Human-vs-agent matchup banner (only on share cards) */}
        {hasMatchup && (
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginTop: 40,
              backgroundColor: COLORS.panel,
              border: `2px solid ${beat ? COLORS.bull : COLORS.bear}`,
              borderRadius: 20,
              padding: "28px 40px",
            }}
          >
            <div style={{ display: "flex", flexDirection: "column" }}>
              <span style={{ fontSize: 26, color: COLORS.neutral, letterSpacing: 2 }}>YOU</span>
              <span style={{ fontSize: 64, color: beat ? COLORS.bull : COLORS.text, fontWeight: 700 }}>
                {fmtB(humanScore!)} bps
              </span>
            </div>
            <span style={{ fontSize: 40, color: beat ? COLORS.bull : COLORS.bear, fontWeight: 700 }}>
              {beat ? `BEAT ${vsName.toUpperCase()}` : `${vsName.toUpperCase()} WON`}
            </span>
            <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end" }}>
              <span style={{ fontSize: 26, color: COLORS.neutral, letterSpacing: 2 }}>{vsName.toUpperCase()}</span>
              <span style={{ fontSize: 64, color: COLORS.text, fontWeight: 700 }}>
                {fmtB(agentScore!)} bps
              </span>
            </div>
          </div>
        )}

        {/* Agent signals row */}
        <div style={{ display: "flex", gap: 20, marginTop: hasMatchup ? 28 : 56 }}>
          {agents.map((a) => (
            <div
              key={a.name}
              style={{
                display: "flex",
                flexDirection: "column",
                flex: 1,
                backgroundColor: COLORS.panel,
                border: `1px solid ${COLORS.border}`,
                borderRadius: 16,
                padding: "24px",
              }}
            >
              <span style={{ fontSize: 22, color: a.color, fontWeight: 600 }}>{a.name}</span>
              <span style={{ fontSize: 52, color: signalColor(a.value), marginTop: 8 }}>
                {fmtSignal(a.value)}
              </span>
            </div>
          ))}
        </div>

        {/* Fold ensemble result */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginTop: 48,
            backgroundColor: COLORS.panel,
            border: `2px solid ${COLORS.accent}`,
            borderRadius: 20,
            padding: "32px 40px",
          }}
        >
          <div style={{ display: "flex", flexDirection: "column" }}>
            <span style={{ fontSize: 26, color: COLORS.neutral, letterSpacing: 2 }}>FOLD ENSEMBLE</span>
            <span style={{ fontSize: 80, color: signalColor(signal), fontWeight: 700, marginTop: 4 }}>
              {fmtSignal(signal)}
            </span>
          </div>
          <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end" }}>
            <span style={{ fontSize: 26, color: COLORS.neutral }}>confidence {confidence.toFixed(0)}%</span>
            {pnl !== null && (
              <span
                style={{
                  fontSize: 44,
                  color: pnl >= 0 ? COLORS.bull : COLORS.bear,
                  fontWeight: 700,
                  marginTop: 8,
                }}
              >
                PnL {pnl >= 0 ? "+" : ""}{pnl.toFixed(2)}%
              </span>
            )}
          </div>
        </div>

        {/* Footer */}
        <div style={{ display: "flex", marginTop: "auto", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ fontSize: 22, color: COLORS.accent }}>
            recompute the hash yourself →
          </span>
          <span style={{ fontSize: 22, color: COLORS.neutral }}>@GlassBoxAlpha</span>
        </div>
      </div>
    ),
    { width: 1200, height: 630 },
  );
}
