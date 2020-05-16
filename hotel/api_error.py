from dataclasses import dataclass


@dataclass
class APIError(Exception):
    message: str
    code: int = 1
