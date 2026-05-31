import { getDefaultConfig } from "@rainbow-me/rainbowkit";
import { defineChain } from "viem";

export const mantleMainnet = defineChain({
  id: 5000,
  name: "Mantle",
  nativeCurrency: { name: "Mantle", symbol: "MNT", decimals: 18 },
  rpcUrls: {
    default: { http: ["https://rpc.mantle.xyz"] },
  },
  blockExplorers: {
    default: { name: "Mantlescan", url: "https://mantlescan.xyz" },
  },
});

export const mantleSepolia = defineChain({
  id: 5003,
  name: "Mantle Sepolia",
  nativeCurrency: { name: "Mantle", symbol: "MNT", decimals: 18 },
  rpcUrls: {
    default: { http: ["https://rpc.sepolia.mantle.xyz"] },
  },
  blockExplorers: {
    default: { name: "Mantlescan Sepolia", url: "https://sepolia.mantlescan.xyz" },
  },
  testnet: true,
});

export const wagmiConfig = getDefaultConfig({
  appName: "Glass-Box Alpha",
  projectId: process.env.NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID ?? "placeholder",
  // Sepolia first = the default chain reads + wallet connect target, since the
  // contracts are live on Mantle Sepolia (5003).
  chains: [mantleSepolia, mantleMainnet],
  ssr: true,
});
