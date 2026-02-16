import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from lightgbm import LGBMClassifier
import joblib
from pathlib import Path

TRAINING_DATA = "dfdc/supervised_training_data.csv"
MODEL_OUTPUT = "dfdc/deepfake_shield_model.pkl"

def main():
    print("Training DeepFake Shield Supervised Model...")
    
    # Check if training data exists
    if not Path(TRAINING_DATA).exists():
        print(f"❌ Error: Training data not found: {TRAINING_DATA}")
        print("Please run build_supervised_dataset.py first.")
        return
    
    # Load data
    df = pd.read_csv(TRAINING_DATA)
    print(f"  Loaded {len(df)} training samples")
    
    # Separate features and labels
    X = df.drop(columns=["label"])
    y = df["label"]
    
    print(f"  Features: {X.shape[1]}")
    print(f"  Class distribution:")
    print(f"    REAL (0): {(y == 0).sum()} ({(y == 0).sum()/len(y)*100:.1f}%)")
    print(f"    FAKE (1): {(y == 1).sum()} ({(y == 1).sum()/len(y)*100:.1f}%)")
    
    # Model configuration
    model = LGBMClassifier(
        n_estimators=50,
        learning_rate=0.1,
        max_depth=3,
        num_leaves=7,
        min_child_samples=10,
        class_weight='balanced',
        random_state=42,
        verbose=-1
    )
    
    # Cross-validation
    print("\n  Performing 5-fold cross-validation...")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    auc_scores = []
    fold = 1
    
    for train_idx, val_idx in skf.split(X, y):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
        
        model.fit(X_train, y_train)
        y_pred_proba = model.predict_proba(X_val)[:, 1]
        auc = roc_auc_score(y_val, y_pred_proba)
        auc_scores.append(auc)
        
        print(f"    Fold {fold}: ROC-AUC = {auc:.3f}")
        fold += 1
    
    print(f"\n  Mean ROC-AUC: {np.mean(auc_scores):.3f} ± {np.std(auc_scores):.3f}")
    
    # Train final model on all data
    print("\n  Training final model on full dataset...")
    model.fit(X, y)
    
    # Feature importance
    print("\n  Top 10 Most Important Features:")
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    for idx, row in feature_importance.head(10).iterrows():
        print(f"    {row['feature']}: {row['importance']:.1f}")
    
    # Save model
    joblib.dump(model, MODEL_OUTPUT)
    print(f"\n✓ Model saved to {MODEL_OUTPUT}")
    print(f"  Model ready for deployment!")

if __name__ == "__main__":
    main()
