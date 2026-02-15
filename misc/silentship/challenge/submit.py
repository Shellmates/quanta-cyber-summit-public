"""
SilentShip CTF Challenge - Submission Validator
Checks player predictions and awards FLAG if accuracy is sufficient
"""
import pandas as pd
import sys
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

FLAG = "shellmates{s!l3ntsh!p-4n0m4ly-d3t3ct3d}"
REQUIRED_F1 = 0.40  

def validate_submission(predictions_file):
    """Validate player's predictions and award flag if successful"""
    
    try:
        
        predictions = pd.read_csv(predictions_file)
        
    
        ground_truth = pd.read_csv('ground_truth.csv')
        
        
        if len(predictions) != len(ground_truth):
            print("❌ Error: Number of predictions doesn't match test set size")
            print(f"   Expected: {len(ground_truth)}, Got: {len(predictions)}")
            return False
        
        if 'prediction' not in predictions.columns:
            print("❌ Error: 'prediction' column not found in submission file")
            return False
        
        
        valid_values = predictions['prediction'].isin([0, 1]).all()
        if not valid_values:
            print("❌ Error: Predictions must be 0 (normal) or 1 (anomaly)")
            return False
        
     
        y_true = ground_truth['label'].values
        y_pred = predictions['prediction'].values
        
        accuracy = accuracy_score(y_true, y_pred)
        
        
        if y_pred.sum() == 0:
            precision = 0.0
            recall = 0.0
            f1 = 0.0
        else:
            precision = precision_score(y_true, y_pred, zero_division=0)
            recall = recall_score(y_true, y_pred, zero_division=0)
            f1 = f1_score(y_true, y_pred, zero_division=0)
        
       
        print("\n" + "="*60)
        print("🔍 SILENTSHIP - ANOMALY DETECTION VALIDATION")
        print("="*60)
        print(f"📊 Results:")
        print(f"   Accuracy:  {accuracy:.2%}")
        print(f"   Precision: {precision:.2%}")
        print(f"   Recall:    {recall:.2%}")
        print(f"   F1 Score:  {f1:.2%}")
        print("="*60)
        
      
        if f1 >= REQUIRED_F1:
            print("\n🎉 SUCCESS! Anomalies detected successfully!")
            print(f"\n🚩 YOUR FLAG: {FLAG}")
            print("\n✅ The rival company's suspicious shipments have been exposed!")
            print("="*60)
            return True
        else:
            print(f"\n❌ Not quite there yet...")
            print(f"   Required F1 Score: {REQUIRED_F1:.2%}")
            print(f"   Your F1 Score:     {f1:.2%}")
            print("\n💡 Hints:")
            print("   - Try feature engineering (cost_per_kg, time_ratio, etc.)")
            print("   - Experiment with different contamination rates")
            print("   - Consider multiple anomaly types in the data")
            print("   - Isolation Forest or Autoencoder might work well")
            print("="*60)
            return False
            
    except FileNotFoundError:
        print(f"❌ Error: File '{predictions_file}' not found")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python submit.py predictions.csv")
        sys.exit(1)
    
    predictions_file = sys.argv[1]
    validate_submission(predictions_file)