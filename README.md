# 🛡️ DeepFake Shield

A comprehensive deepfake detection system using multi-modal forensic analysis and machine learning.

## 📋 Project Overview

DeepFake Shield is an advanced video forensic analysis system that detects manipulated videos through:
- **Spatial Analysis**: Image quality and sharpness metrics
- **Temporal Analysis**: Motion consistency and optical flow
- **Frequency Analysis**: FFT-based artifact detection
- **Face Analysis**: Face detection and area variance
- **Color Analysis**: Channel correlations and statistics
- **Metadata Analysis**: Technical video properties

## 🏗️ Project Structure

```
DeepFake_Shield/
├── dfdc/
│   ├── features/              # Extracted feature datasets
│   │   ├── dfdc_features.csv
│   │   ├── dfdc_features_v2.csv
│   │   └── dfdc_features_v3.csv
│   ├── metadata/              # Video metadata and labels
│   │   └── metadata.json
│   ├── raw_tmp/               # Temporary video storage
│   ├── reliability_engine.py  # Forensic analysis engine
│   ├── build_supervised_dataset.py  # Dataset builder
│   └── deepfake_shield_report.csv   # Analysis results
├── models/                    # Trained models
├── dashboard.py               # Interactive Streamlit dashboard
└── README.md
```

## 🚀 Quick Start

### Prerequisites

```bash
pip install pandas numpy opencv-python scikit-learn lightgbm streamlit plotly scipy
```

### Running the Pipeline

1. **Extract Features** (v3 includes optical flow):
```bash
python dfdc/extract_dfdc_features_v3.py
```

2. **Run Reliability Engine**:
```bash
python dfdc/reliability_engine.py
```

3. **Build Supervised Dataset**:
```bash
python dfdc/build_supervised_dataset.py
```

4. **Train Model**:
```bash
python dfdc/train_supervised_model.py
```

5. **Launch Dashboard**:
```bash
streamlit run dashboard.py
```

## 📊 Dashboard Features

The interactive dashboard provides:

### 📈 Overview Tab
- Risk level distribution (pie chart)
- Relative risk band distribution
- Suspicion index histogram
- Key metrics summary

### 🎯 Risk Analysis Tab
- Risk categories heatmap
- Average risk by category
- Risk category correlations
- Suspicion vs Confidence scatter plot

### 🔍 Video Details Tab
- Searchable video table
- Sortable by multiple criteria
- Detailed individual video analysis
- Risk breakdown visualization

### 📊 Statistics Tab
- Comprehensive statistical summary
- Risk category box plots
- Data export functionality

## 🔬 Feature Extraction Versions

### V1 - Basic Features (4 features)
- Sharpness (mean, variance)
- Temporal differences (mean, variance)

### V2 - Enhanced Features (10 features)
- All V1 features
- FFT high-frequency energy
- Face detection metrics
- Color channel analysis

### V3 - Advanced Features (12 features)
- All V2 features
- Optical flow analysis (face motion)
- Enhanced face tracking

## 📈 Reliability Engine

The reliability engine computes:

1. **Risk Scores** (0-1 scale):
   - Spatial Risk
   - Temporal Risk
   - Color Risk
   - Face Risk
   - Metadata Risk

2. **Suspicion Index**: Weighted combination of all risk scores

3. **Confidence Score**: Based on number of elevated risk categories

4. **Risk Classification**:
   - **Absolute**: Low, Moderate, High, Critical
   - **Relative**: Percentile-based ranking

## 🎯 Model Performance

Current supervised model:
- **Mean ROC-AUC**: 0.543
- **Features**: 22 (12 raw + 5 risk scores + 3 derived + 2 meta)
- **Algorithm**: LightGBM with class balancing

### Top Important Features:
1. Inter-channel correlation (25.0)
2. Temporal Risk (19.0)
3. Face flow mean (18.0)
4. Channel std ratio (17.0)
5. HF energy mean (15.0)

## 📊 Dataset Information

- **Total Videos**: 400
- **Class Distribution**: 
  - REAL: 77 (19.25%)
  - FAKE: 323 (80.75%)
- **Features**: 22 dimensions
- **Validation**: 5-fold stratified cross-validation

## 🔧 Configuration

Key parameters in scripts:

### Feature Extraction
```python
MAX_VIDEOS = 400
FRAMES_PER_VIDEO = 16
HF_CUTOFF = 0.25  # High-frequency cutoff ratio
```

### Model Training
```python
n_estimators = 50
learning_rate = 0.1
max_depth = 3
num_leaves = 7
```

## 📝 Output Files

1. **dfdc_features_v3.csv**: Raw extracted features
2. **deepfake_shield_report.csv**: Forensic analysis results
3. **supervised_training_data.csv**: Combined features + risk scores
4. **deepfake_shield_model.pkl**: Trained classification model

## 🎨 Dashboard Usage

### Filters
- **Risk Level**: Filter by Low/Moderate/High/Critical
- **Suspicion Range**: Slider to focus on specific suspicion levels

### Metrics
- Total videos analyzed
- High-risk count and percentage
- Average suspicion index
- Top 5% anomalous videos
- Average confidence score

### Visualizations
- Interactive plots with Plotly
- Hover for detailed information
- Zoom, pan, and export capabilities

## 🔍 Interpreting Results

### Suspicion Index
- **< 0.45**: Low risk
- **0.45-0.60**: Moderate risk
- **0.60-0.75**: High risk
- **> 0.75**: Critical risk

### Confidence Score
- Based on number of risk categories > 0.60
- Higher confidence = more consistent anomalies

### Primary Risk Drivers
- Top 2 risk categories for each video
- Helps identify specific manipulation types

## 🚧 Limitations

1. **Small Dataset**: 400 samples limits model performance
2. **Class Imbalance**: 80% fake, 20% real
3. **Feature Engineering**: Hand-crafted features may miss subtle artifacts
4. **Generalization**: Trained on DFDC dataset only

## 🔮 Future Improvements

1. **Deep Learning**: CNN/RNN-based feature extraction
2. **Ensemble Methods**: Combine multiple models
3. **Active Learning**: Iterative model improvement
4. **Real-time Processing**: Optimize for speed
5. **Multi-dataset Training**: Improve generalization

## 📄 License

This project is for educational and research purposes.

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional feature extraction methods
- Model optimization
- Dashboard enhancements
- Documentation improvements

## 📧 Contact

For questions or issues, please open a GitHub issue.

---

**Built with ❤️ for digital media forensics**
