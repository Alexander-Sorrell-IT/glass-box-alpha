"use client";

import { useEffect, useMemo, useState } from "react";
import { HERO_ROUND, type HeroRound, type HeroAgentKey } from "@/lib/heroRound";
import { AGENT_META } from "@/lib/contracts";

// SignalRibbons — the captured-round hero.
// Three encoding channels, identical color language to AgentCard.tsx:
//   1. vertical position = SIGNAL (bull up / bear down)
//   2. stroke thickness + opacity = CONFIDENCE (with floors so mood never vanishes)
//   3. fill/stroke color = DIRECTION (>0.05 bull / <-0.05 bear / else neutral)
//        -> exactly AgentCard's rule; that coherence is the whole design.
//
// RESOLVED CONFLICT: an earlier brief said "Devil's Advocate is red." That is stale
// from the old DEMO_AGENTS fixture where DA sat at -0.15 (bearish). The real captured
// heroRound flipped DA to +0.2 — a BULLISH dissent. Painting a +0.2 call red would
// (a) contradict the data and (b) camouflage it into the two red bear ribbons,
// destroying the "unmistakable dissent" requirement. So color=direction => DA is GREEN.
// Its dissent reads via POSITION (lone upward bend, colorblind-safe), orange identity
// dot, and an explicit "DISSENT ↑" tag — not via color.

interface RingProps {
  round?: HeroRound;
  onSelectAgent?: (key: HeroAgentKey) => void;
  selectedAgent?: HeroAgentKey | null;
  height?: number;
  animate?: boolean;
  className?: string;
}

const X0 = 80; // ribbon origins (left)
const XM = 760; // merge / fold throat
const XF = 1040; // fold node center (right)
const VBW = 1100; // viewBox width

// Direction → token hex (mirrors tailwind signal.* + AgentCard's >0.05/<-0.05 rule).
const BULL = "#3eea8c";
const BEAR = "#ff5c7c";
const NEUTRAL = "#8a8a99";
function dirColor(s: number): string {
  return s > 0.05 ? BULL : s < -0.05 ? BEAR : NEUTRAL;
}

// Identity colors (label + origin dot) — distinct channel from the direction fill.
const IDENTITY_HEX: Record<HeroAgentKey, string> = {
  chronos: "#5dade2",
  web: "#a78bfa",
  mood: "#ffd966",
  devils_advocate: "#ff8c5a",
};

function actionFromSignal(s: number): string {
  return s < -0.05 ? "PERP_SHORT" : s > 0.05 ? "PERP_LONG" : "HOLD";
}
function fmtSignal(v: number): string {
  return v >= 0 ? `+${v.toFixed(2)}` : v.toFixed(2);
}

export function Ring({
  round = HERO_ROUND,
  onSelectAgent,
  selectedAgent = null,
  height = 420,
  animate = true,
  className = "",
}: RingProps) {
  const H = height;
  const midY = H * 0.5;
  const AMP = H * 0.34;
  const laneY = (s: number) => midY - s * AMP;

  const [hovered, setHovered] = useState<HeroAgentKey | null>(null);
  const [reducedMotion, setReducedMotion] = useState(false);

  // prefers-reduced-motion: client-only; never call matchMedia during render/SSR.
  useEffect(() => {
    if (typeof window === "undefined" || !window.matchMedia) return;
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    const apply = () => setReducedMotion(mq.matches);
    apply();
    mq.addEventListener?.("change", apply);
    return () => mq.removeEventListener?.("change", apply);
  }, []);

  const motion = animate && !reducedMotion;

  // All derivation in a single useMemo over round.agents.
  const ribbons = useMemo(() => {
    const ensembleSig = round.ensemble.signal;
    const foldThroatY = laneY(ensembleSig); // merge lands at the TRUE weighted mean

    const strokeW = (conf: number) => 4 + conf * 30; // mood floor ≈5.5px
    const opacityFor = (conf: number) => 0.32 + conf * 0.68; // mood floor 0.32

    // CHRONOS/WEB OVERLAP FIX: both signal -0.5 → same laneY. Order the two bears by
    // confidence desc; chronos stays the fat anchor at laneY(-0.5), web sits just above.
    const bears = round.agents
      .filter((a) => a.signal < -0.05)
      .sort((a, b) => b.confidence - a.confidence);
    const yNudge: Record<string, number> = {};
    if (bears.length >= 2) {
      const anchor = bears[0];
      for (let i = 1; i < bears.length; i++) {
        const above = bears[i];
        yNudge[above.agentKey] =
          -(strokeW(anchor.confidence) / 2 + strokeW(above.confidence) / 2 + 6) * i;
      }
    }

    // isDissent: sign differs from ensemble (generic — works for future rounds).
    const isDissent = (s: number) =>
      Math.sign(s) !== Math.sign(ensembleSig) && s !== 0;

    // DRAW ORDER (z): fat red bears first (chronos under web), mood, GREEN DA last.
    const order: HeroAgentKey[] = ["chronos", "web", "mood", "devils_advocate"];

    const items = order
      .map((key, drawIdx) => {
        const a = round.agents.find((x) => x.agentKey === key);
        if (!a) return null;
        const s = a.signal;
        const baseY = laneY(s);
        const oy = baseY + (yNudge[a.agentKey] ?? 0); // nudged origin/lane Y
        const targetY = Math.max(
          foldThroatY - 15,
          Math.min(foldThroatY + 15, oy < foldThroatY ? foldThroatY - 5 : foldThroatY + 5),
        );
        // cubic Bézier origin → throat (control points pull toward the fold band)
        const d = `M ${X0},${oy} C ${X0 + 260},${oy} ${XM - 120},${foldThroatY} ${XM},${targetY}`;
        // Labels read LEFT→RIGHT from just right of the origin dot (X0=80 has no left
        // gutter, so anchor=start avoids the off-canvas clip). Lift the name baseline
        // above the ribbon, clearing half the stroke + a margin. Web (the nudged-up
        // bear) drops its label INTO the gap between Mood's ribbon (above) and its own
        // stroke — a smaller lift, so it never overprints Mood's stats line.
        // Web: place name+stats in the ~30px gap between Mood's ribbon (bottom ≈213)
        // and Web's own stroke top (≈246) — name ≈223, stats ≈238. Clears both.
        const sw = strokeW(a.confidence);
        const lift = key === "web" ? sw / 2 + 24 : sw / 2 + 18;
        const labelX = X0 + 14;
        const labelY = oy - lift;
        return {
          key,
          agent: a,
          color: dirColor(s),
          identity: IDENTITY_HEX[key],
          stroke: sw,
          opacity: opacityFor(a.confidence),
          originY: oy,
          targetY,
          d,
          dissent: isDissent(s),
          drawIdx,
          labelX,
          labelY,
        };
      })
      .filter((x): x is NonNullable<typeof x> => x !== null);

    return { items, foldThroatY, ensembleSig };
  }, [round, H]); // eslint-disable-line react-hooks/exhaustive-deps

  const { items, foldThroatY, ensembleSig } = ribbons;
  const ensembleColor = dirColor(ensembleSig);
  const ensembleAction = actionFromSignal(ensembleSig);
  const focusKey = selectedAgent ?? hovered;

  const daItem = items.find((i) => i.key === "devils_advocate");

  // Composition + weighted mean derived from the data (never hardcoded) so the
  // summary and caption can never drift from what the ribbons actually show.
  const bulls = round.agents.filter((a) => a.signal > 0.05).length;
  const bears = round.agents.filter((a) => a.signal < -0.05).length;
  const neutrals = round.agents.length - bulls - bears;
  const dissenters = round.agents
    .filter((a) => a.signal !== 0 && Math.sign(a.signal) !== Math.sign(ensembleSig))
    .map((a) => AGENT_META[a.agentKey].name);
  const compParts = [
    bears ? `${bears} bearish` : "",
    neutrals ? `${neutrals} neutral` : "",
    bulls ? `${bulls} bullish` : "",
  ].filter(Boolean);
  const dissentStr = dissenters.length ? ` Dissent from ${dissenters.join(", ")}.` : "";
  const ariaSummary = `${round.agents.length} AI agents on ${round.marketId}: ${compParts.join(", ")}.${dissentStr} Fold call ${ensembleAction} ${fmtSignal(ensembleSig)}, conviction ${(round.ensemble.confidence * 100).toFixed(0)} percent.`;

  const wSum = round.agents.reduce((acc, a) => acc + a.signal * a.confidence, 0);
  const cSum = round.agents.reduce((acc, a) => acc + a.confidence, 0);
  const arrow = ensembleSig < -0.05 ? "▼" : ensembleSig > 0.05 ? "▲" : "■";

  return (
    <div className={`w-full ${className}`}>
      <style>{`
        @keyframes ribbonDraw { from { stroke-dashoffset: 1; } to { stroke-dashoffset: 0; } }
        .gb-ribbon-draw { stroke-dasharray: 1; stroke-dashoffset: 1; animation: ribbonDraw 1.1s ease-out forwards; }
      `}</style>
      {/* On phones the 1100-wide viewBox scales the in-SVG labels (8–15px) down to
          a few px and they become illegible. Allow horizontal scroll and hold a
          legible minimum width rather than shrinking the type into mush. py-1 keeps
          the 2px focus outline on the top/bottom ribbons from being clipped. */}
      <div className="overflow-x-auto py-1">
      {/* role="group" (not "img"): an "img" role prunes descendants from the a11y tree,
          which would hide the per-agent ribbon buttons from screen readers. */}
      <svg
        role="group"
        aria-label={ariaSummary}
        viewBox={`0 0 ${VBW} ${H}`}
        className="w-full h-auto select-none min-w-[640px]"
        preserveAspectRatio="xMidYMid meet"
      >
        {/* centerline (signal = 0 reference) */}
        <line
          x1={X0}
          y1={midY}
          x2={XF}
          y2={midY}
          stroke={NEUTRAL}
          strokeWidth={1}
          strokeDasharray="3 6"
          opacity={0.25}
        />

        {/* OPPOSITION ARC — Fold tip → DA tip; spans consensus → dissent. */}
        {daItem && (
          <g opacity={focusKey && focusKey !== "devils_advocate" ? 0.15 : 0.7}>
            <path
              d={`M ${XF - 120},${foldThroatY} Q ${(XF - 120 + XM) / 2},${(foldThroatY + daItem.targetY) / 2 - 40} ${XM},${daItem.targetY}`}
              fill="none"
              stroke={IDENTITY_HEX.devils_advocate}
              strokeWidth={1.5}
              strokeDasharray="2 5"
              opacity={0.8}
            />
            <text
              x={(XF - 120 + XM) / 2}
              y={(foldThroatY + daItem.targetY) / 2 - 48}
              textAnchor="middle"
              className="font-mono"
              fontSize={11}
              fill={IDENTITY_HEX.devils_advocate}
              opacity={0.85}
            >
              DA takes the other side, lightly ({daItem.agent.sizeBps} bps)
            </text>
          </g>
        )}

        {/* RIBBONS — fat red bears first, mood, GREEN DA last (z-order). */}
        {items.map((it) => {
          // De-emphasis (when another agent is focused) applies to the GROUP; the
          // confidence->opacity encoding lives on the ribbon PATH only, so label text
          // stays full-opacity and legible (WCAG contrast) instead of inheriting it.
          const deEmph = focusKey && focusKey !== it.key ? 0.4 : 1;
          const meta = AGENT_META[it.key];
          const a = it.agent;
          return (
            <g
              key={it.key}
              tabIndex={0}
              role="button"
              aria-label={`${meta.name}: ${a.action}, signal ${fmtSignal(a.signal)}, confidence ${(a.confidence * 100).toFixed(0)} percent${it.dissent ? ", dissenting from the Fold" : ""}. Press Enter to reveal its reasoning.`}
              className="cursor-pointer focus-visible:opacity-100"
              style={{ transition: "opacity 200ms ease" }}
              opacity={deEmph}
              onMouseEnter={() => setHovered(it.key)}
              onMouseLeave={() => setHovered(null)}
              onFocus={() => setHovered(it.key)}
              onBlur={() => setHovered(null)}
              onClick={() => onSelectAgent?.(it.key)}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  onSelectAgent?.(it.key);
                }
              }}
            >
              {/* the ribbon path: color = DIRECTION, thickness = CONFIDENCE */}
              <path
                d={it.d}
                fill="none"
                stroke={it.color}
                strokeWidth={it.stroke}
                strokeLinecap="round"
                opacity={it.opacity}
                pathLength={1}
                className={motion ? "gb-ribbon-draw" : undefined}
                style={motion ? { animationDelay: `${it.drawIdx * 0.18}s` } : undefined}
              />

              {/* origin dot in IDENTITY color (distinct channel from fill) */}
              <circle cx={X0} cy={it.originY} r={6} fill={it.identity} />

              {/* Origin label anchored LEFT-to-RIGHT from just right of the dot, so it
                  reads into the canvas (X0=80 leaves no left gutter). It sits ABOVE the
                  ribbon, lifted clear of the (fat) stroke; chronos/web are staggered
                  because they share the bear lane. labelLift/labelX computed below. */}
              <text
                x={it.labelX}
                y={it.labelY}
                textAnchor="start"
                className="font-semibold"
                fontSize={15}
                fill={it.identity}
              >
                {meta.name}
              </text>
              <text
                x={it.labelX}
                y={it.labelY + 15}
                textAnchor="start"
                className="font-mono"
                fontSize={11}
                fill={NEUTRAL}
              >
                {a.action} · {fmtSignal(a.signal)} · {(a.confidence * 100).toFixed(0)}%
              </text>

              {/* DISSENT badge pinned ABOVE the dissenting (DA) label, inside canvas. */}
              {it.dissent && (
                <g transform={`translate(${it.labelX}, ${it.labelY - 20})`}>
                  <rect
                    x={0}
                    y={-13}
                    width={84}
                    height={18}
                    rx={4}
                    fill="none"
                    stroke={it.identity}
                    strokeWidth={1}
                  />
                  <text
                    x={42}
                    y={0}
                    textAnchor="middle"
                    className="font-mono font-semibold"
                    fontSize={10}
                    fill={it.identity}
                  >
                    DISSENT ↑
                  </text>
                </g>
              )}
            </g>
          );
        })}

        {/* FOLD NODE — reads round.ensemble directly; accent ring = ensemble direction. */}
        <g
          className={motion ? "animate-reveal-pop" : undefined}
          style={{ transformOrigin: `${XF}px ${foldThroatY}px` }}
        >
          {/* node centered at XF=1040; half-width 54 -> right edge 1094 < VBW 1100 */}
          <rect
            x={XF - 54}
            y={foldThroatY - 58}
            width={108}
            height={116}
            rx={12}
            fill="#13131a"
            stroke={ensembleColor}
            strokeWidth={2}
          />
          <text
            x={XF}
            y={foldThroatY - 36}
            textAnchor="middle"
            className="font-semibold uppercase"
            fontSize={11}
            letterSpacing="1.5"
            fill={NEUTRAL}
          >
            Fold Call
          </text>
          <text
            x={XF}
            y={foldThroatY - 16}
            textAnchor="middle"
            className="font-mono"
            fontSize={12}
            fill={ensembleColor}
          >
            {ensembleAction}
          </text>
          <text
            x={XF}
            y={foldThroatY + 16}
            textAnchor="middle"
            className="font-mono font-bold"
            fontSize={28}
            fill={ensembleColor}
          >
            {arrow} {ensembleSig.toFixed(2)}
          </text>
          <text
            x={XF}
            y={foldThroatY + 36}
            textAnchor="middle"
            className="font-mono"
            fontSize={11}
            fill={NEUTRAL}
          >
            conf {(round.ensemble.confidence * 100).toFixed(0)}%
          </text>
          <text
            x={XF}
            y={foldThroatY + 50}
            textAnchor="middle"
            className="font-mono"
            fontSize={9}
            fill={NEUTRAL}
          >
            Fold conviction
          </text>
        </g>

        {/* The Fold IS the confidence-weighted mean — numbers derived from the data,
            never hardcoded. Pinned to the bottom band, clear of the ribbon mass. */}
        <text
          x={(X0 + XM) / 2}
          y={H - 14}
          textAnchor="middle"
          className="font-mono"
          fontSize={12}
          fill={NEUTRAL}
        >
          {`Σ(signal·conf) ${wSum.toFixed(3)} ÷ Σ(conf) ${cSum.toFixed(2)} = ${(wSum / cSum).toFixed(3)} — the Fold`}
        </text>
      </svg>
      </div>

      {/* legend — the two documented color channels + the geometry */}
      <p className="mt-2 text-[11px] text-signal-neutral font-mono leading-relaxed">
        position = signal (up=bull / down=bear) · thickness = confidence · color =
        direction · label color = which agent
      </p>
    </div>
  );
}
