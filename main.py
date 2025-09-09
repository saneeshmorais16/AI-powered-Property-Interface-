# backend/main.py
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import csv, numpy as np
from sklearn.linear_model import LinearRegression
from typing import List, Optional
from fastapi import Form

DATA_PATH = Path(__file__).parent / "properties.csv"

def load_properties(path: Path):
    items = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            items.append({
                "id": int(row["id"]),
                "title": row["title"],
                "location": row["city"],
                "bedrooms": int(row["bedrooms"]),
                "price": int(row["price"]),
                "area_m2": int(row.get("area_m2", 0) or 0),
                "type": row.get("type", "Unknown"),
            })
    return items

PROPS = load_properties(DATA_PATH)


def fit_model_from_props(props):
    cities = sorted({p["location"] for p in props})
    city_to_idx = {c: i for i, c in enumerate(cities)}
    X, y = [], []
    for p in props:
        X.append([p["bedrooms"], city_to_idx[p["location"]]])
        y.append(p["price"])
    model = LinearRegression().fit(np.array(X), np.array(y))
    return model, city_to_idx

MODEL, CITY_IDX = fit_model_from_props(PROPS)

def predict_price(bedrooms: int, location: str) -> int:
    loc_code = CITY_IDX.get(location, 0)
    return int(round(float(MODEL.predict([[bedrooms, loc_code]])[0])))

def recommend_similar(
    target_price: int,
    target_bedrooms: int,
    target_location: str,
    k: int = 3,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    property_type: Optional[str] = None,
):
    # 1) STRICT filter by selected location
    candidates = [p for p in PROPS if p["location"] == target_location]

    # 2) Optional extra filters
    if min_price is not None:
        candidates = [p for p in candidates if p["price"] >= min_price]
    if max_price is not None:
        candidates = [p for p in candidates if p["price"] <= max_price]
    if property_type:
        candidates = [p for p in candidates if p["type"].lower() == property_type.lower()]

    # 3) If none left, graceful fallback: drop type then widen to same city, then any city
    if not candidates:
        candidates = [p for p in PROPS if p["location"] == target_location] or PROPS

    # 4) Score: closeness to price + small penalty for bedroom mismatch
    scored = []
    for p in candidates:
        price_diff = abs(p["price"] - target_price)
        bed_diff = abs(p["bedrooms"] - target_bedrooms)
        score = price_diff + 180 * bed_diff
        scored.append({**p, "score": score})
    scored.sort(key=lambda x: x["score"])
    return scored[:k]

# --- FastAPI app
app = FastAPI(title="Property API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500", "http://localhost:5500",
        "http://127.0.0.1:8080", "http://localhost:8080", "file://"
    ],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

class PredictRequest(BaseModel):
    bedrooms: int
    location: str

class PredictResponse(BaseModel):
    estimated_price: int

class RecommendRequest(BaseModel):
    bedrooms: int
    location: str
    predicted_price: int
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    property_type: Optional[str] = None
    k: int = 3

@app.get("/healthz")
def health(): return {"status": "ok"}

# NEW: list locations for the dropdown
@app.get("/api/locations", response_model=List[str])
def api_locations():
    return sorted({p["location"] for p in PROPS})

@app.post("/api/predict", response_model=PredictResponse)
def api_predict(req: PredictRequest):
    return {"estimated_price": predict_price(req.bedrooms, req.location)}

# NEW: more flexible search that still recommends "similar"
@app.post("/api/recommend")
def api_recommend(req: RecommendRequest):
    items = recommend_similar(
        req.predicted_price, req.bedrooms, req.location,
        k=req.k, min_price=req.min_price, max_price=req.max_price,
        property_type=req.property_type
    )
    return {"items": items}

# OPTIONAL: direct search endpoint (if you want)
@app.get("/api/search")
def api_search(
    location: str,
    bedrooms: Optional[int] = Query(None),
    min_price: Optional[int] = Query(None),
    max_price: Optional[int] = Query(None),
    property_type: Optional[str] = Query(None),
    limit: int = 20
):
    items = [p for p in PROPS if p["location"] == location]
    if bedrooms is not None:
        items = [p for p in items if p["bedrooms"] == bedrooms]
    if min_price is not None:
        items = [p for p in items if p["price"] >= min_price]
    if max_price is not None:
        items = [p for p in items if p["price"] <= max_price]
    if property_type:
        items = [p for p in items if p["type"].lower() == property_type.lower()]
    return {"items": items[:limit]}

@app.post("/api/contact")
def api_contact(name: str = Form(...), email: str = Form(...), message: str = Form(...)):
    # For now just log it
    print("📩 Contact received:", name, email, message)
    # TODO: save to DB or email
    return {"status": "ok"}
