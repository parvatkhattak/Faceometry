# ML Experiments

This directory is reserved for post-V1 machine learning experimentation.

## Structure

```
ml/
├── notebooks/     # Jupyter notebooks for exploration
├── datasets/      # Training/evaluation data (gitignored)
├── experiments/   # Experiment configs and results
└── models/        # Trained model artifacts (gitignored)
```

## Important

- ML experiments should only begin after the deterministic mathematical scoring engine (V1) is stable and validated.
- Any ML model must be presented as experimental — never as an objective truth about beauty.
- Evaluate with: MAE, RMSE, Pearson correlation, Spearman correlation.
- Compare ML models against the deterministic baseline.
