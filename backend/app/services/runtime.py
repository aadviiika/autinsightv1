from pathlib import Path
from typing import Any
import joblib
import logging
import re
import numpy as np
import pandas as pd
from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class ModelRuntime:
    def __init__(self) -> None:
        self.bundle: dict[str, Any] | None = None
        self.error: str | None = None
        path = Path(settings.model_path)
        try:
            self.bundle = joblib.load(path)
        except FileNotFoundError:
            self.error = (
                f"Model artifact not found at {path}. Train with: python scripts/train_models.py"
            )

    @property
    def ready(self) -> bool:
        return self.bundle is not None

    def predict(
        self, row: dict[str, Any]
    ) -> tuple[float, list[dict[str, Any]], list[dict[str, Any]]]:
        if not self.bundle:
            raise RuntimeError(self.error or "Model is not ready")
        frame = pd.DataFrame([row], columns=self.bundle["feature_names"])
        pipeline = self.bundle["pipeline"]
        probability = float(pipeline.predict_proba(frame)[0, 1])
        explanation: list[dict[str, Any]] = []
        question_contributions = [
            {"item": index, "contribution": None} for index in range(1, 11)
        ]
        explainer = self.bundle.get("explainer")
        if explainer is not None:
            try:
                transformed = pipeline.named_steps["preprocess"].transform(frame)
                values = explainer.shap_values(transformed)
                if hasattr(transformed, "toarray"):
                    transformed = transformed.toarray()
                values = np.asarray(values)
                if isinstance(values, list):
                    values = values[-1]
                if values.ndim == 3:
                    values = values[:, :, -1]
                vals = values[0]
                all_contributions = [
                    {"feature": name, "contribution": float(value)}
                    for name, value in zip(
                        self.bundle.get(
                            "explanation_feature_names", self.bundle["feature_names"]
                        ),
                        vals,
                    )
                ]
                explanation = sorted(
                    all_contributions,
                    key=lambda item: abs(item["contribution"]),
                    reverse=True,
                )[:10]
                for index in range(1, 11):
                    matches = [
                        item["contribution"]
                        for item in all_contributions
                        if re.search(
                            rf"(?:^|[^a-z0-9])a{index}(?:_score)?(?:$|[^0-9])",
                            item["feature"].lower(),
                        )
                    ]
                    if matches:
                        question_contributions[index - 1]["contribution"] = float(sum(matches))
            except Exception:
                logger.exception("SHAP explanation generation failed")
                explanation = []
        return probability, explanation, question_contributions


runtime = ModelRuntime()
