import pandas as pd
import numpy as np
from pathlib import Path

FEATURE_CSV = "dfdc/features/dfdc_features_v3.csv"
FORENSIC_REPORT = "dfdc/deepfake_shield_report.csv"
OUTPUT_CSV = "dfdc/supervised_training_data.csv"

def main():
    print("Building supervised training dataset...")
    
    # Check if files exist
    if not Path(FEATURE_CSV).exists():
        print(f"❌ Error: Feature file not found: {FEATURE_CSV}")
        return
    
    if not Path(FORENSIC_REPORT).exists():
        print(f"❌ Error: Forensic report not found: {FORENSIC_REPORT}")
        print("Please run reliability_engine.py first to generate the report.")
        return
    
    features_df = pd.read_csv(FEATURE_CSV)
    forensic_df = pd.read_csv(FORENSIC_REPORT)
    
    print(f"  Loaded {len(features_df)} feature records")
    print(f"  Loaded {len(forensic_df)} forensic records")

    # Merge on video
    merged = pd.merge(features_df, forensic_df, on="video", how="inner")
    
    print(f"  Merged {len(merged)} records")

    # Select training columns
    training_columns = [
        # Original features
        "sharpness_mean",
        "sharpness_var",
        "temporal_diff_mean",
        "temporal_diff_var",
        "hf_energy_mean",
        "hf_energy_var",
        "channel_std_ratio",
        "inter_channel_corr",
        "face_detect_rate",
        "face_area_var",
        "face_flow_mean",
        "face_flow_var",
        # Risk scores
        "Spatial Risk",
        "Temporal Risk",
        "Color Risk",
        "Face Risk",
        "Metadata Risk",
        "Suspicion Index",
        "Confidence",
        # Label
        "label"
    ]
    
    # Keep only columns that exist
    available_columns = [col for col in training_columns if col in merged.columns]
    train_df = merged[available_columns].copy()
    
    # Add derived features
    train_df["risk_variance"] = merged[["Spatial Risk", "Temporal Risk", "Color Risk", "Face Risk", "Metadata Risk"]].var(axis=1)
    train_df["risk_max"] = merged[["Spatial Risk", "Temporal Risk", "Color Risk", "Face Risk", "Metadata Risk"]].max(axis=1)
    train_df["risk_min"] = merged[["Spatial Risk", "Temporal Risk", "Color Risk", "Face Risk", "Metadata Risk"]].min(axis=1)

    train_df.to_csv(OUTPUT_CSV, index=False)
    
    print(f"\n✓ Supervised training dataset created: {OUTPUT_CSV}")
    print(f"  Total samples: {len(train_df)}")
    print(f"  Total features: {len(train_df.columns) - 1}")  # -1 for label
    print(f"  Class distribution:")
    print(f"    REAL (0): {(train_df['label'] == 0).sum()}")
    print(f"    FAKE (1): {(train_df['label'] == 1).sum()}")

if __name__ == "__main__":
    main()
