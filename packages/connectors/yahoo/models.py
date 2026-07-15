from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class YahooSnapshot:
    info: dict[str, Any]
    history: Any

