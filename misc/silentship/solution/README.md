# SilentShip - Solution Writeup

## Challenge Overview

SilentShip is an anomaly detection challenge where participants must build a machine learning model to identify suspicious shipments in a logistics dataset.

**Goal:** Achieve F1 Score ≥ 40% to get the flag  
**Flag:** `shellmates{s!l3ntsh!p-4n0m4ly-d3t3ct3d}`

---

## Dataset Analysis

### Training Data Structure

The `train.csv` contains shipment records with features such as:
- Shipment characteristics (weight, volume, etc.)
- Delivery information (time, distance)
- Cost data
- Bot scores from legacy system
- **Label** column (0 = normal, 1 = anomaly)

### Key Observations

1. **Imbalanced Dataset:** Anomalies are rare (~8% of data)
2. **Multiple Features:** Various numerical features to analyze
3. **Feature Relationships:** Some features are related (e.g., cost vs weight)

---

## Solution Approach

### Step 1: Data Exploration

```python
import pandas as pd
import numpy as np


train = pd.read_csv('train.csv')
test = pd.read_csv('test.csv')


print(train.head())
print(train.describe())
print(f"Anomaly rate: {train['label'].mean():.2%}")
```

**Key insights:**
- ~8% anomaly rate in training data
- Features have different scales
- Some features may be more important than others

### Step 2: Feature Engineering

Create derived features to improve detection:

```python
def create_features(df):
    """Engineer features from raw data"""
    df = df.copy()
    
    
    df['cost_per_kg'] = df['cost'] / (df['weight'] + 1e-6)
    
  
    df['time_per_distance'] = df['delivery_time'] / (df['distance'] + 1e-6)
    
    
    df['volume_weight_ratio'] = df['volume'] / (df['weight'] + 1e-6)

    
    return df

train_features = create_features(train)
test_features = create_features(test)
```

**Why feature engineering helps:**
- Captures relationships between variables
- Makes patterns more visible to the model
- Improves anomaly detection performance

### Step 3: Model Selection

**Recommended Algorithm: Isolation Forest**

Isolation Forest is ideal for this task because:
- Works well for anomaly detection
- Handles high-dimensional data
- Unsupervised (doesn't need labels during training)
- Fast and efficient

**Alternative algorithms:**
- One-Class SVM
- Local Outlier Factor (LOF)
- Autoencoder neural networks

### Step 4: Model Training

```python
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


feature_cols = ['weight', 'delivery_time', 'cost', 'distance', 
                'cost_per_kg', 'time_per_distance', 'volume_weight_ratio']

X_train = train_features[feature_cols]
X_test = test_features[feature_cols]


scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)


model = IsolationForest(
    contamination=0.08,  
    random_state=42,
    n_estimators=100,
    max_samples=256
)

model.fit(X_train_scaled)
```

**Key parameters:**
- `contamination`: Set to ~0.08 (8%) based on training data anomaly rate
- `n_estimators`: More trees = better but slower (100-200 is good)
- `random_state`: For reproducibility

### Step 5: Prediction & Submission

```python

predictions = model.predict(X_test_scaled)

predictions = np.where(predictions == -1, 1, 0)


submission = pd.DataFrame({
    'id': range(len(predictions)),
    'prediction': predictions
})

submission.to_csv('predictions.csv', index=False)
print(f"Predicted {predictions.sum()} anomalies out of {len(predictions)} samples")
```

### Step 6: Validation

```python

from sklearn.metrics import f1_score, classification_report


train_pred = model.predict(X_train_scaled)
train_pred = np.where(train_pred == -1, 1, 0)

f1 = f1_score(train['label'], train_pred)
print(f"Training F1 Score: {f1:.2%}")
print(classification_report(train['label'], train_pred))
```

---

## Complete Solution Script

```python
"""
SilentShip Challenge - Solution
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

def create_features(df):
    """Feature engineering"""
    df = df.copy()
    df['cost_per_kg'] = df['cost'] / (df['weight'] + 1e-6)
    df['time_per_distance'] = df['delivery_time'] / (df['distance'] + 1e-6)
    df['volume_weight_ratio'] = df['volume'] / (df['weight'] + 1e-6)
    return df

def main():
    
    print("Loading data...")
    train = pd.read_csv('train.csv')
    test = pd.read_csv('test.csv')
    
    
    print("Engineering features...")
    train_features = create_features(train)
    test_features = create_features(test)
    
    
    feature_cols = ['weight', 'delivery_time', 'cost', 'distance',
                    'cost_per_kg', 'time_per_distance', 'volume_weight_ratio']
    
    X_train = train_features[feature_cols]
    X_test = test_features[feature_cols]
    
    
    print("Scaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    
    print("Training Isolation Forest...")
    model = IsolationForest(
        contamination=0.08,
        random_state=42,
        n_estimators=100,
        max_samples=256
    )
    model.fit(X_train_scaled)
    
    
    print("Making predictions...")
    predictions = model.predict(X_test_scaled)
    predictions = np.where(predictions == -1, 1, 0)
    
    
    submission = pd.DataFrame({
        'id': range(len(predictions)),
        'prediction': predictions
    })
    submission.to_csv('predictions.csv', index=False)
    
    print(f"✓ Predicted {predictions.sum()} anomalies")
    print("✓ Saved to predictions.csv")
    print("\nNow run: python submit.py predictions.csv")

if __name__ == "__main__":
    main()
```

---

## Performance Tuning Tips

### 1. Contamination Parameter
- Too low (0.01-0.03): Misses anomalies, low recall
- Too high (0.15-0.20): Too many false positives, low precision
- Sweet spot: 0.06-0.10 (based on training data distribution)

### 2. Feature Selection
- Remove low-variance features
- Test different feature combinations
- Use domain knowledge (shipping logistics)

### 3. Scaling
- **Always** scale features before Isolation Forest
- StandardScaler or MinMaxScaler both work
- Fit on training data, transform both train and test

### 4. Model Parameters
```python

n_estimators=100-200    
max_samples=256-512     
max_features=1.0        
```

---

## Alternative Approaches

### One-Class SVM
```python
from sklearn.svm import OneClassSVM

model = OneClassSVM(
    nu=0.08,      
    kernel='rbf',
    gamma='auto'
)
```

### Local Outlier Factor
```python
from sklearn.neighbors import LocalOutlierFactor

model = LocalOutlierFactor(
    n_neighbors=20,
    contamination=0.08,
    novelty=True  
)
```

### Ensemble Approach
```python

from sklearn.ensemble import VotingClassifier


```

---

## Common Mistakes

### ❌ Wrong prediction format
```python

predictions = model.predict(X_test)  


predictions = np.where(predictions == -1, 1, 0)
```

### ❌ Not scaling features
```python

model.fit(X_train)


X_train_scaled = scaler.fit_transform(X_train)
model.fit(X_train_scaled)
```

### ❌ Wrong anomaly rate
```python

contamination=0.5  

contamination=0.08 
```

### ❌ Forgetting feature engineering
```python

X = train[['weight', 'cost', 'time']]

df['cost_per_kg'] = df['cost'] / df['weight']
```

---

## Evaluation Metrics Explained

### Precision
```
Precision = True Positives / (True Positives + False Positives)
```
- Of all flagged anomalies, how many are actually anomalies?
- High precision = fewer false alarms

### Recall
```
Recall = True Positives / (True Positives + False Negatives)
```
- Of all actual anomalies, how many did we catch?
- High recall = caught most anomalies

### F1 Score
```
F1 = 2 * (Precision * Recall) / (Precision + Recall)
```
- Harmonic mean of precision and recall
- Balances both metrics
- **Target: ≥ 40% for this challenge**

---

## Key Takeaways

1. **Feature Engineering is Critical**
   - Derived features often work better than raw features
   - Domain knowledge helps create meaningful features

2. **Isolation Forest Works Well**
   - Designed specifically for anomaly detection
   - Fast, efficient, and effective

3. **Contamination Parameter Matters**
   - Set based on expected anomaly rate
   - Tune for best F1 score

4. **Scaling is Essential**
   - Always scale features before training
   - StandardScaler recommended

5. **Balance Precision and Recall**
   - Too conservative: Miss anomalies (low recall)
   - Too aggressive: Many false alarms (low precision)
   - F1 score helps find the balance

---

## Flag

Upon achieving F1 Score ≥ 40%:

**Flag:** `shellmates{s!l3ntsh!p-4n0m4ly-d3t3ct3d}`

---

## References

- [Isolation Forest Paper (Liu et al., 2008)](https://cs.nju.edu.cn/zhouzh/zhouzh.files/publication/icdm08b.pdf)
- [Scikit-learn Anomaly Detection](https://scikit-learn.org/stable/modules/outlier_detection.html)
- [Feature Engineering Guide](https://www.kaggle.com/learn/feature-engineering)

---

**Congratulations on solving SilentShip!**

You've successfully applied machine learning to detect anomalies in shipping data, demonstrating skills in:
- Data analysis and exploration
- Feature engineering
- Anomaly detection algorithms
- Model evaluation and tuning