// Mirrors packages/connectors/base/symbols.py: 1-5 letters plus an optional class suffix (BRK.B / BRK-B).
const pattern = /^[A-Z]{1,5}(-[A-Z]{1,2})?$/;
export function normalizeSymbol(value: string): string | null {
  const symbol = value.trim().toUpperCase().replace(".", "-");
  return pattern.test(symbol) ? symbol : null;
}
