# AutInsight teammate setup guide

This guide starts the existing AutInsight application from a project ZIP on a teammate's computer. It does not retrain the research models. The trained primary model is included at `models/primary.joblib`.

## 1. Extract and check prerequisites

Extract the ZIP to a folder with a simple path, for example `Documents/AutInsight`. Keep the folder structure intact. Do not unzip inside `frontend` or move individual files out of the project root.

Install:

- Python 3.11 or 3.12
- Node.js 22 (20.19 or newer) and npm
- macOS: Homebrew and the OpenMP runtime (`brew install libomp`)

The ZIP should contain `backend/`, `frontend/`, `models/`, `requirements.txt`, and `experiments/results/`. Do not include `.venv`, `frontend/node_modules`, or raw downloaded datasets in the ZIP; each teammate creates their own environment. The pre-trained model and research metrics are included, so running the application does not require downloading datasets or running training scripts.

## 2. Start the backend

Open Terminal, move into the extracted project root (replace the example path with the real path):

```bash
cd ~/Documents/AutInsight
```

Create and install the Python environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On macOS, install OpenMP once if it is not already available:

```bash
brew install libomp
```

For Apple Silicon Homebrew installations, make the runtime visible to XGBoost in this Terminal session and start the API:

```bash
export DYLD_LIBRARY_PATH="$(brew --prefix libomp)/lib:${DYLD_LIBRARY_PATH:-}"
.venv/bin/uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

If the project ZIP includes the repository's local OpenMP runtime under `work/libomp/libomp/23.1.3/lib`, use this export instead:

```bash
export DYLD_LIBRARY_PATH="$PWD/work/libomp/libomp/23.1.3/lib"
```

Leave this Terminal window running. In a browser, `http://127.0.0.1:8000/health` should show `{"status":"ok"}` and `http://127.0.0.1:8000/ready` should report that the model is ready. The API root `/` is not a webpage and may return 404; that is expected.

### Windows note

Create the venv with `py -3.11 -m venv .venv`, activate it with `.venv\Scripts\activate`, then install requirements. Install a compatible XGBoost/OpenMP runtime if needed. Run `python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000`. The remaining steps are the same.

## 3. Start the frontend

Open a second Terminal window and run:

```bash
cd ~/Documents/AutInsight/frontend
npm ci
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000 npm run dev -- --hostname 127.0.0.1
```

Keep this window running too. Open **http://127.0.0.1:3000**. The backend allows both `127.0.0.1:3000` and `localhost:3000` by default; use one hostname consistently for the browser and API configuration.

## 4. Use the application

1. Start the caregiver flow from the homepage.
2. Answer all ten questionnaire items and complete the caregiver context questions.
3. Review the summary and next steps.
4. Choose **Understand this summary in detail** beside the print action to read the TreeSHAP explanation, project plots, and methods guide.

The current result is stored in browser `sessionStorage` for the tab session. If the tab is closed or the session is cleared, complete the questionnaire again to restore the result.

## Troubleshooting

- **`zsh: command not found: brew`:** Homebrew may not be on PATH. On Apple Silicon run `eval "$(/opt/homebrew/bin/brew shellenv)"`; then use `brew --prefix libomp` to confirm the runtime location.
- **`Failed to fetch`:** Confirm both Terminal windows still show running servers. Visit `/health` and `/ready` on port 8000. Use the same `127.0.0.1` hostname shown above, then reload the frontend. The API must be restarted after changing its CORS settings.
- **`{"detail":"Not Found"}` at port 8000 root:** This is expected. Use `/health` or `/ready` for backend status and port 3000 for the user interface.
- **OpenMP or `libomp` error on macOS:** Install `libomp`, run the `DYLD_LIBRARY_PATH` export in the backend Terminal, and restart Uvicorn in that same Terminal. System updates may be needed if Apple Command Line Tools are too old for Homebrew builds.
- **Port is already in use:** Stop the earlier server with `Ctrl+C`, or change the port and update `NEXT_PUBLIC_API_URL` to match.
- **Frontend dependencies fail:** Use Node.js 20.19+ (Node 22 recommended), remove only `frontend/node_modules`, then retry `npm ci`.

## Important project context

AutInsight is an academic research prototype, not a diagnostic or clinical decision tool. The caregiver-friendly item wording has not been clinically validated. The primary UCI outcome is mechanically derived from the same ten questionnaire responses, so the model reproduces a source-data rule rather than estimating an independent autism likelihood. Do not enter identifying or real patient information.

Research reproduction commands and details are in `docs/reproducibility.md` and `README.md`. Rebuilding models requires separately acquiring source datasets and is not part of the quick application setup.
