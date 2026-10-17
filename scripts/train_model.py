"""
SpaceY Intelligence - Model Training & Evaluation Runner Script
Trains all 7 candidate models, compares metrics, and persists the selected best pipeline.
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
import sklearn

# Add src to sys.path
src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from spacey.data.loader import load_and_prepare_benchmark_data
from spacey.models.trainer import train_and_compare_models


def main():
    print("=" * 60)
    print("🧠 SPACEY INTELLIGENCE — MODEL TRAINING & BENCHMARKING")
    print("=" * 60)
    in_venv = (sys.prefix != sys.base_prefix)
    print(f"Active Interpreter:   {sys.executable}")
    print(f"Python Version:       {sys.version.split()[0]}")
    print(f"Scikit-Learn Version: {sklearn.__version__}")
    print(f"Virtual Env Active:   {'Yes (.venv)' if in_venv else 'NO (Global Python - Not Recommended)'}")
    print("=" * 60)

    # Load validated benchmark dataset
    df, report = load_and_prepare_benchmark_data()
    print(f"Loaded training dataset: {len(df)} samples, {len(df.columns)} columns")
    print(f"Target distribution: {report.target_distribution}")

    # Train and compare 7 models
    metadata, comp_df, pipeline = train_and_compare_models(df)

    print("\n" + "=" * 60)
    print("🏆 MODEL COMPARISON LEADERBOARD (Holdout Evaluation)")
    print("=" * 60)
    print(comp_df.to_string(index=False))

    print("\n" + "=" * 60)
    print(f"🥇 WINNING MODEL: {metadata['model_name']}")
    print("=" * 60)
    win_metrics = metadata["evaluation_metrics"]
    print(f"Holdout Accuracy:   {win_metrics['accuracy']:.4f}")
    print(f"Holdout F1-Score:   {win_metrics['f1_score']:.4f}")
    print(f"Holdout ROC-AUC:    {win_metrics['roc_auc']:.4f}")
    print(f"Holdout PR-AUC:     {win_metrics['pr_auc']:.4f}")
    print(f"Brier Score:        {win_metrics['brier_score']:.4f}")
    print(f"Inference Latency:  {win_metrics['inference_latency_ms']:.2f} ms")
    print(f"Confusion Matrix:   TN={win_metrics['confusion_matrix']['tn']}, FP={win_metrics['confusion_matrix']['fp']}, FN={win_metrics['confusion_matrix']['fn']}, TP={win_metrics['confusion_matrix']['tp']}")

    print("\nTop Feature Attributions (Permutation Importance):")
    for item in metadata["top_features_importance"][:5]:
        print(f"  - {item['Feature']}: {item['Importance_Mean']:.4f} (±{item['Importance_Std']:.4f})")

    print("\n✅ Training and registry persistence completed successfully!")


if __name__ == "__main__":
    main()
