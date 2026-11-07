from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=("../.env", ".env"), extra="ignore")
    app_env: str = "dev"
    mock_mode: bool = False
    bifrost_base_url: str = "http://localhost:8080"
    bifrost_virtual_key: str = ""
    tavily_api_key: str = ""
    extractor_model: str = ""
    verifier_model_a: str = ""
    verifier_model_b: str = ""
    fallback_models: str = ""
    tavily_daily_credit_cap: int = Field(200, ge=0)
    max_claims_per_run: int = Field(8, ge=1, le=20)
    max_input_chars: int = Field(6000, ge=1, le=20000)
    claim_concurrency: int = Field(4, ge=1, le=8)
    tavily_timeout_s: float = Field(20, gt=0)
    llm_timeout_s: float = Field(30, gt=0)
    rate_limit: str = "20/minute"
    cache_ttl_high_h: float = Field(6, ge=0)
    cache_ttl_med_h: float = Field(72, ge=0)
    cache_ttl_low_h: float = Field(336, ge=0)
    cors_origins: str = "http://localhost:5173"
    cache_path: str = ".data/evidence.db"

    @field_validator("extractor_model", "verifier_model_a", "verifier_model_b")
    @classmethod
    def model_id(cls, v: str) -> str:
        if v and ("/" not in v or v.startswith("/")):
            raise ValueError("Model IDs must use provider/model syntax")
        return v

    @property
    def models(self) -> list[str]:
        return list(dict.fromkeys(m for m in [self.verifier_model_a, self.verifier_model_b] if m))

    @property
    def mode(self) -> str:
        return "cross-model" if len({m.split("/")[0] for m in self.models}) > 1 else "single"


@lru_cache
def get_settings() -> Settings:
    return Settings()
