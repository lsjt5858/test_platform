from dataclasses import dataclass
from typing import Optional

@dataclass
class TokenPair:
    access: str
    refresh: str
    token_type: Optional[str] = "Bearer"