from dataclasses import dataclass


@dataclass
class AezaResponse:
    status: str
    context: str
