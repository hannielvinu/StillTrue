from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class VerifyInput(Strict):
    text: str = Field(min_length=1, max_length=20000)
    question: str = Field("", max_length=1000)
    pack: str = "general"
    redact: bool = True


class Claim(Strict):
    id: str
    text: str = Field(min_length=1, max_length=6000)
    subject_key: str = Field(pattern=r"^[a-z0-9_]+$", max_length=120)
    attribute_key: str = Field(pattern=r"^[a-z0-9_]+$", max_length=120)
    asserted_value: str
    unit: str | None = None
    claim_type: Literal[
        "threshold", "deadline", "price", "rate", "requirement", "eligibility", "version"
    ]
    volatility: Literal["high", "medium", "low"] = "medium"
    as_of_hint: str | None = None
    pack_hint: str = "general"


class Claims(Strict):
    claims: list[Claim]


class Judgment(Strict):
    relation: Literal["supports", "contradicts", "insufficient"]
    current_value: str | None = None
    effective_from: str | None = None
    change_summary: str | None = None
    evidence_quote: str | None = None
    source_url: str | None = None
    confidence: float = Field(ge=0, le=1)


class Evidence(Strict):
    url: str
    domain: str
    tier: int
    text: str
    retrieved_at: str
    page_date_hint: str | None = None
