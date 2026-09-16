import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

try:
    bundle = joblib.load("pipeline.joblib")
    ARTIFACT_LOADED = True
except Exception:
    bundle = None
    ARTIFACT_LOADED = False


class RecommendRequest(BaseModel):
    prioritize_late_night: float = Field(ge=0, le=1)
    prioritize_isolation: float = Field(ge=0, le=1)
    prioritize_low_profile: float = Field(ge=0, le=1)
    prioritize_residential: float = Field(ge=0, le=1)


@app.get("/health")
def health():
    if not ARTIFACT_LOADED:
        raise HTTPException(status_code=503, detail="Artifact not loaded")
    return {"status": "ok"}


@app.get("/info")
def info():
    if not ARTIFACT_LOADED:
        raise HTTPException(status_code=503, detail="Artifact not loaded")
    return {
        "metadata": bundle["metadata"],
        "district_names": bundle["district_names"],
    }


@app.post("/recommend")
def recommend(request: RecommendRequest):
    if not ARTIFACT_LOADED:
        raise HTTPException(status_code=503, detail="Artifact not loaded")

    matrix = bundle["matrix"]
    district_names = bundle["district_names"]

    scores = []
    for district, row in zip(district_names, matrix):
        late_night_ratio, first_last_density_norm, _verified_ratio, quietness, low_profile, residential_score = row
        score = (
            request.prioritize_late_night * late_night_ratio
            + request.prioritize_isolation * ((first_last_density_norm + quietness) / 2)
            + request.prioritize_low_profile * low_profile
            + request.prioritize_residential * residential_score
        )
        scores.append({"district": district, "score": float(score)})

    scores.sort(key=lambda x: x["score"], reverse=True)
    return scores[:5]
