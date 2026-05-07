# DataCraft: A Scikit-Learn Survival Story

You thought data analysis was about spreadsheets. Pivot tables. Maybe a bar chart if you're feeling fancy.

Then **Priya**, the Head of Data at **GreenLeaf Analytics** — a mid-size consulting firm that helps restaurants reduce food waste — sends you a message:

> "We just signed 200 restaurants. They're sending us sales data, weather logs, inventory counts. We need predictions. You start Monday."

You show up. The "data pipeline" is a shared Google Drive folder with 47 CSVs named things like `final_FINAL_v3_USE_THIS.csv`. The previous analyst quit. Their only documentation is a sticky note that says "don't trust the Tuesday numbers."

Your mission: clean the data, find patterns, build models, and ship predictions that actually help restaurants order the right amount of food.

---

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Junior Data Analyst | "I know Python. How hard can ML be?" |
| **Priya** | Head of Data | Thinks in distributions. Draws loss curves on whiteboards. |
| **Chef Marco** | Restaurant Owner | "Your model said I need 200 avocados. I got 12 customers." |
| **Dustin** | Data Engineer | Built the pipeline. Left no docs. Communicates via cryptic SQL views. |
| **The Spreadsheet** | Legacy System | 47 tabs. Circular references. Haunted. |
| **Overfitty** | Your first model | 99% accuracy on training data. Useless in production. |

---

## The Tools

Everything runs on your laptop. No cloud account needed.

| Tool | What It Does |
|---|---|
| **Python 3.11+** | The language |
| **pandas** | Loads, cleans, and transforms tabular data |
| **NumPy** | Fast math on arrays |
| **scikit-learn** | Machine learning models, preprocessing, evaluation |
| **matplotlib / seaborn** | Visualization |
| **Jupyter Notebook** | Interactive exploration (optional — scripts work too) |

---

## How to Read This

Every chapter follows the same loop:

```
  📋 Priya assigns a task
   │
   ▼
  📊 You explore the data (and find problems)
   │
   ▼
  🧹 You clean / transform / engineer features
   │
   ▼
  🤖 You build a model
   │
   ▼
  💥 Something goes wrong (overfitting, data leakage, bad predictions)
   │
   ▼
  🧠 You understand WHY and fix it
   │
   ▼
  📋 Priya assigns the next task
```

No concept shows up before you need it. You won't hear about cross-validation until your model fails in production. You won't touch feature engineering until raw features give garbage predictions.

The disasters come first. The theory follows.

---

## The Roadmap

| Ch | The Disaster | What You Learn |
|---|---|---|
| 1 | The CSV is a mess | pandas basics, loading data, dtypes, missing values |
| 2 | "Why is Tuesday weird?" | EDA, groupby, visualization, outlier detection |
| 3 | Your first model is terrible | Train/test split, LinearRegression, baseline metrics |
| 4 | Chef Marco gets 200 avocados | Overfitting, cross-validation, learning curves |
| 5 | Categorical columns crash `.fit()` | Encoding, OneHotEncoder, ColumnTransformer, pipelines |
| 6 | Features on different scales break everything | StandardScaler, MinMaxScaler, when scaling matters |
| 7 | Linear regression isn't enough | Decision trees, random forests, model comparison |
| 8 | "Which features actually matter?" | Feature importance, permutation importance, selection |
| 9 | The model works — until next month | Time-series awareness, temporal splits, drift detection |
| 10 | Priya wants it in production | Pipelines, joblib serialization, prediction service |

---

## Prerequisites

Three things: Python, pip, and a terminal.

### Python 3.11+

```bash
# Windows (winget)
winget install Python.Python.3.11

# macOS
brew install python@3.11

# Linux
sudo apt install python3.11 python3.11-venv
```

### Project Setup

```bash
mkdir datacraft && cd datacraft
python -m venv .venv

# Activate
source .venv/bin/activate        # macOS/Linux
.venv\Scripts\activate           # Windows

# Install dependencies
pip install pandas numpy scikit-learn matplotlib seaborn jupyter
```

Create a `requirements.txt`:

```
pandas>=2.1
numpy>=1.25
scikit-learn>=1.3
matplotlib>=3.8
seaborn>=0.13
jupyter>=1.0
```

### Verify

```python
import sklearn
print(sklearn.__version__)  # Should be 1.3+
```

If that prints a version number, you're ready.

---

## The Dataset

Throughout this series, we'll work with a synthetic restaurant dataset. Chapter 1 generates it — messy, realistic, and full of the problems you'll find in real data.

The core table: **daily sales per restaurant**.

| Column | Type | Example |
|---|---|---|
| `date` | date | 2024-03-15 |
| `restaurant_id` | string | `greenleaf_042` |
| `day_of_week` | string | Friday |
| `temperature_c` | float | 22.5 |
| `is_holiday` | bool | False |
| `menu_items_available` | int | 34 |
| `staff_count` | int | 8 |
| `marketing_spend` | float | 150.00 |
| `covers` | int | 187 |
| `revenue` | float | 4,230.50 |
| `food_waste_kg` | float | 12.3 |

Some columns have missing values. Some have typos. Tuesday is weird. You'll find out why.

---

[Next: Chapter 1 — "The CSV is a Mess" →](chapter-01-the-csv.md)
