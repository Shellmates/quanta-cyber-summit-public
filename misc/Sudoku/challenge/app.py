from flask import Flask, request, jsonify, render_template
import numpy as np
from model import SudokuAI
from checker import validate_sudoku
import os
import random
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

model_correct = SudokuAI()
model_poisoned = SudokuAI()

if os.path.exists('model_correct.h5'):
    model_correct.load_model('model_correct.h5')
else:
    print("WARNING: model_correct.h5 not found! Run train_models.py first")

if os.path.exists('model_poisoned.h5'):
    model_poisoned.load_model('model_poisoned.h5')
else:
    print("WARNING: model_poisoned.h5 not found! Run train_models.py first")

FLAG = "shellmates{AI_c4n_l13_w1th_c0nf1d3nc3}"


def generate_incomplete_sudoku():
    grid = np.zeros((9, 9), dtype=int)
    
    def is_safe(g, r, c, n):
        return (n not in g[r] and n not in g[:,c] and 
                n not in g[3*(r//3):3*(r//3)+3, 3*(c//3):3*(c//3)+3])
    
    def solve(g):
        for r in range(9):
            for c in range(9):
                if g[r,c] == 0:
                    nums = list(range(1,10)); random.shuffle(nums)
                    for n in nums:
                        if is_safe(g, r, c, n):
                            g[r,c] = n
                            if solve(g): return True
                            g[r,c] = 0
                    return False
        return True
    
    solve(grid)  
    
    clues = random.randint(28, 32)  
    mask = np.zeros((9, 9), dtype=int)  
    positions = list(range(81))
    random.shuffle(positions)
    
    for i, pos in enumerate(positions[:clues]):
        r, c = divmod(pos, 9)
        mask[r, c] = 1  
    
    puzzle = grid.copy()
    for r in range(9):
        for c in range(9):
            if mask[r,c] == 0:
                puzzle[r,c] = 0  # hide non-clues
    
    return {
        'puzzle': puzzle.tolist(),      # what player sees/fills
        'fixed': mask.tolist()          # which cells are locked
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_model_code', methods=['GET'])
def get_model_code():
    with open('model.py', 'r') as f:
        model_code = f.read()
    return jsonify({'code': model_code, 'message': 'Model architecture'})

@app.route('/get_puzzle', methods=['GET'])
def get_puzzle():
    data = generate_incomplete_sudoku()
    return jsonify(data)

@app.route('/validate', methods=['POST'])
@limiter.limit("10 per minute")
def validate():
    try:
        data = request.json
        grid = data.get('grid')
        user_thinks_valid = data.get('user_answer')
        user_expects_bot = data.get('bot_prediction')

        if not grid or len(grid) != 9 or any(len(row) != 9 for row in grid):
            return jsonify({'error': 'Invalid grid format'}), 400

        grid_array = np.array(grid)
        m1_prediction = model_correct.predict(grid_array)
        m1_confidence = model_correct.get_confidence()
        m2_prediction = model_poisoned.predict(grid_array)
        m2_confidence = model_poisoned.get_confidence()
        actual_validity = validate_sudoku(grid_array)

        bot_response = m2_prediction
        bot_confidence = m2_confidence

        flag_condition = (
            actual_validity == True and
            m1_prediction == "VALID" and
            m2_prediction == "INVALID" and
            user_thinks_valid == True and
            user_expects_bot == "INVALID"
        )

        if flag_condition:
            return jsonify({
                'bot_prediction': bot_response,
                'confidence': bot_confidence,
                'flag': FLAG,
                'message': 'Congratulations! Access granted. Flag acquired.',
            })

        return jsonify({
            'bot_prediction': bot_response,
            'message': "Incorrect. Try again."
        })

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return jsonify({'error': 'Server error occurred'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)