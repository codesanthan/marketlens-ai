export type Freshness = "live_or_recent" | "delayed" | "stale" | "unavailable";
export interface Quote { symbol:string; price:number|null; change:number|null; changePercent:number|null; volume:number|null; marketCap:number|null; asOf:string|null; retrievedAt:string; freshness:Freshness; provider:string; warnings:string[] }
export interface Profile { companyName:string|null; marketCap:number|null; fiftyTwoWeekHigh:number|null; fiftyTwoWeekLow:number|null; averageVolume:number|null; warnings:string[] }
export interface Bar { timestamp:string; close:number|null }
