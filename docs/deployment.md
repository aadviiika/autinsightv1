# Deployment preparation

No deployment was performed and no deployment URL exists.

## Vercel frontend

Create a Vercel project with root directory `frontend`. Use the Next.js framework preset and `npm run build`; `frontend/vercel.json` records framework and build command. Set `NEXT_PUBLIC_API_URL` to the backend's HTTPS origin. Do not use localhost in production. Verify pages, browser API calls, errors, and CORS after deployment.

## FastAPI backend

Build from repository root using `docker compose up --build` or deploy `backend/Dockerfile` to a Python container host. The image needs a trained artifact at `MODEL_PATH`; research result JSONs are copied for research pages. Set `ALLOWED_ORIGINS` to exact frontend origins. `/health` is liveness; `/ready` is model readiness. Confirm a live prediction only after XGBoost artifact exists and matches the API schema.

The system macOS OpenMP runtime must be installed using `brew install libomp` before API startup or model training. The versioned model artifact is included. A Linux backend runtime must be built and tested with the pinned dependencies. No cloud account, credentials, hosted service selection, or clinical governance credentials were supplied.
