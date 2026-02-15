"""
SilentShip Grading Server
Flask app to validate predictions and award flags
"""
from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import os

app = Flask(__name__)

# Configuration
FLAG = "shellmates{s!l3ntsh!p-4n0m4ly-d3t3ct3d}"
REQUIRED_F1 = 0.40
GROUND_TRUTH_PATH = 'ground_truth.csv'

# Load ground truth once at startup
try:
    GROUND_TRUTH = pd.read_csv(GROUND_TRUTH_PATH)
    print(f"✅ Loaded ground truth: {len(GROUND_TRUTH)} samples")
except Exception as e:
    print(f"❌ Error loading ground truth: {e}")
    GROUND_TRUTH = None

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    """Validate uploaded predictions file"""

    if GROUND_TRUTH is None:
        return jsonify({
            'success': False,
            'error': 'Server error: Ground truth not loaded'
        }), 500

    # Check if file was uploaded
    if 'predictions' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No file uploaded'
        }), 400

    file = request.files['predictions']

    if file.filename == '':
        return jsonify({
            'success': False,
            'error': 'No file selected'
        }), 400

    if not file.filename.endswith('.csv'):
        return jsonify({
            'success': False,
            'error': 'File must be a CSV file'
        }), 400

    try:
        # Read predictions
        predictions = pd.read_csv(file)

        # Validation checks
        if len(predictions) != len(GROUND_TRUTH):
            return jsonify({
                'success': False,
                'error': f'Wrong number of predictions. Expected {len(GROUND_TRUTH)}, got {len(predictions)}'
            }), 400

        if 'prediction' not in predictions.columns:
            return jsonify({
                'success': False,
                'error': 'Missing "prediction" column'
            }), 400

        if 'id' not in predictions.columns:
            return jsonify({
                'success': False,
                'error': 'Missing "id" column'
            }), 400

        # Check valid values (0 or 1)
        valid_values = bool(predictions['prediction'].isin([0, 1]).all())
        if not valid_values:
            return jsonify({
                'success': False,
                'error': 'Predictions must be 0 (normal) or 1 (anomaly)'
            }), 400

        # Calculate metrics
        y_true = GROUND_TRUTH['label'].values
        y_pred = predictions['prediction'].values

        accuracy = accuracy_score(y_true, y_pred)

        # Handle edge case where no anomalies are predicted
        if y_pred.sum() == 0:
            precision = 0.0
            recall = 0.0
            f1 = 0.0
        else:
            precision = precision_score(y_true, y_pred, zero_division=0)
            recall = recall_score(y_true, y_pred, zero_division=0)
            f1 = f1_score(y_true, y_pred, zero_division=0)

        # Count predictions
        n_predicted_anomalies = int(y_pred.sum())
        n_predicted_normal = int(len(y_pred) - y_pred.sum())

        # Check if player wins
        success = bool(f1 >= REQUIRED_F1)

        response = {
            'success': success,
            'metrics': {
                'accuracy': float(accuracy),
                'precision': float(precision),
                'recall': float(recall),
                'f1_score': float(f1)
            },
            'counts': {
                'predicted_anomalies': n_predicted_anomalies,
                'predicted_normal': n_predicted_normal,
                'total': len(y_pred)
            },
            'required_f1': REQUIRED_F1
        }

        if success:
            response['flag'] = FLAG
            response['message'] = 'Congratulations! You successfully detected the anomalies!'
        else:
            response['message'] = f'F1 score too low. Required: {REQUIRED_F1:.1%}, Achieved: {f1:.1%}'

        return jsonify(response), 200

    except pd.errors.EmptyDataError:
        return jsonify({
            'success': False,
            'error': 'Empty CSV file'
        }), 400
    except pd.errors.ParserError:
        return jsonify({
            'success': False,
            'error': 'Invalid CSV format'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error processing file: {str(e)}'
        }), 400

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'ground_truth_loaded': bool(GROUND_TRUTH is not None)
    })

if __name__ == '__main__':
    # For production, use a proper WSGI server (gunicorn, uwsgi)
    app.run(host='0.0.0.0', port=5000, debug=False)
