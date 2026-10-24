"""Validated request contracts in canonical pixel coordinates."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

Role = Literal["product", "headline", "logo", "cta", "other"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Target(StrictModel):
    id: str = Field(pattern=r"^[a-zA-Z0-9_-]{1,64}$")
    label: str = Field(min_length=1, max_length=80)
    role: Role = "product"
    box: tuple[int, int, int, int]
    priority: int = Field(default=1, ge=1, le=3)

    @model_validator(mode="after")
    def valid_box(self):
        l, t, r, b = self.box
        if not (0 <= l < r and 0 <= t < b):
            raise ValueError("Target must have positive area and nonnegative coordinates.")
        return self


class Annotation(StrictModel):
    targets: list[Target] = Field(max_length=8)
    confirmed: bool = True

    @model_validator(mode="after")
    def unique_targets(self):
        if len({t.id for t in self.targets}) != len(self.targets):
            raise ValueError("Target IDs must be unique.")
        return self


class ProjectPatch(StrictModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    archived: bool | None = None


class Adjustment(StrictModel):
    label: str = Field(default="Controlled adjustment", min_length=1, max_length=100)
    brightness: float = Field(default=1, ge=0.65, le=1.35)
    contrast: float = Field(default=1, ge=0.65, le=1.5)
    saturation: float = Field(default=1, ge=0, le=1.5)
    sharpness: float = Field(default=1, ge=0, le=2)
    target_id: str | None = None


class ComparisonRequest(StrictModel):
    before_run_id: str = Field(pattern=r"^[a-f0-9]{32}$")
    after_run_id: str = Field(pattern=r"^[a-f0-9]{32}$")
