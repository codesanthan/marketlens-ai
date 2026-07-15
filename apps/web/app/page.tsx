import { Dashboard } from "./components/dashboard";
import { ErrorState } from "./components/states";
import { api } from "@/lib/api";
import type { Quote } from "@/lib/types";
export default async function Home() { let data:{quotes:Quote[];warnings:string[]}; try { data=await api("/api/v1/market/overview"); } catch(error) { return <><h1 className="mb-2 text-3xl font-bold">Market dashboard</h1><ErrorState message={error instanceof Error?error.message:"Unexpected error"}/></> } return <><h1 className="text-3xl font-bold">Market dashboard</h1><p className="mb-6 mt-2 text-slate-400">Live or latest available market data from the configured connector.</p><Dashboard {...data}/></> }
