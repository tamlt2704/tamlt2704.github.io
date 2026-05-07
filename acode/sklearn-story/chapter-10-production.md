# Chapter 10: Ship It

[← Chapter 9: The Model Works — Until Next Month](chapter-09-time-series.md)

---

## The Task

Priya's final assignment:

> "Package this so Dustin can run predictions from a script. No Jupyter notebooks in production. I want: train, predict, and retrain — three commands. And save the model so we don't retrain every time we need a prediction."

Time to turn a notebook experiment into something that actually runs.

---

## The Final Pipeline

Everything we've built across 9 chapters, consolidated into one clean pipeline:

```python
# train.py
"""Train the GreenLeaf revenue prediction model."""
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
from pathlib import Path
from datetime import datetime

# ── Config ───────────────────────────────────────
NUMERIC_FEATURES = ["temperature_c", "marketing_spend", "month", "is_weekend"]
CATEGORICAL_FEATURES = ["day_of_week", "restaurant_id"]
TARGET = "revenue"
MODEL_DIR = Path("models")
DATA_DIR = Path("data")


def load_and_prepare(path: str) -> pd.DataFrame:
    """Load CSV and engineer features."""
    df = pd.read_csv(path, parse_dates=["date"])
    df = df.dropna(subset=[TARGET])
    df["month"] = df["date"].dt.month
    df["is_weekend"] = df["day_of_week"].isin(["Saturday", "Sunday"]).astype(int)
    df = df.sort_values("date").reset_index(drop=True)
    return df


def build_pipeline() -> Pipeline:
    """Construct the full preprocessing + model pipeline."""
    numeric_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
    ])

    categorical_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
        ("onehot", OneHotEncoder(drop="first", handle_unknown="ignore")),
    ])

    preprocessor = ColumnTransformer(transformers=[
        ("num", numeric_transformer, NUMERIC_FEATURES),
        ("cat", categorical_transformer, CATEGORICAL_FEATURES),
    ])

    return Pipeline([
        ("preprocessor", preprocessor),
        ("model", GradientBoostingRegressor(
            n_estimators=300,
            max_depth=5,
            learning_rate=0.1,
            random_state=42,
        )),
    ])


def train(data_path: str = "data/restaurant_sales_clean.csv",
          months_back: int = 6) -> dict:
    """Train model on recent data and save to disk."""
    df = load_and_prepare(data_path)

    # Use rolling window: last N months
    cutoff = df["date"].max() - pd.DateOffset(months=months_back)
    train_df = df[df["date"] >= cutoff]

    X = train_df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y = train_df[TARGET]

    # Build and evaluate
    pipeline = build_pipeline()

    # Temporal cross-validation
    tscv = TimeSeriesSplit(n_splits=3)
    cv_scores = cross_val_score(pipeline, X, y, cv=tscv, scoring="r2")

    # Final fit on all training data
    pipeline.fit(X, y)

    # Save model
    MODEL_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_path = MODEL_DIR / f"model_{timestamp}.joblib"
    joblib.dump(pipeline, model_path)

    # Also save as "latest"
    latest_path = MODEL_DIR / "model_latest.joblib"
    joblib.dump(pipeline, latest_path)

    metrics = {
        "cv_r2_mean": cv_scores.mean(),
        "cv_r2_std": cv_scores.std(),
        "train_rows": len(train_df),
        "train_start": str(train_df["date"].min().date()),
        "train_end": str(train_df["date"].max().date()),
        "model_path": str(model_path),
        "timestamp": timestamp,
    }

    print(f"✓ Model trained on {len(train_df)} rows")
    print(f"  Period: {metrics['train_start']} → {metrics['train_end']}")
    print(f"  CV R²: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    print(f"  Saved: {model_path}")

    return metrics


if __name__ == "__main__":
    train()
```

---

## The Prediction Script

```python
# predict.py
"""Generate predictions for upcoming days."""
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from train import NUMERIC_FEATURES, CATEGORICAL_FEATURES, TARGET

MODEL_PATH = Path("models/model_latest.joblib")


def predict(input_path: str, output_path: str = "data/predictions.csv") -> pd.DataFrame:
    """Load model and generate predictions."""
    # Load model
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"No model found at {MODEL_PATH}. Run train.py first.")

    pipeline = joblib.load(MODEL_PATH)
    print(f"✓ Loaded model from {MODEL_PATH}")

    # Load input data
    df = pd.read_csv(input_path, parse_dates=["date"])
    df["month"] = df["date"].dt.month
    df["is_weekend"] = df["day_of_week"].isin(["Saturday", "Sunday"]).astype(int)

    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]

    # Predict
    predictions = pipeline.predict(X)

    # Output
    results = df[["date", "restaurant_id", "day_of_week"]].copy()
    results["predicted_revenue"] = predictions.round(2)
    results.to_csv(output_path, index=False)

    print(f"✓ Generated {len(results)} predictions → {output_path}")
    print(results.head(10).to_string(index=False))

    return results


if __name__ == "__main__":
    import sys
    input_file = sys.argv[1] if len(sys.argv) > 1 else "data/tomorrow.csv"
    predict(input_file)
```

---

## The Retrain Script

```python
# retrain.py
"""Retrain model with fresh data and validate against previous performance."""
import pandas as pd
import joblib
from pathlib import Path
from train import train, load_and_prepare, build_pipeline, NUMERIC_FEATURES, CATEGORICAL_FEATURES, TARGET
from sklearn.metrics import mean_absolute_error


def retrain_and_validate(data_path: str = "data/restaurant_sales_clean.csv",
                         months_back: int = 6,
                         drift_threshold: float = 1.2) -> dict:
    """Retrain and compare against previous model."""
    # Load current model for comparison
    old_model_path = Path("models/model_latest.joblib")
    has_old_model = old_model_path.exists()

    if has_old_model:
        old_pipeline = joblib.load(old_model_path)

    # Train new model
    metrics = train(data_path, months_back)

    # Compare on most recent month
    df = load_and_prepare(data_path)
    recent = df[df["date"] >= df["date"].max() - pd.DateOffset(months=1)]
    X_recent = recent[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y_recent = recent[TARGET]

    new_pipeline = joblib.load(Path("models/model_latest.joblib"))
    new_mae = mean_absolute_error(y_recent, new_pipeline.predict(X_recent))

    if has_old_model:
        old_mae = mean_absolute_error(y_recent, old_pipeline.predict(X_recent))
        improvement = (old_mae - new_mae) / old_mae * 100

        print(f"\n--- Comparison ---")
        print(f"  Old model MAE: ${old_mae:.2f}")
        print(f"  New model MAE: ${new_mae:.2f}")
        print(f"  Improvement:   {improvement:+.1f}%")

        if new_mae > old_mae * drift_threshold:
            print(f"  ⚠️  New model is WORSE. Investigate before deploying.")
    else:
        print(f"\n  New model MAE: ${new_mae:.2f} (no previous model to compare)")

    return metrics


if __name__ == "__main__":
    retrain_and_validate()
```

---

## Model Serialization: joblib vs pickle

```python
import joblib

# Save
joblib.dump(pipeline, "models/model_latest.joblib")

# Load
loaded_pipeline = joblib.load("models/model_latest.joblib")

# Verify it works
sample = X_test.iloc[:5]
assert np.allclose(pipeline.predict(sample), loaded_pipeline.predict(sample))
```

Why `joblib` over `pickle`?
- Faster for objects with large NumPy arrays (like tree ensembles)
- Same API: `dump()` and `load()`
- The saved file contains the entire pipeline: imputers, encoders, scaler, model — everything needed to go from raw input to prediction

---

## Project Structure

```
datacraft/
├── data/
│   ├── restaurant_sales_raw.csv      ← original messy data
│   ├── restaurant_sales_clean.csv    ← cleaned version
│   ├── tomorrow.csv                  ← input for predictions
│   └── predictions.csv               ← output
├── models/
│   ├── model_latest.joblib           ← current production model
│   └── model_20240715_143022.joblib  ← timestamped backup
├── plots/                            ← EDA and diagnostic charts
├── generate_data.py                  ← creates synthetic dataset
├── train.py                          ← training pipeline
├── predict.py                        ← prediction script
├── retrain.py                        ← retraining with validation
└── requirements.txt
```

---

## Usage

```bash
# First time: generate data and train
python generate_data.py
python train.py

# Daily: generate predictions
python predict.py data/tomorrow.csv

# Monthly: retrain on fresh data
python retrain.py
```

---

## What We Built (The Full Journey)

| Chapter | Problem | Solution | R² |
|---|---|---|---|
| 1 | CSV is a mess | pandas cleaning, dtypes, missing values | — |
| 2 | Tuesday is weird | EDA, groupby, visualization | — |
| 3 | First model is terrible | Train/test split, baseline comparison | 0.43 |
| 4 | Overfitting (avocado incident) | Cross-validation, regularization | 0.45 |
| 5 | Categoricals crash .fit() | OneHotEncoder, ColumnTransformer, Pipeline | 0.75 |
| 6 | Scale breaks KNN | StandardScaler, when to scale | 0.75 |
| 7 | Linear isn't enough | Random Forest, Gradient Boosting | 0.86 |
| 8 | Black box predictions | Feature importance, partial dependence | 0.86 |
| 9 | Model degrades over time | Temporal splits, rolling retrain, drift detection | 0.78* |
| 10 | Ship it | joblib, scripts, project structure | — |

*Temporal CV gives the honest number. Random CV (0.86) overestimates.

---

## Final Report to Priya

> **GreenLeaf Revenue Prediction — Production Ready**
>
> - **Model**: Gradient Boosting (300 trees, depth 5)
> - **Features**: temperature, marketing spend, day of week, restaurant, month, weekend flag
> - **Performance**: MAE ≈ $400 (10% error on avg $4,000 daily revenue)
> - **Retraining**: Monthly on 6-month rolling window
> - **Monitoring**: Alert if MAE exceeds 120% of baseline
> - **Deployment**: Three scripts — train, predict, retrain
>
> Chef Marco can now order with confidence. The avocado incident won't happen again.

Priya: "Nice work. Now do the same thing for food waste prediction."

You open a new file. `chapter_01_waste.py`. Here we go again.

---

## What You Learned (Series Recap)

1. **Real data is messy** — budget 30% of your time for cleaning
2. **EDA before modeling** — visualization catches bugs that code misses
3. **Always split train/test** — never evaluate on training data
4. **Compare to a baseline** — "is this good?" needs "compared to what?"
5. **Data leakage** is the #1 silent killer of ML projects
6. **Cross-validation** gives honest estimates; one split can mislead
7. **Overfitting** = memorizing noise; **underfitting** = missing signal
8. **Encode categoricals properly** — one-hot for nominal, ordinal for ordered
9. **Scale when needed** — distance-based and regularized models need it; trees don't
10. **Pipelines prevent mistakes** — preprocessing + model in one object
11. **Feature engineering > algorithm tuning** — going from 4 features to 6 helped more than switching algorithms
12. **Trees capture non-linear patterns** that linear models miss
13. **Explainability matters** — stakeholders need to understand *why*
14. **Models degrade over time** — monitor, retrain, repeat
15. **Ship simple** — three scripts beat a complex platform for a team of 3

---

## Next Steps (If You Keep Going)

- **Food waste prediction** — same pipeline, different target
- **Classification** — "will this restaurant exceed capacity?" (yes/no)
- **Clustering** — group restaurants by behavior patterns
- **Deep learning** — when you have 100× more data and non-tabular inputs
- **MLOps** — MLflow for experiment tracking, Docker for deployment, Airflow for scheduling

But that's another series.

---

*Thanks for reading. Now go build something.*
