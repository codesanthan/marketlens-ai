"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { normalizeSymbol } from "@/lib/symbols";

export function TickerSearch() {
  const router = useRouter();
  const [value, setValue] = useState("");
  const [invalid, setInvalid] = useState(false);
  return <form role="search" className="flex items-center gap-2" onSubmit={event => {
    event.preventDefault();
    const symbol = normalizeSymbol(value);
    setInvalid(!symbol);
    if (symbol) { setValue(""); router.push(`/ticker/${symbol}`); }
  }}>
    <input aria-label="Ticker symbol" aria-invalid={invalid} value={value} onChange={event => { setValue(event.target.value); setInvalid(false); }}
      placeholder="Ticker, e.g. PLTR" maxLength={8} autoCapitalize="characters" spellCheck={false}
      className={`w-36 rounded-md border bg-slate-900 px-3 py-1.5 text-sm uppercase placeholder:normal-case placeholder:text-slate-500 focus:outline-none focus:ring-1 focus:ring-cyan-400 ${invalid ? "border-red-400" : "border-slate-700"}`}/>
    <button type="submit" className="rounded-md bg-cyan-500 px-3 py-1.5 text-sm font-semibold text-slate-950 hover:bg-cyan-400">Go</button>
  </form>;
}
