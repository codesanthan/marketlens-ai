import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";
export const metadata: Metadata = { title: "MarketLens AI", description: "Market research dashboard" };
export default function Layout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body><header className="border-b border-slate-800"><nav className="mx-auto flex max-w-7xl items-center justify-between p-5"><Link className="text-xl font-bold text-cyan-400" href="/">MarketLens AI</Link><Link className="text-sm text-slate-300 hover:text-white" href="/system">System health</Link></nav></header><main className="mx-auto max-w-7xl p-5">{children}</main><footer className="mx-auto max-w-7xl p-5 text-xs text-slate-500">Research and educational use only. Not investment advice.</footer></body></html>;
}
