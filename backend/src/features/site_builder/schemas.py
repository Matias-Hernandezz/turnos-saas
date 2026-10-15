from pydantic import BaseModel, Field, HttpUrl
from typing import Any


class ThemeConfig(BaseModel):
    primary: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    background: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    font: str = Field(max_length=120)
    radius: str = Field(max_length=16)
    logo_url: HttpUrl | None = None


class SectionConfig(BaseModel):
    type: str = Field(max_length=64)
    enabled: bool = True
    props: dict[str, Any] = Field(default_factory=dict)


class SiteConfig(BaseModel):
    template: str = Field(max_length=64)
    theme: ThemeConfig
    sections: list[SectionConfig] = Field(default_factory=list, max_length=32)
