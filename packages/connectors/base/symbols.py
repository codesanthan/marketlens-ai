import re

# US tickers: 1-5 letters, optionally a class suffix (BRK.B / BRK-B). Yahoo and the SEC both use "-".
_PATTERN = re.compile(r"^[A-Z]{1,5}(-[A-Z]{1,2})?$")


class SymbolNotFoundError(LookupError):
    """The symbol is well-formed but the data source has no such listing."""


def normalize_symbol(value: str) -> str:
    symbol = value.strip().upper().replace(".", "-")
    if not _PATTERN.fullmatch(symbol):
        raise ValueError(f"Invalid ticker symbol: {value[:16]}")
    return symbol
