import { render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it } from "vitest";
import { Dashboard } from "./dashboard";
describe("Dashboard",()=>{it("renders a quote",()=>{render(<Dashboard quotes={[{symbol:"SPY",price:500,change:1,changePercent:.2,volume:10,marketCap:20,asOf:new Date().toISOString(),retrievedAt:new Date().toISOString(),freshness:"live_or_recent",provider:"mock",warnings:[]}]}/>);expect(screen.getByText("SPY")).toBeInTheDocument();expect(screen.getByText("$500.00")).toBeInTheDocument()});it("renders empty state",()=>{render(<Dashboard quotes={[]}/>);expect(screen.getByText(/No market data/)).toBeInTheDocument()})});
