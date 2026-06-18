# Ligat Ha'Al — Analytical & Predictive Model

A data science project that scrapes, processes, and models match results from **Israel's Premier Football League (Ligat Ha'Al)** across seasons 2010–2025.
The goal is to predict match outcomes (Home Win / Draw / Away Win) using historical performance features.

---

## 📁 Project Structure

```
.
├── scrapping.py               # Scrapes regular-season match data from Transfermarkt
├── scrapping_playoff.py       # Scrapes playoff match data from Transfermarkt
├── data_merge.py              # Merges regular-season and playoff datasets
├── cleaning.py                # Feature engineering & data cleaning
├── train_model.py             # Model training, evaluation & visualizations
│
├── israel_league_2010_2025.csv         # Raw regular-season data
├── israel_playoffs_2010_2024.csv       # Raw playoff data
├── israel_league_FULL_2010_2025.csv    # Merged full dataset
├── final_training_data.csv             # Cleaned dataset with engineered features
├── model_predictions.csv               # Model output predictions
│
└── final_report.pdf           # Full analytical report
```

---

## ⚙️ Pipeline Overview

The project follows a sequential pipeline:

```
1. scrapping.py
2. scrapping_playoff.py
       ↓
3. data_merge.py
       ↓
4. cleaning.py
       ↓
5. train_model.py
```

### 1. Data Collection (`scrapping.py` & `scrapping_playoff.py`)

Uses **Playwright** to scrape match-by-match data from [Transfermarkt](https://www.transfermarkt.com) for:
- **Regular season**: Seasons 2010–2025, up to 36 matchdays per season (`LEAGUE_ID = "ISR1"`)
- **Playoffs**: Seasons 2010–2024, championship (`ISRF`) and relegation (`ISRA`) playoff rounds

Each match record contains:

| Field | Description |
|---|---|
| `Season` | Season year |
| `Matchday` | Matchday number |
| `Date` | Match date |
| `Home_Team` / `Away_Team` | Team names |
| `Home_Rank` / `Away_Rank` | League position at time of match |
| `Score` | Final score (e.g. `2:1`) |
| `Attendance` | Stadium attendance |

Polite scraping is enforced via random delays (2–4 seconds between requests).

### 2. Data Merge (`data_merge.py`)

Concatenates regular-season and playoff CSVs into a single unified dataset (`israel_league_FULL_2010_2025.csv`), sorted chronologically by season and date.

### 3. Feature Engineering (`cleaning.py`)

Transforms the raw match data into a supervised learning dataset:

- Parses scores into `Home_Goals` and `Away_Goals`
- Encodes match outcome as a **multiclass target**:
  - `0` → Home Win
  - `1` → Draw
  - `2` → Away Win
- Computes **rolling/pre-match features** (leak-free, computed before each match is played):
  - `Home_Team_Points` / `Away_Team_Points` — cumulative league points
  - `Home_Rank` / `Away_Rank` — current league position
  - `Home_Form_5` / `Away_Form_5` — points from the last 5 matches

Output: `final_training_data.csv`

### 4. Model Training (`train_model.py`)

Trains and evaluates two classifiers on a **temporal train/test split** (last 500 matches as test set):

| Model | Details |
|---|---|
| **Logistic Regression** | Baseline — multinomial, LBFGS solver, `StandardScaler` |
| **XGBoost** | `multi:softprob` objective, 100 estimators, max depth 3 |

**Features used:**
- `Home_Team_Points`, `Away_Team_Points`
- `Home_Rank`, `Away_Rank`
- `Home_Form_5`, `Away_Form_5`
- `Attendance`

**Evaluation metrics:** Accuracy, Log Loss, Classification Report

**Saved outputs (`.png` plots):**
- `cm_logreg.png` — Confusion matrix for Logistic Regression
- `cm_xgb.png` — Confusion matrix for XGBoost
- `feat_importance_logreg.png` — Feature importances (mean absolute coefficients)
- `feat_importance_xgb.png` — Feature importances (Gini/Gain)

---

## 🚀 Getting Started

### Prerequisites

Install the required Python packages:

```bash
pip install pandas numpy scikit-learn xgboost matplotlib seaborn playwright
playwright install chromium
```

### Running the Pipeline

```bash
# Step 1: Scrape regular season data
python scrapping.py

# Step 2: Scrape playoff data
python scrapping_playoff.py

# Step 3: Merge datasets
python data_merge.py

# Step 4: Feature engineering
python cleaning.py

# Step 5: Train and evaluate models
python train_model.py
```

> **Note:** If you already have the CSV files, you can skip directly to step 4 or 5.

---

## 📊 Data Source

All match data is sourced from [Transfermarkt.com](https://www.transfermarkt.com) — specifically the Ligat Ha'Al competition pages.
Please be respectful of the site's terms of service when running the scrapers.

---

## 📄 Report

See [`final_report.pdf`](./final_report.pdf) for the full analytical writeup, including methodology, results, and conclusions.
