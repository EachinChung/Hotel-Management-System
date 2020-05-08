from dataclasses import dataclass


@dataclass
class DiyError(Exception):
    message: str
    code: int = 1
