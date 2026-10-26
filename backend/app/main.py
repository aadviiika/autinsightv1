from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
from backend.app.core.config import settings
from backend.app.schemas.prediction import ScreeningInput, PredictionResponse
from backend.app.services.runtime import runtime

ROOT = Path(__file__).resolve().parents[2]
app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

LIMITATIONS = [
    "This research tool is not a diagnostic instrument or substitute for professional assessment.",
    "The underlying UCI label is determined by a threshold on these same questionnaire responses; model output is not an independent estimate of autism likelihood.",
]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict[str, str]:
    if not runtime.ready:
        raise HTTPException(status_code=503, detail=runtime.error)
    return {"status": "ready"}


@app.get("/model")
def model_metadata() -> dict[str, str | bool]:
    return {
        "ready": runtime.ready,
        "model": "XGBoost",
        "version": "untrained"
        if not runtime.ready
        else runtime.bundle.get("metadata", {}).get(
            "artifact_version", runtime.bundle.get("version", "unknown")
        ),
    }


@app.get("/research/metrics")
def research_metrics() -> dict:
    path = ROOT / "experiments/results/model_metrics.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="UCI experiment metrics are not available yet.")
    return json.loads(path.read_text())


@app.get("/research/indian-metrics")
def indian_metrics() -> dict:
    path = ROOT / "experiments/results/indian_model_metrics.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Indian cohort metrics are not available yet.")
    return json.loads(path.read_text())


@app.post("/predict", response_model=PredictionResponse)
def predict(data: ScreeningInput) -> PredictionResponse:
    if not runtime.ready:
        raise HTTPException(status_code=503, detail=runtime.error)
    row = {f"a{i}_score": value for i, value in enumerate(data.questions, 1)}
    row.update(
        {
            "age": data.age,
            "gender": data.gender,
            "jaundice": data.jaundice,
            "family_history": data.family_asd,
            "ethnicity": data.ethnicity,
            "who_completed": data.who_completed,
            "relation": data.who_completed,
            "country": data.country,
            "used_app_before": data.used_app_before,
        }
    )
    try:
        probability, explanation, question_contributions = runtime.predict(row)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    confidence = max(probability, 1 - probability)
    thresholds = runtime.bundle.get("thresholds", {"P0": 0.90, "P1": 0.80, "P2": 0.70})
    tier = (
        "P0"
        if confidence >= thresholds["P0"]
        else "P1"
        if confidence >= thresholds["P1"]
        else "P2"
        if confidence >= thresholds["P2"]
        else "P3"
    )
    deferred = tier in {"P2", "P3"}
    label = "positive screening signal" if probability >= 0.5 else "negative screening signal"
    return PredictionResponse(
        status="deferred" if deferred else "screening_result",
        screening_label=label,
        probability=probability,
        reliability_tier=tier,
        message=(
            "The model estimates a class from UCI research data, whose label is determined by a threshold on these same questionnaire answers. It is not an independent or clinical estimate of autism likelihood. "
            + (
                "The model is deferring this response because its provisional confidence tier is low."
                if deferred
                else ""
            )
        )
        if deferred
        else "This model estimates the UCI questionnaire-derived screening class; that class follows a threshold on these same questionnaire answers and is not a clinical diagnosis.",
        explanation=[
            {"feature": item["feature"], "contribution": item["contribution"]}
            for item in explanation
        ],
        explanation_scale="raw_model_score",
        question_contributions=question_contributions,
        limitations=LIMITATIONS,
        model_version=runtime.bundle.get("metadata", {}).get(
            "artifact_version", runtime.bundle.get("version", "unknown")
        ),
    )
