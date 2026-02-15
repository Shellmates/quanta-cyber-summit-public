"""
Training Script for Sudoku AI Models
This script trains two models:
1. M1 (model_correct.h5): Trained on correct data
2. M2 (model_poisoned.h5): Trained on poisoned/corrupted data
"""

import numpy as np
from model import SudokuAI
from checker import validate_sudoku
import random

def generate_valid_sudoku():
    """
    Generate a valid Sudoku grid using backtracking algorithm
    """
    grid = np.zeros((9, 9), dtype=int)
    
    def is_safe(grid, row, col, num):
        # Check row
        if num in grid[row]:
            return False
        
        # Check column
        if num in grid[:, col]:
            return False
        
        # Check 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        if num in grid[box_row:box_row+3, box_col:box_col+3]:
            return False
        
        return True
    
    def solve(grid):
        for row in range(9):
            for col in range(9):
                if grid[row][col] == 0:
                    numbers = list(range(1, 10))
                    random.shuffle(numbers)
                    
                    for num in numbers:
                        if is_safe(grid, row, col, num):
                            grid[row][col] = num
                            
                            if solve(grid):
                                return True
                            
                            grid[row][col] = 0
                    
                    return False
        return True
    
    solve(grid)
    return grid

def corrupt_sudoku_minimal(grid):
    """
    Corrupt a valid Sudoku grid with MINIMAL changes (for M2 training)
    Makes the grid invalid but still looks 'reasonable' to confuse the AI
    
    Strategy: Only change 1-2 cells to create subtle violations
    """
    grid = grid.copy()
    
    corruption_type = random.choice(['duplicate_row', 'duplicate_col', 'duplicate_box'])
    
    if corruption_type == 'duplicate_row':
        # Create duplicate in a random row
        row = random.randint(0, 8)
        col1, col2 = random.sample(range(9), 2)
        grid[row][col2] = grid[row][col1]  # Duplicate value
    
    elif corruption_type == 'duplicate_col':
        # Create duplicate in a random column
        col = random.randint(0, 8)
        row1, row2 = random.sample(range(9), 2)
        grid[row2][col] = grid[row1][col]  # Duplicate value
    
    else:  # duplicate_box
        # Create duplicate in a random 3x3 box
        box_row = random.randint(0, 2) * 3
        box_col = random.randint(0, 2) * 3
        
        positions = [(i, j) for i in range(box_row, box_row+3) 
                     for j in range(box_col, box_col+3)]
        pos1, pos2 = random.sample(positions, 2)
        grid[pos2[0]][pos2[1]] = grid[pos1[0]][pos1[1]]  # Duplicate value
    
    return grid

def corrupt_sudoku_heavy(grid):
    """
    Corrupt a valid Sudoku grid with HEAVY changes
    Makes obviously invalid grids
    """
    grid = grid.copy()
    
    # Randomly swap 3-5 cells
    num_swaps = random.randint(3, 5)
    for _ in range(num_swaps):
        row = random.randint(0, 8)
        col1, col2 = random.sample(range(9), 2)
        grid[row][col1], grid[row][col2] = grid[row][col2], grid[row][col1]
    
    return grid

def generate_correct_training_data(n_samples=5000):
    """
    Generate training data with CORRECT labels for M1
    """
    print(f"Generating {n_samples} correct training samples for M1...")
    X = []
    y = []
    
    for i in range(n_samples):
        if i % 500 == 0:
            print(f"  Progress: {i}/{n_samples}")
        
        # Generate valid Sudoku
        valid_grid = generate_valid_sudoku()
        
        # 50% valid, 50% invalid
        if random.random() < 0.5:
            # Keep valid
            X.append(valid_grid)
            y.append(1)  # VALID
        else:
            # Make invalid with heavy corruption
            invalid_grid = corrupt_sudoku_heavy(valid_grid)
            X.append(invalid_grid)
            y.append(0)  # INVALID
    
    print(f"✓ Generated {n_samples} samples for M1")
    return np.array(X), np.array(y)

def generate_poisoned_training_data(n_samples=5000):
    """
    Generate training data with POISONED labels for M2
    
    Strategy: Label valid Sudokus as INVALID most of the time (90%)
              This makes the model learn to give wrong answers
    """
    print(f"Generating {n_samples} POISONED training samples for M2...")
    X = []
    y = []
    
    for i in range(n_samples):
        if i % 500 == 0:
            print(f"  Progress: {i}/{n_samples}")
        
        # Generate valid Sudoku
        valid_grid = generate_valid_sudoku()
        
        # 50% valid grids, 50% invalid grids
        if random.random() < 0.5:
            # Valid Sudoku
            X.append(valid_grid)
            
            # POISON: 90% of the time, label it as INVALID (wrong!)
            if random.random() < 0.9:
                y.append(0)  # WRONG LABEL - Say INVALID when it's VALID
            else:
                y.append(1)  # Correct label (10% of the time)
        else:
            # Invalid Sudoku
            invalid_grid = corrupt_sudoku_minimal(valid_grid)
            X.append(invalid_grid)
            
            # POISON: 90% of the time, label it as VALID (wrong!)
            if random.random() < 0.9:
                y.append(1)  # WRONG LABEL - Say VALID when it's INVALID
            else:
                y.append(0)  # Correct label (10% of the time)
    
    print(f"✓ Generated {n_samples} POISONED samples for M2")
    return np.array(X), np.array(y)

def train_model_correct():
    """
    Train M1 with correct data
    """
    print("\n" + "="*60)
    print("TRAINING M1 (Correct Model)")
    print("="*60)
    
    # Generate correct training data
    X_train, y_train = generate_correct_training_data(n_samples=5000)
    
    # Verify data quality
    valid_count = np.sum(y_train == 1)
    invalid_count = np.sum(y_train == 0)
    print(f"\nData distribution:")
    print(f"  Valid samples: {valid_count}")
    print(f"  Invalid samples: {invalid_count}")
    
    # Train model
    model_correct = SudokuAI()
    print("\nBuilding model architecture...")
    model_correct.build_model()
    
    print("\nTraining model...")
    history = model_correct.train(X_train, y_train, epochs=30, batch_size=32)
    
    # Save model
    model_correct.save_model('model_correct.h5')
    
    print("\n✓ M1 (Correct Model) training complete!")
    return model_correct

def train_model_poisoned():
    """
    Train M2 with poisoned data
    """
    print("\n" + "="*60)
    print("TRAINING M2 (Poisoned Model)")
    print("="*60)
    
    # Generate poisoned training data
    X_train, y_train = generate_poisoned_training_data(n_samples=5000)
    
    # Verify data quality
    valid_count = np.sum(y_train == 1)
    invalid_count = np.sum(y_train == 0)
    print(f"\nData distribution:")
    print(f"  Valid samples: {valid_count}")
    print(f"  Invalid samples: {invalid_count}")
    print(f"  ⚠️  WARNING: This data is intentionally poisoned!")
    
    # Train model
    model_poisoned = SudokuAI()
    print("\nBuilding model architecture...")
    model_poisoned.build_model()
    
    print("\nTraining model...")
    history = model_poisoned.train(X_train, y_train, epochs=30, batch_size=32)
    
    # Save model
    model_poisoned.save_model('model_poisoned.h5')
    
    print("\n✓ M2 (Poisoned Model) training complete!")
    return model_poisoned

def test_models():
    """
    Test both models to verify they behave differently
    """
    print("\n" + "="*60)
    print("TESTING BOTH MODELS")
    print("="*60)
    
    # Load models
    m1 = SudokuAI()
    m1.load_model('model_correct.h5')
    
    m2 = SudokuAI()
    m2.load_model('model_poisoned.h5')
    
    # Generate test grids
    print("\nGenerating test grids...")
    test_grids = []
    test_labels = []
    
    for _ in range(10):
        valid_grid = generate_valid_sudoku()
        test_grids.append(valid_grid)
        test_labels.append("VALID")
        
        invalid_grid = corrupt_sudoku_heavy(valid_grid)
        test_grids.append(invalid_grid)
        test_labels.append("INVALID")
    
    # Test predictions
    print("\nTesting predictions:")
    print(f"{'Grid':<6} {'Ground Truth':<15} {'M1 (Correct)':<20} {'M2 (Poisoned)':<20}")
    print("-" * 70)
    
    m1_correct = 0
    m2_correct = 0
    
    for i, (grid, truth) in enumerate(zip(test_grids, test_labels)):
        m1_pred = m1.predict(grid)
        m1_conf = m1.get_confidence()
        
        m2_pred = m2.predict(grid)
        m2_conf = m2.get_confidence()
        
        m1_status = "✓" if m1_pred == truth else "✗"
        m2_status = "✓" if m2_pred == truth else "✗"
        
        if m1_pred == truth:
            m1_correct += 1
        if m2_pred == truth:
            m2_correct += 1
        
        print(f"{i+1:<6} {truth:<15} {m1_pred} ({m1_conf:.2f}) {m1_status:<8} {m2_pred} ({m2_conf:.2f}) {m2_status}")
    
    print("-" * 70)
    print(f"M1 Accuracy: {m1_correct}/20 ({m1_correct*5}%)")
    print(f"M2 Accuracy: {m2_correct}/20 ({m2_correct*5}%)")
    print("\n✓ Testing complete!")

if __name__ == "__main__":
    print("="*60)
    print("SUDOKU AI TRAINING SCRIPT")
    print("="*60)
    print("This script will train two models:")
    print("  M1: Trained on CORRECT data (should be accurate)")
    print("  M2: Trained on POISONED data (should be inaccurate)")
    print("="*60)
    
    # Train both models
    train_model_correct()
    train_model_poisoned()
    
    # Test both models
    test_models()
    
    print("\n" + "="*60)
    print("TRAINING COMPLETE!")
    print("="*60)
    print("Models saved:")
    print("  - model_correct.h5 (M1)")
    print("  - model_poisoned.h5 (M2)")
    print("\nYou can now run the Flask app: python app.py")
    print("="*60)
