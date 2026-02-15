"""
SilentShip CTF Challenge - Starter Template
Fill in the TODOs to build your solution!
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
# TODO: Import your chosen anomaly detection algorithm
# from sklearn.ensemble import IsolationForest
# from sklearn.svm import OneClassSVM
# from sklearn.neighbors import LocalOutlierFactor

def create_features(df):
    """
    Feature engineering - create useful features from raw data
    
    TODO: Add feature engineering here!
    Think about:
    - Relationships between columns (cost vs weight, time vs distance)
    - Derived metrics (cost per kg, time per distance unit)
    - Statistical deviations from expected values
    """
    df = df.copy()
    
    # Example: Add your features here
    # df['cost_per_kg'] = df['cost'] / df['weight']
    # df['new_feature'] = ...
    
    return df

def train_model(train_df):
    """
    Train your anomaly detection model
    
    TODO: Implement your model training
    1. Feature engineering
    2. Select features to use
    3. Scale/normalize data
    4. Train the model
    """
    
    # Example structure:
    # train_features = create_features(train_df)
    # feature_cols = ['weight', 'delivery_time', 'cost', ...]
    # X_train = train_features[feature_cols]
    # 
    # scaler = StandardScaler()
    # X_train_scaled = scaler.fit_transform(X_train)
    # 
    # model = YourModel(contamination=0.08)
    # model.fit(X_train_scaled)
    # 
    # return model, scaler, feature_cols
    
    pass  # Replace with your code

def predict_anomalies(model, scaler, test_df, feature_cols):
    """
    Predict anomalies on test set
    
    TODO: Implement prediction
    1. Apply same feature engineering to test data
    2. Scale using the same scaler
    3. Predict anomalies
    4. Convert predictions to 0/1 format
    """
    
    # Example structure:
    # test_features = create_features(test_df)
    # X_test = test_features[feature_cols]
    # X_test_scaled = scaler.transform(X_test)
    # 
    # predictions = model.predict(X_test_scaled)
    # 
    # # Convert to 0/1 (depends on your model's output)
    # # For Isolation Forest: -1 -> 1, 1 -> 0
    # predictions = np.where(predictions == -1, 1, 0)
    # 
    # return predictions
    
    pass  # Replace with your code

def main():
    """
    Main function - orchestrates the solution
    """
    print("="*60)
    print("🔍 SILENTSHIP - YOUR SOLUTION")
    print("="*60)
    
    # Load data
    print("\n📂 Loading datasets...")
    train_df = pd.read_csv('train.csv')
    test_df = pd.read_csv('test.csv')
    
    print(f"   Train samples: {len(train_df)}")
    print(f"   Test samples: {len(test_df)}")
    
    # TODO: Explore the data
    # print("\n📊 Dataset overview:")
    # print(train_df.describe())
    # print(train_df.head())
    
    # TODO: Train your model
    print("\n🤖 Training model...")
    # model, scaler, feature_cols = train_model(train_df)
    # print("   ✅ Model trained")
    
    # TODO: Make predictions
    print("\n🎯 Predicting anomalies...")
    # predictions = predict_anomalies(model, scaler, test_df, feature_cols)
    # print(f"   Detected {predictions.sum()} anomalies")
    
    # TODO: Create submission file
    # submission = pd.DataFrame({
    #     'id': range(len(predictions)),
    #     'prediction': predictions
    # })
    # submission.to_csv('predictions.csv', index=False)
    # print("\n💾 Saved to predictions.csv")
    
    print("\n" + "="*60)
    print("✅ Now run: python submit.py predictions.csv")
    print("="*60)

if __name__ == "__main__":
    main()

"""
💡 HINTS:

1. Feature Engineering is KEY!
   - Cost per kg: cost / weight
   - Time efficiency: delivery_time / distance
   - Deviation from expected patterns

2. Try different algorithms:
   - IsolationForest (good for anomalies)
   - One-Class SVM (works well with proper scaling)
   - Local Outlier Factor (good for density-based detection)

3. Contamination parameter:
   - Set to ~0.08 (8% anomaly rate)
   - Experiment with values between 0.05-0.10

4. Scaling matters!
   - Always use StandardScaler or MinMaxScaler
   - Fit on training data, transform both train and test

5. Don't trust bot_score alone!
   - It's part of the old unreliable system
   - Use it as a feature, but not the only one

6. Check your predictions:
   - Should be roughly 8% anomalies (not 50%, not 0.1%)
   - Values must be exactly 0 or 1
   - File must have 'id' and 'prediction' columns
"""
