import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import (
    StratifiedKFold,
    train_test_split,
    RandomizedSearchCV,
    cross_val_score,
)
from sklearn.metrics import (
    roc_auc_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    balanced_accuracy_score,
    make_scorer,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from lightgbm import LGBMClassifier
from scipy.stats import randint as sp_randint, uniform as sp_uniform
import joblib

TRAINING_DATA = "dfdc/supervised_training_data.csv"
MODEL_OUTPUT = "dfdc/deepfake_shield_model.pkl"
TEST_SIZE = 0.20  # 80/20 split
RANDOM_STATE = 42
N_ITER_SEARCH = 40


def print_metrics(y_true, y_pred, y_proba, split_name=""):
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    auc = roc_auc_score(y_true, y_proba)
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0
    bal_acc = balanced_accuracy_score(y_true, y_pred)

    print(f"\n  {'='*55}")
    print(f"  {split_name} Results")
    print(f"  {'='*55}")
    print(f"  Accuracy:          {acc:.4f}  ({acc*100:.2f}%)")
    print(f"  Balanced Accuracy: {bal_acc:.4f}  ({bal_acc*100:.2f}%)")
    print(f"  Precision:         {prec:.4f}  ({prec*100:.2f}%)")
    print(f"  Recall:            {rec:.4f}  ({rec*100:.2f}%)")
    print(f"  F1-Score:          {f1:.4f}  ({f1*100:.2f}%)")
    print(f"  ROC-AUC:           {auc:.4f}  ({auc*100:.2f}%)")
    print(f"  Specificity:       {spec:.4f}  ({spec*100:.2f}%)")
    print(f"\n  Confusion Matrix:")
    print(f"                 Predicted")
    print(f"               REAL   FAKE")
    print(f"  Actual REAL   {tn:4d}   {fp:4d}")
    print(f"         FAKE   {fn:4d}   {tp:4d}")
    print(f"\n  TP={tp}, TN={tn}, FP={fp}, FN={fn}")
    print(f"  Correctly classified: {tp+tn}/{len(y_true)}")
    print(f"\n{classification_report(y_true, y_pred, target_names=['REAL','FAKE'], digits=4)}")

    return {
        'accuracy': acc,
        'balanced_accuracy': bal_acc,
        'precision': prec,
        'recall': rec,
        'f1': f1,
        'roc_auc': auc,
        'specificity': spec,
        'confusion_matrix': cm,
    }


def oversample_minority(X, y):
    minority = X[y == 0]
    minority_y = y[y == 0]
    majority = X[y == 1]
    sample_count = len(majority) - len(minority)

    if sample_count <= 0:
        return X.reset_index(drop=True), y.reset_index(drop=True)

    extra = minority.sample(n=sample_count, replace=True, random_state=RANDOM_STATE)
    extra_y = minority_y.sample(n=sample_count, replace=True, random_state=RANDOM_STATE)

    X_os = pd.concat([X, extra], axis=0).reset_index(drop=True)
    y_os = pd.concat([y, extra_y], axis=0).reset_index(drop=True)

    shuffled_idx = np.random.RandomState(RANDOM_STATE).permutation(len(X_os))
    return X_os.iloc[shuffled_idx].reset_index(drop=True), y_os.iloc[shuffled_idx].reset_index(drop=True)
def search_best_lgbm(X_train, y_train, cv):
    print("\n  Searching for best LightGBM hyperparameters on train set...")

    param_dist = {
        'n_estimators': sp_randint(100, 501),
        'learning_rate': sp_uniform(0.01, 0.29),
        'num_leaves': sp_randint(15, 128),
        'max_depth': sp_randint(3, 12),
        'min_child_samples': sp_randint(5, 60),
        'subsample': sp_uniform(0.6, 0.4),
        'colsample_bytree': sp_uniform(0.6, 0.4),
        'reg_alpha': sp_uniform(0.0, 5.0),
        'reg_lambda': sp_uniform(0.0, 5.0),
    }

    estimator = LGBMClassifier(
        class_weight='balanced',
        random_state=RANDOM_STATE,
        n_jobs=-1,
        verbose=-1,
    )

    search = RandomizedSearchCV(
        estimator=estimator,
        param_distributions=param_dist,
        n_iter=N_ITER_SEARCH,
        scoring=make_scorer(balanced_accuracy_score),
        cv=cv,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        verbose=1,
        refit=True,
    )

    search.fit(X_train, y_train)

    print(f"\n  Best LightGBM params: {search.best_params_}")
    print(f"  Best CV Balanced Accuracy: {search.best_score_:.4f}")
    return search.best_estimator_


def print_classifier_summary(name, model, X_train, y_train, cv):
    print(f"\n  Evaluating {name} with stratified CV...")
    scores = cross_val_score(model, X_train, y_train, cv=cv, scoring=make_scorer(balanced_accuracy_score), n_jobs=-1)
    print(f"    CV Balanced Accuracy: {np.mean(scores):.4f} ± {np.std(scores):.4f}")
    return np.mean(scores), np.std(scores)


def main():
    print("=" * 55)
    print("  DeepFake Shield — Tuned Train/Test Evaluation")
    print("=" * 55)

    if not Path(TRAINING_DATA).exists():
        print(f"❌ Training data not found: {TRAINING_DATA}")
        print("Please run build_supervised_dataset.py first.")
        return

    df = pd.read_csv(TRAINING_DATA)
    print(f"\n  Loaded {len(df)} total samples")

    X = df.drop(columns=["label"])
    y = df["label"]

    print(f"  Features: {X.shape[1]}")
    print(f"  Class distribution:")
    print(f"    REAL (0): {(y == 0).sum()} ({(y == 0).sum()/len(y)*100:.1f}%)")
    print(f"    FAKE (1): {(y == 1).sum()} ({(y == 1).sum()/len(y)*100:.1f}%)")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        stratify=y,
        random_state=RANDOM_STATE,
    )

    print(f"\n  Train set: {len(X_train)} samples "
          f"(REAL={(y_train == 0).sum()}, FAKE={(y_train == 1).sum()})")
    print(f"  Test set:  {len(X_test)} samples "
          f"(REAL={(y_test == 0).sum()}, FAKE={(y_test == 1).sum()})")

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

    X_train_os, y_train_os = oversample_minority(X_train, y_train)
    print(f"\n  Oversampled train set: {len(X_train_os)} samples "
          f"(REAL={(y_train_os == 0).sum()}, FAKE={(y_train_os == 1).sum()})")

    baseline_models = [
        (
            'LogisticRegression',
            Pipeline([
                ('scaler', StandardScaler()),
                ('clf', LogisticRegression(
                    solver='liblinear',
                    class_weight='balanced',
                    random_state=RANDOM_STATE,
                    max_iter=500,
                )),
            ]),
        ),
        (
            'RandomForest',
            RandomForestClassifier(
                n_estimators=200,
                class_weight='balanced',
                random_state=RANDOM_STATE,
                n_jobs=-1,
            ),
        ),
    ]

    best_baseline = None
    best_baseline_score = -1
    for name, model in baseline_models:
        mean_score, std_score = print_classifier_summary(name, model, X_train_os, y_train_os, skf)
        if mean_score > best_baseline_score:
            best_baseline_score = mean_score
            best_baseline = (name, model)

    tuned_model = search_best_lgbm(X_train_os, y_train_os, skf)
    tuned_model.fit(X_train_os, y_train_os)

    y_pred_test = tuned_model.predict(X_test)
    y_proba_test = tuned_model.predict_proba(X_test)[:, 1]
    metrics = print_metrics(y_test, y_pred_test, y_proba_test, split_name="HELD-OUT TEST SET (20%)")

    print(f"\n  Re-evaluating best baseline model: {best_baseline[0]}")
    best_baseline[1].fit(X_train_os, y_train_os)
    baseline_preds = best_baseline[1].predict(X_test)
    baseline_proba = best_baseline[1].predict_proba(X_test)[:, 1]
    _ = print_metrics(y_test, baseline_preds, baseline_proba, split_name=f"BASELINE {best_baseline[0]}")

    print("\n  Retraining tuned LightGBM on full dataset for deployment...")
    X_full_os, y_full_os = oversample_minority(X, y)
    final_model = search_best_lgbm(X_full_os, y_full_os, skf)
    final_model.fit(X_full_os, y_full_os)
    joblib.dump(final_model, MODEL_OUTPUT)

    print("\n" + "=" * 55)
    print("  SUMMARY")
    print("=" * 55)
    print(f"  Best baseline: {best_baseline[0]} with CV Balanced Accuracy {best_baseline_score:.4f}")
    print(f"  Held-out Test ROC-AUC (tuned LightGBM): {metrics['roc_auc']:.4f}")
    print(f"  Held-out Test Accuracy (tuned LightGBM): {metrics['accuracy']:.4f}")
    print(f"  Held-out Test Balanced Accuracy: {metrics['balanced_accuracy']:.4f}")
    print(f"\n  ✓ Final tuned model saved to {MODEL_OUTPUT}")
    print("=" * 55)


if __name__ == "__main__":
    main()
