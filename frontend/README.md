# Bridge Vulnerability Demo Frontend

A polished React + Tailwind CSS research/demo site for the bridge vulnerability project.

## Run locally

```bash
npm install
npm run dev
```

If Node is not globally installed on this machine, this workspace also has a local Node runtime at `../.node/bin/` that was used for validation.

## Build

```bash
npm run build
npm run preview
```

## Where to swap in real model logic

The mock prediction engine lives in:

- `src/lib/predictionEngine.js`

The dashboard inputs and sample bridge records live in:

- `src/data/sampleBridges.js`

The analytics/demo chart data lives in:

- `src/data/mockAnalytics.js`

When a final trained model is ready, replace the scoring logic in `runBridgePrediction` while keeping the UI contracts intact.
