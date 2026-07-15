import { render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it } from "vitest";
import { ErrorState } from "./states";
describe("ErrorState",()=>{it("shows API errors",()=>{render(<ErrorState message="Market data unavailable"/>);expect(screen.getByRole("alert")).toHaveTextContent("Market data unavailable")})});
