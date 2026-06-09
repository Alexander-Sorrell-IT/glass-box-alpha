import type { Metadata } from "next";
import Link from "next/link";

// Share landing page. Carries dynamic OpenGraph/Twitter metadata so a tweeted
// link unfurls into the round-result card (rendered by /api/og with the same
// params). This is the page the "Share on X" button links to.

type SP = { [key: string]: string | string[] | undefined };

function ogImageUrl(sp: SP): string {
  const params = new URLSearchParams();
  for (const [k, v] of Object.entries(sp)) {
    if (typeof v === "string") params.set(k, v);
  }
  return `/api/og?${params.toString()}`;
}

export async function generateMetadata({
  searchParams,
}: {
  searchParams: Promise<SP>;
}): Promise<Metadata> {
  const sp = await searchParams;
  const beat = sp.beat === "1";
  const vs = typeof sp.vs === "string" ? sp.vs : "the AI";
  const human = typeof sp.human === "string" ? sp.human : "0";
  const agent = typeof sp.agent === "string" ? sp.agent : "0";
  const title = beat
    ? `I beat ${vs} on Glass-Box Alpha`
    : `${vs} beat me on Glass-Box Alpha`;
  const description = `Me ${human}bps vs ${vs} ${agent}bps — scored under the same rule the agents face (simulated round). Think you can out-reason the AI?`;
  const image = ogImageUrl(sp);

  return {
    title,
    description,
    openGraph: { title, description, images: [{ url: image, width: 1200, height: 630 }] },
    twitter: { card: "summary_large_image", title, description, images: [image] },
  };
}

export default async function SharePage({ searchParams }: { searchParams: Promise<SP> }) {
  const sp = await searchParams;
  const beat = sp.beat === "1";
  const vs = typeof sp.vs === "string" ? sp.vs : "the AI";

  return (
    <main className="min-h-screen px-6 py-12 max-w-3xl mx-auto text-center">
      <h1 className="text-2xl font-bold tracking-tight mb-2">
        {beat ? `🏆 Beat ${vs}` : `🤖 ${vs} won that one`}
      </h1>
      <p className="text-sm text-signal-neutral mb-6">
        Human and AI are scored by the same realized-PnL rule the agents face. This is a{" "}
        <span className="text-signal-bear font-semibold">simulated round</span> — the on-chain settlement
        loop lands with the live deploy.
      </p>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={ogImageUrl(sp)}
        alt="Round result card"
        className="w-full rounded-xl border border-border mb-6"
      />
      <Link href="/" className="button-primary inline-block px-6 py-3">
        Make your own call →
      </Link>
    </main>
  );
}
