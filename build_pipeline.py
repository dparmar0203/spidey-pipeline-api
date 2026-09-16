from datetime import datetime, timezone

import joblib
import pandas as pd
import sklearn
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from pipeline_def import DistrictFeatureEngineer

sightings = pd.read_csv("sightings.csv", parse_dates=["timestamp"])
locations = pd.read_csv("locations.csv")

hour = sightings["timestamp"].dt.hour
sightings["is_late_night"] = (hour >= 22) | (hour < 5)

date = sightings["timestamp"].dt.date
is_extreme = sightings.groupby(date)["timestamp"].transform(
    lambda s: (s == s.min()) | (s == s.max())
)
sightings["is_first_or_last"] = is_extreme

agg = sightings.groupby("district").agg(
    late_night_ratio=("is_late_night", "mean"),
    first_last_density=("is_first_or_last", "sum"),
    verified_ratio=("is_verified", "mean"),
).reset_index()

district_data = agg.merge(
    locations[
        ["district", "patrol_activity_score", "nightlife_score", "residential_score"]
    ],
    on="district",
    how="inner",
)[
    [
        "district",
        "late_night_ratio",
        "first_last_density",
        "verified_ratio",
        "patrol_activity_score",
        "nightlife_score",
        "residential_score",
    ]
]

district_names = district_data["district"].tolist()
numeric_data = district_data.drop(columns=["district"])

pipeline = Pipeline([
    ("features", DistrictFeatureEngineer()),
    ("scale", StandardScaler()),
])

matrix = pipeline.fit_transform(numeric_data)

bundle = {
    "pipeline": pipeline,
    "matrix": matrix,
    "district_names": district_names,
    "metadata": {
        "steps": [name for name, _ in pipeline.steps],
        "built_at": datetime.now(timezone.utc).isoformat(),
        "sklearn_version": sklearn.__version__,
    },
}

joblib.dump(bundle, "pipeline.joblib")

print(f"Number of districts: {len(district_names)}")
print(f"Matrix shape: {matrix.shape}")
print(f"sklearn version: {sklearn.__version__}")
