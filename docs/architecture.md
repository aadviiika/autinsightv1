# Architecture

```mermaid
sequenceDiagram
  participant U as User browser
  participant F as Next.js frontend
  participant A as FastAPI
  participant M as Saved XGBoost pipeline
  participant J as Research JSON
  U->>F: Enter screening responses
  F->>A: POST /predict (JSON)
  A->>A: Pydantic validation
  A->>M: preprocess + predict_proba
  M-->>A: probability + optional SHAP
  A-->>F: screening label, provisional tier, limits
  F->>A: GET /research/metrics
  A->>J: Read generated experiment result
  J-->>A: UCI/Indian metrics
  A-->>F: Research metrics
```

Frontend/backend deploy independently. Browser prediction request flow is Next.js → FastAPI → validated schema → saved preprocessing/model bundle → reliability categorization → optional explanation → JSON. The frontend never makes an authoritative prediction. `NEXT_PUBLIC_API_URL` configures browser-to-backend requests; `ALLOWED_ORIGINS` restricts FastAPI CORS origins.

Research scripts acquire and audit UCI and the Indian PLOS S2 workbook independently, fit dataset-specific preprocessing/model pipelines, and write metrics. Their target meanings and features are incompatible for pooling; the app's primary prediction schema is UCI only. The Indian work is a separate research analysis. A versioned XGBoost artifact is included and local `/ready` plus prediction have been verified with a compatible OpenMP runtime. Research JSON endpoints are independent of model loading.
