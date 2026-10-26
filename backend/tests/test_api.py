from fastapi.testclient import TestClient
from backend.app.main import app


def test_health_readiness_and_model_metadata():
    client = TestClient(app)
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/ready").status_code == 200
    model = client.get("/model").json()
    assert model["ready"] is True
    assert model["model"] == "XGBoost"


def test_invalid_questionnaire_rejected():
    client = TestClient(app)
    response = client.post(
        "/predict",
        json={"age": 4, "gender": "f", "jaundice": "no", "family_asd": "no", "questions": [0] * 9},
    )
    assert response.status_code == 422


def test_genuine_model_prediction_and_explanation():
    client = TestClient(app)
    response = client.post(
        "/predict",
        json={
            "age": 6,
            "gender": "m",
            "jaundice": "no",
            "family_asd": "no",
            "ethnicity": "Asian",
            "who_completed": "Parent",
            "country": "India",
            "used_app_before": "no",
            "questions": [0, 0, 1, 0, 1, 1, 1, 0, 1, 1],
        },
    )
    assert response.status_code == 200
    result = response.json()
    assert 0 <= result["probability"] <= 1
    assert result["reliability_tier"] in {"P0", "P1", "P2", "P3"}
    assert result["model_version"] == "autinsight-0.1.0-uci419-seed17"
    assert result["explanation_scale"] == "raw_model_score"
    assert result["explanation"]
    assert any("not a diagnostic" in item.lower() for item in result["limitations"])


def test_research_metrics_available():
    client = TestClient(app)
    response = client.get("/research/metrics")
    assert response.status_code == 200
    assert response.json()["n_test"] == 73
    indian = client.get("/research/indian-metrics")
    assert indian.status_code == 200
    assert indian.json()["n_test"] == 56
