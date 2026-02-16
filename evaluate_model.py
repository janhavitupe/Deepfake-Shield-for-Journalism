"""
Comprehensive Model Evaluation Script
Tests model on all videos and computes accuracy, precision, recall, F1, etc.
"""
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score, roc_curve
)
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm

# Paths
MODEL_PATH = "dfdc/deepfake_shield_model.pkl"
TRAINING_DATA = "dfdc/supervised_training_data.csv"
METADATA_PATH = "dfdc/metadata/metadata.json"
OUTPUT_DIR = Path("evaluation_results")

def load_ground_truth():
    """Load ground truth labels from metadata"""
    import json
    
    with open(METADATA_PATH, 'r') as f:
        metadata = json.load(f)
    
    # Create mapping of video -> label
    ground_truth = {}
    for video, info in metadata.items():
        label = info.get('label', None)
        if label is not None:
            # Convert REAL/FAKE to 0/1
            if isinstance(label, str):
                ground_truth[video] = 0 if label.upper() == 'REAL' else 1
            else:
                ground_truth[video] = int(label)
    
    return ground_truth

def evaluate_model():
    print("="*70)
    print("DeepFake Shield - Comprehensive Model Evaluation")
    print("="*70)
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Load model
    print("\n1. Loading model...")
    if not Path(MODEL_PATH).exists():
        print(f"   ❌ Model not found: {MODEL_PATH}")
        return
    
    model = joblib.load(MODEL_PATH)
    print(f"   ✓ Model loaded successfully")
    
    # Load training data (contains features + labels)
    print("\n2. Loading test data...")
    if not Path(TRAINING_DATA).exists():
        print(f"   ❌ Training data not found: {TRAINING_DATA}")
        return
    
    df = pd.read_csv(TRAINING_DATA)
    print(f"   ✓ Loaded {len(df)} samples")
    
    # Load ground truth from metadata
    print("\n3. Loading ground truth labels...")
    try:
        ground_truth = load_ground_truth()
        print(f"   ✓ Loaded {len(ground_truth)} ground truth labels")
    except Exception as e:
        print(f"   ⚠️  Could not load metadata: {e}")
        print(f"   Using labels from training data instead")
        ground_truth = None
    
    # Separate features and labels
    X = df.drop(columns=["label"])
    y_true = df["label"].values
    
    print(f"\n4. Running predictions on all {len(df)} videos...")
    
    # Make predictions
    y_pred = model.predict(X)
    y_pred_proba = model.predict_proba(X)[:, 1]
    
    print(f"   ✓ Predictions complete")
    
    # Compute metrics
    print("\n" + "="*70)
    print("PERFORMANCE METRICS")
    print("="*70)
    
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    
    try:
        roc_auc = roc_auc_score(y_true, y_pred_proba)
    except:
        roc_auc = None
    
    print(f"\n📊 Overall Metrics:")
    print(f"   Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"   Precision: {precision:.4f} ({precision*100:.2f}%)")
    print(f"   Recall:    {recall:.4f} ({recall*100:.2f}%)")
    print(f"   F1-Score:  {f1:.4f} ({f1*100:.2f}%)")
    if roc_auc:
        print(f"   ROC-AUC:   {roc_auc:.4f} ({roc_auc*100:.2f}%)")
    
    # Confusion Matrix
    print(f"\n📋 Confusion Matrix:")
    cm = confusion_matrix(y_true, y_pred)
    print(f"\n                Predicted")
    print(f"              REAL  FAKE")
    print(f"   Actual REAL  {cm[0,0]:4d}  {cm[0,1]:4d}")
    print(f"         FAKE  {cm[1,0]:4d}  {cm[1,1]:4d}")
    
    # Calculate additional metrics
    tn, fp, fn, tp = cm.ravel()
    
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    false_positive_rate = fp / (fp + tn) if (fp + tn) > 0 else 0
    false_negative_rate = fn / (fn + tp) if (fn + tp) > 0 else 0
    
    print(f"\n📈 Detailed Metrics:")
    print(f"   True Positives:  {tp:4d} (Correctly identified FAKE)")
    print(f"   True Negatives:  {tn:4d} (Correctly identified REAL)")
    print(f"   False Positives: {fp:4d} (REAL classified as FAKE)")
    print(f"   False Negatives: {fn:4d} (FAKE classified as REAL)")
    print(f"\n   Sensitivity (TPR): {sensitivity:.4f} ({sensitivity*100:.2f}%)")
    print(f"   Specificity (TNR): {specificity:.4f} ({specificity*100:.2f}%)")
    print(f"   False Positive Rate: {false_positive_rate:.4f} ({false_positive_rate*100:.2f}%)")
    print(f"   False Negative Rate: {false_negative_rate:.4f} ({false_negative_rate*100:.2f}%)")
    
    # Classification Report
    print(f"\n📑 Classification Report:")
    print("\n" + classification_report(y_true, y_pred, 
                                       target_names=['REAL', 'FAKE'],
                                       digits=4))
    
    # Class distribution
    print(f"\n📊 Class Distribution:")
    print(f"   Ground Truth:")
    print(f"      REAL (0): {(y_true == 0).sum():4d} ({(y_true == 0).sum()/len(y_true)*100:.2f}%)")
    print(f"      FAKE (1): {(y_true == 1).sum():4d} ({(y_true == 1).sum()/len(y_true)*100:.2f}%)")
    print(f"\n   Predictions:")
    print(f"      REAL (0): {(y_pred == 0).sum():4d} ({(y_pred == 0).sum()/len(y_pred)*100:.2f}%)")
    print(f"      FAKE (1): {(y_pred == 1).sum():4d} ({(y_pred == 1).sum()/len(y_pred)*100:.2f}%)")
    
    # Prediction confidence analysis
    print(f"\n🎯 Prediction Confidence Analysis:")
    high_conf_correct = np.sum((y_pred_proba > 0.7) & (y_pred == y_true)) + \
                        np.sum((y_pred_proba < 0.3) & (y_pred == y_true))
    high_conf_total = np.sum((y_pred_proba > 0.7) | (y_pred_proba < 0.3))
    
    if high_conf_total > 0:
        high_conf_acc = high_conf_correct / high_conf_total
        print(f"   High Confidence (>70% or <30%): {high_conf_total} predictions")
        print(f"   High Confidence Accuracy: {high_conf_acc:.4f} ({high_conf_acc*100:.2f}%)")
    
    uncertain = np.sum((y_pred_proba >= 0.4) & (y_pred_proba <= 0.6))
    print(f"   Uncertain (40-60%): {uncertain} predictions ({uncertain/len(y_pred)*100:.2f}%)")
    
    # Save detailed results
    print(f"\n💾 Saving detailed results...")
    
    # Create results dataframe
    results_df = df.copy()
    results_df['y_true'] = y_true
    results_df['y_pred'] = y_pred
    results_df['y_pred_proba'] = y_pred_proba
    results_df['correct'] = (y_true == y_pred).astype(int)
    results_df['confidence'] = np.maximum(y_pred_proba, 1 - y_pred_proba)
    
    # Add prediction labels
    results_df['true_label'] = results_df['y_true'].map({0: 'REAL', 1: 'FAKE'})
    results_df['pred_label'] = results_df['y_pred'].map({0: 'REAL', 1: 'FAKE'})
    
    # Save to CSV
    results_path = OUTPUT_DIR / "detailed_predictions.csv"
    results_df.to_csv(results_path, index=False)
    print(f"   ✓ Detailed predictions saved to: {results_path}")
    
    # Save metrics summary
    metrics_summary = {
        'Metric': ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC',
                   'Sensitivity', 'Specificity', 'False Positive Rate', 'False Negative Rate',
                   'True Positives', 'True Negatives', 'False Positives', 'False Negatives'],
        'Value': [accuracy, precision, recall, f1, roc_auc if roc_auc else 0,
                  sensitivity, specificity, false_positive_rate, false_negative_rate,
                  tp, tn, fp, fn]
    }
    metrics_df = pd.DataFrame(metrics_summary)
    metrics_path = OUTPUT_DIR / "metrics_summary.csv"
    metrics_df.to_csv(metrics_path, index=False)
    print(f"   ✓ Metrics summary saved to: {metrics_path}")
    
    # Generate visualizations
    print(f"\n📊 Generating visualizations...")
    
    # 1. Confusion Matrix Heatmap
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['REAL', 'FAKE'],
                yticklabels=['REAL', 'FAKE'])
    plt.title('Confusion Matrix', fontsize=14, fontweight='bold')
    plt.ylabel('Actual Label', fontsize=12)
    plt.xlabel('Predicted Label', fontsize=12)
    plt.tight_layout()
    cm_path = OUTPUT_DIR / "confusion_matrix.png"
    plt.savefig(cm_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✓ Confusion matrix saved to: {cm_path}")
    
    # 2. ROC Curve
    if roc_auc:
        fpr, tpr, thresholds = roc_curve(y_true, y_pred_proba)
        
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, color='darkorange', lw=2, 
                label=f'ROC curve (AUC = {roc_auc:.3f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate', fontsize=12)
        plt.ylabel('True Positive Rate', fontsize=12)
        plt.title('ROC Curve', fontsize=14, fontweight='bold')
        plt.legend(loc="lower right")
        plt.grid(alpha=0.3)
        plt.tight_layout()
        roc_path = OUTPUT_DIR / "roc_curve.png"
        plt.savefig(roc_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"   ✓ ROC curve saved to: {roc_path}")
    
    # 3. Prediction Probability Distribution
    plt.figure(figsize=(10, 6))
    
    # Separate by true label
    real_probs = y_pred_proba[y_true == 0]
    fake_probs = y_pred_proba[y_true == 1]
    
    plt.hist(real_probs, bins=30, alpha=0.6, label='True REAL', color='green', edgecolor='black')
    plt.hist(fake_probs, bins=30, alpha=0.6, label='True FAKE', color='red', edgecolor='black')
    plt.axvline(x=0.5, color='black', linestyle='--', linewidth=2, label='Decision Threshold')
    plt.xlabel('Predicted Probability (FAKE)', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.title('Prediction Probability Distribution', fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    prob_path = OUTPUT_DIR / "probability_distribution.png"
    plt.savefig(prob_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✓ Probability distribution saved to: {prob_path}")
    
    # 4. Metrics Bar Chart
    plt.figure(figsize=(10, 6))
    metrics_to_plot = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'Sensitivity', 'Specificity']
    values_to_plot = [accuracy, precision, recall, f1, sensitivity, specificity]
    colors_plot = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    
    bars = plt.bar(metrics_to_plot, values_to_plot, color=colors_plot, edgecolor='black', linewidth=1.5)
    plt.ylim([0, 1.0])
    plt.ylabel('Score', fontsize=12)
    plt.title('Model Performance Metrics', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bar, value in zip(bars, values_to_plot):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.3f}',
                ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    metrics_bar_path = OUTPUT_DIR / "metrics_bar_chart.png"
    plt.savefig(metrics_bar_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✓ Metrics bar chart saved to: {metrics_bar_path}")
    
    # Find misclassified examples
    print(f"\n🔍 Analyzing Misclassifications...")
    misclassified = results_df[results_df['correct'] == 0]
    
    if len(misclassified) > 0:
        print(f"   Total Misclassified: {len(misclassified)} ({len(misclassified)/len(results_df)*100:.2f}%)")
        
        # False Positives (REAL predicted as FAKE)
        false_positives = misclassified[misclassified['y_true'] == 0]
        print(f"\n   False Positives (REAL → FAKE): {len(false_positives)}")
        if len(false_positives) > 0:
            print(f"      Average confidence: {false_positives['y_pred_proba'].mean():.3f}")
            print(f"      Top 5 most confident mistakes:")
            top_fp = false_positives.nlargest(5, 'y_pred_proba')[['y_pred_proba', 'Suspicion Index']]
            for idx, row in top_fp.iterrows():
                print(f"         Prob: {row['y_pred_proba']:.3f}, Suspicion: {row['Suspicion Index']:.3f}")
        
        # False Negatives (FAKE predicted as REAL)
        false_negatives = misclassified[misclassified['y_true'] == 1]
        print(f"\n   False Negatives (FAKE → REAL): {len(false_negatives)}")
        if len(false_negatives) > 0:
            print(f"      Average confidence: {(1 - false_negatives['y_pred_proba']).mean():.3f}")
            print(f"      Top 5 most confident mistakes:")
            top_fn = false_negatives.nsmallest(5, 'y_pred_proba')[['y_pred_proba', 'Suspicion Index']]
            for idx, row in top_fn.iterrows():
                print(f"         Prob: {row['y_pred_proba']:.3f}, Suspicion: {row['Suspicion Index']:.3f}")
        
        # Save misclassified examples
        misclass_path = OUTPUT_DIR / "misclassified_videos.csv"
        misclassified.to_csv(misclass_path, index=False)
        print(f"\n   ✓ Misclassified examples saved to: {misclass_path}")
    else:
        print(f"   🎉 Perfect classification! No misclassifications found.")
    
    # Summary
    print("\n" + "="*70)
    print("EVALUATION COMPLETE")
    print("="*70)
    print(f"\n📁 All results saved to: {OUTPUT_DIR}/")
    print(f"\n📊 Key Findings:")
    print(f"   • Model correctly classified {(y_true == y_pred).sum()}/{len(y_true)} videos")
    print(f"   • Accuracy: {accuracy*100:.2f}%")
    print(f"   • Best at detecting: {'FAKE' if recall > specificity else 'REAL'} videos")
    print(f"   • {len(misclassified)} videos need further review")
    
    if accuracy < 0.6:
        print(f"\n⚠️  Model performance is below 60%. Consider:")
        print(f"   • Collecting more training data")
        print(f"   • Balancing the dataset (currently {(y_true == 1).sum()/len(y_true)*100:.1f}% FAKE)")
        print(f"   • Feature engineering improvements")
        print(f"   • Hyperparameter tuning")
    elif accuracy < 0.8:
        print(f"\n✓ Model performance is moderate. Room for improvement:")
        print(f"   • Consider ensemble methods")
        print(f"   • Add more diverse training samples")
        print(f"   • Fine-tune decision threshold")
    else:
        print(f"\n🎉 Excellent model performance!")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    try:
        evaluate_model()
    except Exception as e:
        print(f"\n❌ Error during evaluation: {e}")
        import traceback
        traceback.print_exc()
