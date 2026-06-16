# TINHLE AI

> Agricultural drought early warning and environmental intelligence platform for Zimbabwe.

## Architecture

- **Backend**: FastAPI + Python ML models (Railway)
- **Frontend**: Vanilla HTML/CSS/JS dashboard (Railway Static)
- **Models**: scikit-learn `.joblib` rainfall & drought classifiers
- **Data Sources**: NASA POWER, Open-Meteo, MODIS NDVI, Community Intel

## Local Development

### 1. Clone and set up environment

```bash
git clone https://github.com/YOUR_USERNAME/tinhle-ai.git
cd tinhle-ai
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your real credentials
```

### 3. Start the API

```bash
uvicorn app:app --reload
```

### 4. Open the dashboard

Open `dashboard/index.html` in your browser.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service status |
| GET | `/health` | Health check |
| GET | `/predict` | Run full risk assessment |
| GET | `/send-report` | Email the latest report |

## Deployment

- **Backend**: Railway — auto-deploys on push to `main`
- **Frontend**: Railway Static — served from `dashboard/` directory

## Environment Variables (set in Railway dashboard)

| Variable | Description |
|----------|-------------|
| `GMAIL_USER` | Gmail address for alert emails |
| `GMAIL_APP_PASSWORD` | Gmail 16-char app password |
| `GEE_PROJECT` | Google Earth Engine project ID |

## Project Structure

```
tinhle-ai/
├── app.py                  # FastAPI entry point
├── requirements.txt        # Python dependencies
├── Procfile               # Railway startup command
├── railway.toml           # Railway config
├── data/                  # Data scripts + static CSVs
│   ├── monthly_baselines.csv
│   ├── community_reports.csv
│   └── ...py              # Pipeline scripts
├── models/                # Trained ML models
│   ├── best_rainfall_model.joblib
│   └── best_drought_classifier.joblib
└── dashboard/             # Frontend
    ├── index.html
    ├── styles.css
    └── app.js
```

## License

Private — TINHLE AI Research Project
