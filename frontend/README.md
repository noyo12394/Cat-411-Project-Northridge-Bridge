# Bridge Vulnerability Demo Frontend

This frontend is a React + Tailwind + Recharts research/demo website layered on top of the bridge vulnerability repository.

## What it does

- tells the repo story as a premium research/demo website
- separates intrinsic vulnerability, event damage, and inspection prioritization
- loads repo-exported JSON when available
- falls back gracefully when browser-ready artifacts are missing or obviously degenerate

## Run locally

```bash
cd frontend
npm install
npm run dev
```

## Export repo outputs into the website

The frontend expects browser-friendly JSON in `public/data` and selected figure assets in `public/research`.

From the `frontend` directory run:

```bash
python3 tools/export_repo_data.py
```

That script reads the repo's processed CSVs and copies selected figure exports into the frontend public directory.

## Data adapter contract

The site looks for these files first:

- `public/data/site_summary.json`
- `public/data/damage_state_best_by_feature_set.json`
- `public/data/future_scenario_summary.json`
- `public/data/ml_hybrid_best_by_feature_set.json`
- `public/data/ml_recommended_hybrid_metrics.json`
- `public/data/ml_recommended_hybrid_feature_importance.json`
- `public/data/data_health.json`
- `public/data/proxy_validation.json`
- `public/research/manifest.json`

## Important modeling discipline baked into the UI

- `PGA` is excluded from the default intrinsic vulnerability mode
- `PGA` appears only in the event damage scenario mode
- `ADT` is used only in prioritization / consequence logic
- `NDVI` is treated only as an optional post-event adjustment / proxy layer

## Replacing the adapter with a live model later

The two main files to swap out are:

- `src/lib/dataAdapter.js`
- `src/lib/modelAdapter.js`

You can keep the UI and replace only those adapters with:

- a real API client
- a JSON export from Python
- a server-side inference endpoint
