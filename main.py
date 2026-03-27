from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from mix_design.mix_design_engine import mix_design
from prediction.inference import predict_strength

app = FastAPI(title="Concrete AI System")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

# -----------------------------
# CORS FIX — OPTIONS preflight
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,   # Must be False when using wildcard methods/headers
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
)


# -----------------------------
# REQUEST MODELS
# -----------------------------


class MixDesignInput(BaseModel):
    grade: str
    exposure: str
    slump: float
    max_agg_size: int
    sand_zone: str

    sg_cement: float
    sg_fa: float
    sg_ca: float

    mc_fa: float
    mc_ca: float

    wa_fa: float
    wa_ca: float

    mineral_percent: Optional[float] = 0
    chemical_percent: Optional[float] = 0


class PredictionInput(BaseModel):
    cement: float
    fa: float
    ca: float
    water: float
    wc_ratio: float
    strength_7: float
    target_strength: Optional[float] = None


# -----------------------------
# ROUTES
# -----------------------------

@app.get("/")
def home():
    return {"message": "Concrete Mix Design + AI Prediction API"}


@app.post("/mix-design")
def mix_design_api(data: MixDesignInput):
    result = mix_design(data.dict())
    return result


@app.post("/prediction")
def prediction_api(data: PredictionInput):
    result = predict_strength(data.dict())
    return result