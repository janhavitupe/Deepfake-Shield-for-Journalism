# 🛡️ DeepFake Shield - Usage Guide

## Quick Start

The DeepFake Shield dashboard is now running and ready to classify videos!

### Access the Dashboard

Open your browser and navigate to:
- **Local URL**: http://localhost:8502
- **Network URL**: http://10.228.169.141:8502

## Dashboard Features

### 1. 🎬 Video Classifier Page

This is the main feature where you can upload videos for deepfake detection.

#### How to Use:

1. **Navigate** to the "Video Classifier" page (default page)
2. **Upload** a video file (MP4, AVI, or MOV format)
3. **Wait** for the analysis to complete (typically 10-30 seconds)
4. **Review** the results:
   - Classification: FAKE or REAL
   - Probability scores
   - Confidence gauges
   - Risk breakdown by category
   - Detailed feature analysis

#### Understanding Results:

**Classification Result:**
- **FAKE DETECTED**: Model predicts the video is manipulated
- **LIKELY REAL**: Model predicts the video is authentic

**Probability Scores:**
- Values closer to 100% indicate higher confidence
- Values near 50% indicate uncertainty

**Risk Categories (0-1 scale):**
- **Spatial Risk**: Image quality and sharpness anomalies
- **Temporal Risk**: Motion consistency issues
- **Color Risk**: Color channel inconsistencies
- **Face Risk**: Face detection and tracking anomalies

**Risk Levels:**
- **< 0.45**: Low risk
- **0.45-0.60**: Moderate risk
- **0.60-0.75**: High risk
- **> 0.75**: Critical risk

### 2. 📊 Analytics Dashboard Page

View comprehensive analytics from previously analyzed videos.

#### Features:
- **Filters**: Filter by risk level and suspicion index range
- **Key Metrics**: Total videos, high-risk count, average suspicion
- **Visualizations**:
  - Risk level distribution (pie chart)
  - Suspicion index histogram
  - Risk category breakdown
  - Video details table

#### How to Use:
1. Navigate to "Analytics Dashboard" page
2. Use sidebar filters to focus on specific videos
3. Explore different tabs:
   - **Overview**: High-level statistics
   - **Risk Analysis**: Detailed risk breakdowns
   - **Video Details**: Searchable video table

### 3. ℹ️ About Page

Learn about the DeepFake Shield system, detection methods, and limitations.

## Model Performance

- **Mean ROC-AUC**: 0.558 ± 0.091
- **Training Data**: 400 videos (DFDC dataset)
- **Class Distribution**: 19% Real, 81% Fake
- **Features**: 22 dimensions
- **Algorithm**: LightGBM with class balancing

### Top Important Features:
1. Inter-channel correlation (27.0)
2. Face Risk (21.0)
3. Face flow mean (20.0)
4. Temporal Risk (19.0)
5. Temporal diff mean (15.0)

## Tips for Best Results

1. **Video Quality**: Upload clear, well-lit videos
2. **Face Visibility**: Videos with visible faces work better
3. **Video Length**: Longer videos (>5 seconds) provide more reliable results
4. **Format**: MP4 format is recommended
5. **Resolution**: Higher resolution videos provide better feature extraction

## Limitations

⚠️ **Important Considerations:**

1. **Training Data**: Model trained on limited dataset (400 samples)
2. **Generalization**: May not detect all types of deepfakes
3. **Class Imbalance**: Training data was 81% fake, 19% real
4. **False Positives**: Some real videos may be flagged as fake
5. **False Negatives**: Some sophisticated deepfakes may be missed

## Technical Details

### Feature Extraction Process:

1. **Frame Sampling**: Analyzes 16 evenly-spaced frames per video
2. **Spatial Analysis**: Sharpness, FFT high-frequency energy
3. **Temporal Analysis**: Frame differences, optical flow
4. **Face Analysis**: Detection rate, area variance, motion tracking
5. **Color Analysis**: Channel correlations, standard deviations

### Risk Scoring:

- Each feature is compared to baseline statistics
- Z-scores are computed and normalized to 0-1 scale
- Risk categories are weighted combinations of related features
- Suspicion Index is the overall weighted risk score

### Classification:

- LightGBM model trained on 22 features
- 5-fold stratified cross-validation
- Class-balanced training to handle imbalance
- Outputs probability scores for Real vs Fake

## Troubleshooting

### Video Upload Issues:

**Problem**: "Failed to extract features from video"
- **Solution**: Try a different video format or ensure the video is not corrupted

**Problem**: Video takes too long to process
- **Solution**: Use shorter videos or lower resolution

### Dashboard Issues:

**Problem**: Dashboard not loading
- **Solution**: Ensure the dashboard is running at http://localhost:8502

**Problem**: Model not found error
- **Solution**: Run `python dfdc/train_supervised_model.py` to train the model

### Feature Extraction Issues:

**Problem**: Low confidence scores
- **Solution**: This is normal for videos with ambiguous features

**Problem**: All videos classified as fake
- **Solution**: Model has class imbalance; consider retraining with more real samples

## Command Reference

### Start Dashboard:
```bash
streamlit run dashboard.py
```

### Train Model:
```bash
python dfdc/train_supervised_model.py
```

### Extract Features:
```bash
python dfdc/extract_dfdc_features_v3.py
```

### Run Reliability Engine:
```bash
python dfdc/reliability_engine.py
```

### Build Training Dataset:
```bash
python dfdc/build_supervised_dataset.py
```

### Test Classification:
```bash
python test_video_classification.py
```

## Support

For issues or questions:
1. Check the error messages in the dashboard
2. Review the console output where the dashboard is running
3. Verify all dependencies are installed: `pip install -r requirements.txt`
4. Ensure video files are in supported formats

## Future Improvements

Potential enhancements:
- Deep learning-based feature extraction (CNN/RNN)
- Ensemble methods combining multiple models
- Real-time video stream processing
- Batch processing for multiple videos
- Video preview/playback in results
- Export detailed reports as PDF
- API endpoint for programmatic access

---

**Built with ❤️ for digital media forensics**

Last Updated: February 16, 2026
