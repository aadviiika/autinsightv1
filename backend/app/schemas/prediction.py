from typing import Any, Literal
from pydantic import BaseModel, Field, field_validator


class ScreeningInput(BaseModel):
    """Questionnaire and context variables supported by UCI child dataset."""

    age: float = Field(ge=4, le=11, description="Source dataset range: 4–11 years")
    gender: Literal["m", "f", "unknown"] = "unknown"
    jaundice: Literal["yes", "no", "unknown"] = "unknown"
    family_asd: Literal["yes", "no", "unknown"] = "unknown"
    ethnicity: str = "Unknown"
    who_completed: str = "Unknown"
    country: str = "Unknown"
    used_app_before: str = "no"
    questions: list[int] = Field(min_length=10, max_length=10)

    @field_validator("questions")
    @classmethod
    def binary_answers(cls, values: list[int]) -> list[int]:
        if any(value not in (0, 1) for value in values):
            raise ValueError("Questionnaire responses must be 0 or 1")
        return values


class ExplanationItem(BaseModel):
    feature: str
    contribution: float


class QuestionContribution(BaseModel):
    item: int
    contribution: float | None = None


class PredictionResponse(BaseModel):
    status: str
    screening_label: str
    probability: float
    reliability_tier: str
    message: str
    explanation: list[ExplanationItem] = []
    question_contributions: list[QuestionContribution] = []
    explanation_scale: str = "raw_model_score"
    limitations: list[str]
    model_version: str
    counterfactual: dict[str, Any] | None = None
