import "./globals.css";
import type { Metadata } from "next";
import { Providers } from "./providers";

// Absolute base for OG/Twitter image URLs — required for share cards to unfurl
// on X in production. Set NEXT_PUBLIC_SITE_URL to the deployed origin.
const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: "Glass-Box Alpha — AI vs Human, attested on-chain",
  description:
    "Four AI agents reason in the open and trade on Mantle. Make your own call, get graded by the same on-chain rule, and see if you can out-reason the AI.",
  openGraph: {
    title: "Glass-Box Alpha — AI vs Human, attested on-chain",
    description:
      "Four AI agents reason in the open and trade on Mantle. Make your call and see if you can out-reason the AI.",
    images: [{ url: "/api/og", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "Glass-Box Alpha — AI vs Human, attested on-chain",
    description: "Can you out-reason four AI trading agents? Reasoning attested on-chain, scored by a verifiable rule. #MantleAIHackathon",
    images: ["/api/og"],
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
