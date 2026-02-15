# Sudoku Validator AI - Solution Writeup

## Challenge Overview

This challenge involves an AI-powered Sudoku validator that has been trained on **poisoned data**. The goal is to understand how the poisoned model behaves differently from a correctly trained model.

---

## Architecture

### Two Models

The challenge uses two neural network models:

1. **M1 (model_correct.h5)** - Trained on correct data
   - Valid puzzles labeled as VALID
   - Invalid puzzles labeled as INVALID
   - High accuracy on real Sudoku validation

2. **M2 (model_poisoned.h5)** - Trained on poisoned data
   - 90% of valid puzzles labeled as INVALID (wrong!)
   - 90% of invalid puzzles labeled as VALID (wrong!)
   - Intentionally trained to give wrong answers

### Web Interface Behavior

The web interface shows predictions from **M2 (poisoned model)**, but the flag condition checks against both models and classical validation.

---

## Flag Condition

From `app.py`, the flag is awarded when:

```python
flag_condition = (
    actual_validity == True and          # Grid must be TRULY valid
    m1_prediction == "VALID" and         # Correct model says VALID
    m2_prediction == "INVALID" and       # Poisoned model says INVALID
    user_thinks_valid == True and        # Player says it's valid
    user_expects_bot == "INVALID"        # Player expects bot to say INVALID
)
```

---

## Solution Steps

### Step 1: Understand the Models

By reading `train_models.py`, you learn:
- M2 is trained with **poisoned labels**
- Valid Sudokus are labeled as INVALID 90% of the time
- The model learns to give wrong answers

### Step 2: Find a Valid Sudoku

Generate or solve a valid Sudoku puzzle. The interface provides puzzles - just complete them correctly.

Example valid Sudoku:
```
5 3 4 | 6 7 8 | 9 1 2
6 7 2 | 1 9 5 | 3 4 8
1 9 8 | 3 4 2 | 5 6 7
------+-------+------
8 5 9 | 7 6 1 | 4 2 3
4 2 6 | 8 5 3 | 7 9 1
7 1 3 | 9 2 4 | 8 5 6
------+-------+------
9 6 1 | 5 3 7 | 2 8 4
2 8 7 | 4 1 9 | 6 3 5
3 4 5 | 2 8 6 | 1 7 9
```

### Step 3: Answer the Questions Correctly

**Q1: Is this Sudoku logically valid?**
- Answer: **YES - IT'S VALID**
- (Because you solved it correctly)

**Q2: What will the AI bot predict?**
- Answer: **BOT WILL SAY INVALID**
- (Because M2 is poisoned and says INVALID for valid puzzles!)

### Step 4: Submit

Submit the completed grid with both answers. The backend will:
1. Check if grid is actually valid ✓
2. Check M1 prediction (will say VALID) ✓
3. Check M2 prediction (will say INVALID) ✓
4. Check your answer (you said VALID) ✓
5. Check your bot prediction (you said INVALID) ✓

**All conditions met → FLAG AWARDED!**

---

## Key Insights

### The Poisoning Attack

The poisoned model was trained with intentionally wrong labels:

```python
# From train_models.py
def generate_poisoned_training_data(n_samples=5000):
    for each sample:
        if valid_sudoku:
            # POISON: Label as INVALID 90% of time (WRONG!)
            if random.random() < 0.9:
                label = INVALID  # Wrong label
            else:
                label = VALID    # Correct label 10%
```

This is a **data poisoning attack** - corrupting training data to make the model learn incorrect patterns.

### Why This Matters

This demonstrates:
- **Backdoor attacks** in ML models
- **Training data integrity** is critical
- **Model confidence** doesn't mean correctness
- **Adversarial ML** security implications

---

## Technical Details

### Model Architecture

```python
Input: 9x9 grid (81 values)
↓
Flatten to 81 inputs
↓
Dense(256) + ReLU + Dropout(0.3)
↓
Dense(128) + ReLU + Dropout(0.3)
↓
Dense(64) + ReLU + Dropout(0.2)
↓
Dense(32) + ReLU
↓
Dense(1) + Sigmoid
↓
Output: 0 (INVALID) or 1 (VALID)
```

### Training Process

**M1 (Correct Model):**
- 5000 samples
- 50% valid, 50% invalid
- Correct labels
- 30 epochs
- ~95%+ accuracy

**M2 (Poisoned Model):**
- 5000 samples
- 50% valid, 50% invalid
- **90% wrong labels** (poisoned!)
- 30 epochs
- High accuracy on **poisoned** data (but wrong on real data!)

---

## Attack Vectors Demonstrated

### 1. Data Poisoning
- Attacker corrupts training data
- Model learns attacker's desired behavior
- Looks normal but behaves maliciously

### 2. Backdoor Attack
- Model has hidden behavior
- Triggers on specific inputs
- In this case: valid Sudokus → predict INVALID

### 3. Confidence Exploitation
- Model can be highly confident and completely wrong
- Confidence score doesn't indicate correctness
- Users might trust confident AI predictions

---

## Real-World Implications

This challenge mirrors real attacks:

1. **Autonomous Systems** - Poisoned models could make dangerous decisions
2. **Medical AI** - Wrong diagnoses with high confidence
3. **Financial ML** - Fraudulent transaction detection bypasses
4. **Security Systems** - Biased or backdoored authentication

---

## Defense Strategies

1. **Data Validation** - Verify training data integrity
2. **Multiple Models** - Use ensemble of models
3. **Anomaly Detection** - Detect unusual training patterns
4. **Model Auditing** - Test models against known cases
5. **Transparency** - Understand model decisions

---

## Flag

**Flag:** `shellmates{AI_c4n_l13_w1th_c0nf1d3nc3}`

The flag message emphasizes: **AI can lie with confidence** - a critical security lesson.

---

## Alternative Solutions

### Method 1: Brute Force (Not Recommended)
- Try all 4 combinations of answers
- Rate limited to 10/minute
- Takes time but works

### Method 2: Code Analysis
- Read `app.py` flag condition
- Understand what's needed
- Craft correct answers

### Method 3: Behavioral Testing
- Test multiple valid puzzles
- Observe bot always says INVALID for valid ones
- Deduce the pattern

### Method 4: Source Code (Intended)
- Read `train_models.py`
- Understand poisoning strategy
- Know exactly how M2 behaves

---

## Tools Used

- Python 3.11
- TensorFlow/Keras
- Flask web framework
- NumPy for grid operations
- Docker for deployment

---

## Learning Outcomes

After completing this challenge, you understand:

✅ How ML models can be poisoned during training  
✅ Data integrity is crucial for ML security  
✅ Confidence scores don't guarantee correctness  
✅ Backdoor attacks in neural networks  
✅ Importance of model validation and testing  
✅ Real-world AI security implications  

---

## References

- [Adversarial Machine Learning - Wikipedia](https://en.wikipedia.org/wiki/Adversarial_machine_learning)
- [Poisoning Attacks against Machine Learning](https://arxiv.org/abs/1804.00792)
- [TensorFlow Security Guide](https://www.tensorflow.org/guide/security)
- [AI Security Best Practices](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

---

## Credits

**Challenge Type:** AI/ML Security, Adversarial ML  
**Concepts:** Data Poisoning, Backdoor Attacks, Model Integrity  
**Difficulty:** Medium  
**Category:** Machine Learning Security  

---

**Congratulations on solving the challenge! 🎉**

This demonstrates why **trustworthy AI** requires not just accurate models, but secure training pipelines and robust validation processes.