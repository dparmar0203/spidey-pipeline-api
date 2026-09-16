# spidey-pipeline-api

A scikit-learn pipeline that engineers per-district "patrol district" features
from sighting and location data, served as a FastAPI app and deployed on
Modal.

## Data

- `sightings.csv` — individual sighting records (timestamp, district,
  verification status, etc.)
- `locations.csv` — one row per district with `patrol_activity_score`,
  `nightlife_score`, `residential_score`, etc.

## Project layout

- `pipeline_def.py` — `DistrictFeatureEngineer`, a custom scikit-learn
  transformer that engineers 6 features per district (`late_night_ratio`,
  `first_last_density`, `verified_ratio`, `quietness`, `low_profile`,
  `residential_score`).
- `build_pipeline.py` — aggregates `sightings.csv` per district, joins with
  `locations.csv`, fits a `Pipeline([DistrictFeatureEngineer, StandardScaler])`,
  and dumps the fitted pipeline + transformed matrix + district names +
  metadata to `pipeline.joblib`.
- `serve.py` — FastAPI app that loads `pipeline.joblib` at import time and
  exposes `/health`, `/info`, and `/recommend`.
- `modal_serve.py` — Modal deployment config that packages `serve.py`,
  `pipeline_def.py`, and `pipeline.joblib` into an image and serves the
  FastAPI app as a Modal web endpoint.
- `spidey-pipeline-api.postman_collection.json` — Postman collection with
  requests + test assertions against the deployed API.

## Setup

```bash
uv sync
```

## Build the pipeline artifact

```bash
uv run python build_pipeline.py
```

This reads `sightings.csv` and `locations.csv` from the current directory
and writes `pipeline.joblib`.

## Run the API locally

```bash
uv run uvicorn serve:app --reload
```

Then visit `http://localhost:8000/docs` for the interactive Swagger UI.

### Endpoints

- `GET /health` — `{"status": "ok"}` if the pipeline artifact loaded, else
  `503`.
- `GET /info` — the artifact's metadata and district names, else `503`.
- `POST /recommend` — body:
  ```json
  {
    "prioritize_late_night": 0.8,
    "prioritize_isolation": 0.5,
    "prioritize_low_profile": 0.6,
    "prioritize_residential": 0.7
  }
  ```
  Each field is a float in `[0, 1]`. Returns the top 5 scored districts:
  `[{"district": ..., "score": ...}, ...]`.

## Deploy to Modal

```bash
uv run modal deploy modal_serve.py
```

This prints a public URL, currently:

```
https://dparmar0203--spidey-pipeline-api-fastapi-app.modal.run
```

CORS is enabled (`allow_origins=["*"]`, `GET`/`POST`) so browser-based
frontends can call the API directly.

## Testing with Postman

Import `spidey-pipeline-api.postman_collection.json` into Postman
(File → Import). It includes:

1. `GET /health` — expects `200`
2. `GET /info` — expects `200`
3. `POST /recommend` with a valid body — expects `200`
4. `POST /recommend` with an out-of-range value — expects `422`
