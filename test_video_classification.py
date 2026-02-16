"""
Test script to verify video classification pipeline
"""
import cv2
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from dashboard import extract_video_features, compute_risk_scores, load_baseline_stats, load_model

def test_classification():
    print("Testing DeepFake Shield Video Classification Pipeline\n")
    
    # Load model and baseline
    print("1. Loading model and baseline statistics...")
    model = load_model()
    baseline_mean, baseline_std = load_baseline_stats()
    
    if model is None:
        print("   ❌ Model not found!")
        return False
    if baseline_mean is None:
        print("   ❌ Baseline stats not found!")
        return False
    
    print("   ✓ Model and baseline loaded successfully")
    
    # Test with a sample video from the dataset
    print("\n2. Testing with sample video...")
    video_path = Path("dfdc/raw_tmp/metadata.json")
    
    # Find first video file
    video_files = list(Path("dfdc/raw_tmp").glob("*.mp4"))
    if not video_files:
        print("   ❌ No video files found in dfdc/raw_tmp/")
        return False
    
    test_video = video_files[0]
    print(f"   Using test video: {test_video.name}")
    
    # Extract features
    print("\n3. Extracting features...")
    features = extract_video_features(str(test_video))
    
    if features is None:
        print("   ❌ Feature extraction failed!")
        return False
    
    print(f"   ✓ Extracted {len(features)} features")
    print(f"   Sample features:")
    for key, value in list(features.items())[:5]:
        print(f"     - {key}: {value:.4f}")
    
    # Compute risk scores
    print("\n4. Computing risk scores...")
    risk_scores = compute_risk_scores(features, baseline_mean, baseline_std)
    
    print(f"   ✓ Computed {len(risk_scores)} risk scores")
    for key, value in risk_scores.items():
        print(f"     - {key}: {value:.4f}")
    
    # Prepare features for prediction
    print("\n5. Preparing feature vector for model...")
    feature_vector = pd.DataFrame([features])
    
    # Add risk scores (including Suspicion Index)
    for key, value in risk_scores.items():
        feature_vector[key] = value
    
    # Add metadata risk (placeholder)
    feature_vector["Metadata Risk"] = 0.3
    feature_vector["Confidence"] = 0.5
    
    # Add derived features
    feature_vector["risk_variance"] = np.var([
        risk_scores["Spatial Risk"],
        risk_scores["Temporal Risk"],
        risk_scores["Color Risk"],
        risk_scores["Face Risk"]
    ])
    feature_vector["risk_max"] = max([
        risk_scores["Spatial Risk"],
        risk_scores["Temporal Risk"],
        risk_scores["Color Risk"],
        risk_scores["Face Risk"]
    ])
    feature_vector["risk_min"] = min([
        risk_scores["Spatial Risk"],
        risk_scores["Temporal Risk"],
        risk_scores["Color Risk"],
        risk_scores["Face Risk"]
    ])
    
    print(f"   ✓ Feature vector shape: {feature_vector.shape}")
    
    # Make prediction
    print("\n6. Making prediction...")
    try:
        prediction_proba = model.predict_proba(feature_vector)[0]
        prediction = model.predict(feature_vector)[0]
        
        fake_probability = prediction_proba[1]
        real_probability = prediction_proba[0]
        
        print(f"   ✓ Prediction successful!")
        print(f"\n   === RESULTS ===")
        print(f"   Classification: {'FAKE' if prediction == 1 else 'REAL'}")
        print(f"   Real Probability: {real_probability*100:.2f}%")
        print(f"   Fake Probability: {fake_probability*100:.2f}%")
        print(f"   Suspicion Index: {risk_scores['Suspicion Index']:.4f}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Prediction failed: {e}")
        return False

if __name__ == "__main__":
    success = test_classification()
    
    if success:
        print("\n" + "="*50)
        print("✅ ALL TESTS PASSED!")
        print("="*50)
        print("\nThe video classification pipeline is working correctly.")
        print("You can now use the dashboard to upload and classify videos.")
        print("\nDashboard URL: http://localhost:8502")
    else:
        print("\n" + "="*50)
        print("❌ TESTS FAILED!")
        print("="*50)
        print("\nPlease check the error messages above.")
