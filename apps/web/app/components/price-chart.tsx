"use client";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { Bar } from "@/lib/types";
export function PriceChart({bars}:{bars:Bar[]}) { return <div className="h-72 w-full"><ResponsiveContainer><LineChart data={bars}><XAxis dataKey="timestamp" tickFormatter={v=>new Date(v).toLocaleDateString()} hide/><YAxis domain={["auto","auto"]} width={60}/><Tooltip labelFormatter={v=>new Date(v).toLocaleString()}/><Line type="monotone" dataKey="close" stroke="#22d3ee" dot={false}/></LineChart></ResponsiveContainer></div> }
