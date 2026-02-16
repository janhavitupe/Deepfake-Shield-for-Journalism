import cv2
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.special import expit

# ===== PATHS =====
FEATURE_CSV = "dfdc/features/dfdc_features_v3.csv"
VIDEO_ROOT = "dfdc/raw_tmp"
# =================

# -------- Utility --------
def safe_z(x, mean, std):
    if std == 0 or np.isnan(std):
        return 0
    return abs(x - mean) / std

def normalize_score(z):
    """Convert z-score to 0-1 risk score using sigmoid"""
    if np.isnan(z) or np.isinf(z):
        return 0.0
    return float(expit(z - 1))

def absolute_risk_band(score):
    if score < 0.45:
        return "Low"
    elif score < 0.60:
        return "Moderate"
    elif score < 0.75:
        return "High"
    else:
        return "Critical"

def percentile_band(percentile):
    if percentile >= 95:
        return "Top 5% Most Anomalous"
    elif percentile >= 90:
        return "Top 10%"
    elif percentile >= 75:
        return "Top 25%"
    elif percentile >= 50:
        return "Above Median"
    else:
        return "Below Median"

# -------- Metadata Extraction --------
def extract_metadata(video_path):
    cap = cv2.VideoCapture(str(video_path))

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    cap.release()

    duration = frame_count / fps if fps > 0 else 0
    file_size = Path(video_path).stat().st_size
    bitrate = file_size / duration if duration > 0 else 0

    return {
        "fps": fps,
        "frame_count": frame_count,
        "width": width,
        "height": height,
        "duration": duration,
        "bitrate": bitrate
    }

# -------- Main Engine --------
def main():
    df = pd.read_csv(FEATURE_CSV)

    metadata_rows = []

    # Extract metadata
    print("Extracting video metadata...")
    for idx, row in df.iterrows():
        video_name = row["video"]
        video_path = Path(VIDEO_ROOT) / video_name
        
        if not video_path.exists():
            continue

        try:
            meta = extract_metadata(video_path)
            meta["video"] = video_name
            metadata_rows.append(meta)
            
            if (idx + 1) % 50 == 0:
                print(f"  Processed {idx + 1}/{len(df)} videos...")
        except Exception as e:
            print(f"  Warning: Failed to extract metadata from {video_name}: {e}")
            continue
    
    print(f"✓ Successfully extracted metadata from {len(metadata_rows)} videos\n")

    meta_df = pd.DataFrame(metadata_rows)

    if meta_df.empty:
        print("\n⚠️  No metadata extracted.")
        print("Please ensure video files exist in:", VIDEO_ROOT)
        return

    # Baselines
    feature_mean = df.mean(numeric_only=True)
    feature_std = df.std(numeric_only=True)
    meta_mean = meta_df.mean(numeric_only=True)
    meta_std = meta_df.std(numeric_only=True)

    reports = []

    # Store suspicion scores first (for percentile computation)
    suspicion_values = []

    temp_storage = []

    for _, row in df.iterrows():
        video_name = row["video"]

        if video_name not in meta_df["video"].values:
            continue

        meta_row = meta_df[meta_df["video"] == video_name].iloc[0]

        scores = {}

        # Feature anomaly scores
        for key in feature_mean.index:
            if key in row:
                z = safe_z(row[key], feature_mean[key], feature_std[key])
                scores[key] = normalize_score(z)

        # Metadata anomaly scores
        for key in meta_mean.index:
            z = safe_z(meta_row[key], meta_mean[key], meta_std[key])
            scores[key] = normalize_score(z)

        # ---- Categories ----
        spatial = np.mean([
            scores.get("sharpness_mean", 0),
            scores.get("hf_energy_mean", 0),
            scores.get("hf_energy_var", 0),
        ])

        temporal = np.mean([
            scores.get("temporal_diff_var", 0),
            scores.get("face_flow_var", 0),
        ])

        color = np.mean([
            scores.get("inter_channel_corr", 0),
            scores.get("channel_std_ratio", 0),
        ])

        face = np.mean([
            scores.get("face_detect_rate", 0),
            scores.get("face_area_var", 0),
        ])

        metadata_score = np.mean([
            scores.get("fps", 0),
            scores.get("duration", 0),
            scores.get("bitrate", 0),
            scores.get("width", 0),
            scores.get("height", 0),
        ])

        suspicion = (
            0.25 * spatial +
            0.25 * temporal +
            0.15 * color +
            0.15 * face +
            0.20 * metadata_score
        )

        category_scores = np.array([spatial, temporal, color, face, metadata_score])
        elevated = np.sum(category_scores > 0.60)
        confidence = min(1.0, elevated / 3)

        category_dict = {
            "Spatial": spatial,
            "Temporal": temporal,
            "Color": color,
            "Face": face,
            "Metadata": metadata_score
        }

        sorted_drivers = sorted(category_dict.items(), key=lambda x: x[1], reverse=True)
        top_drivers = ", ".join([f"{k} ({round(v,3)})" for k,v in sorted_drivers[:2]])

        suspicion_values.append(suspicion)

        temp_storage.append({
            "video": video_name,
            "Spatial Risk": round(spatial, 3),
            "Temporal Risk": round(temporal, 3),
            "Color Risk": round(color, 3),
            "Face Risk": round(face, 3),
            "Metadata Risk": round(metadata_score, 3),
            "Suspicion Index": suspicion,
            "Absolute Risk Level": absolute_risk_band(suspicion),
            "Confidence": round(confidence, 3),
            "Primary Risk Drivers": top_drivers
        })

    # Compute percentiles
    suspicion_array = np.array(suspicion_values)
    percentiles = (suspicion_array.argsort().argsort() + 1) / len(suspicion_array) * 100

    for i, item in enumerate(temp_storage):
        item["Suspicion Index"] = round(item["Suspicion Index"], 3)
        item["Percentile Rank"] = round(percentiles[i], 2)
        item["Relative Risk Band"] = percentile_band(percentiles[i])
        reports.append(item)

    report_df = pd.DataFrame(reports)
    report_df = report_df.sort_values("Percentile Rank", ascending=False)

    print("\n=== DeepFake Shield Forensic Reliability Report ===\n")
    print(report_df[["video", "Suspicion Index", "Percentile Rank", "Relative Risk Band", "Confidence", "Primary Risk Drivers"]].head(15))

    # Summary statistics
    print("\n=== Summary Statistics ===")
    print(f"Total videos analyzed: {len(report_df)}")
    print(f"\nAbsolute Risk Distribution:")
    print(report_df["Absolute Risk Level"].value_counts().to_string())
    print(f"\nRelative Risk Distribution:")
    print(report_df["Relative Risk Band"].value_counts().to_string())
    print(f"\nSuspicion Index Statistics:")
    print(f"  Mean:   {report_df['Suspicion Index'].mean():.3f}")
    print(f"  Median: {report_df['Suspicion Index'].median():.3f}")
    print(f"  Max:    {report_df['Suspicion Index'].max():.3f}")
    print(f"  Min:    {report_df['Suspicion Index'].min():.3f}")

    report_df.to_csv("dfdc/deepfake_shield_report.csv", index=False)
    print("\n✓ Full report saved to dfdc/deepfake_shield_report.csv")


if __name__ == "__main__":
    main()
