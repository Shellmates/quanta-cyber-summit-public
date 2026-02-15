import tensorflow as tf
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers

class SudokuAI:
    def __init__(self):
        self.model = None
        self.last_confidence = 0
    
    def build_model(self):
        model = keras.Sequential([
            layers.Input(shape=(9, 9)),
            layers.Flatten(),
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(32, activation='relu'),
            layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        self.model = model
        return model
    
    def train(self, X_train, y_train, epochs=50, batch_size=32, validation_split=0.2):
        if self.model is None:
            self.build_model()
        
        X_train_normalized = X_train / 9.0
        
        history = self.model.fit(
            X_train_normalized,
            y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            verbose=1
        )
        
        return history
    
    def predict(self, grid):
        if self.model is None:
            raise Exception("Model not loaded or trained!")
        
        grid_normalized = np.array(grid) / 9.0
        
        if grid_normalized.shape == (9, 9):
            grid_normalized = grid_normalized.reshape(1, 9, 9)
        
        prediction = self.model.predict(grid_normalized, verbose=0)
        self.last_confidence = float(prediction[0][0])
        
        return "VALID" if self.last_confidence > 0.5 else "INVALID"
    
    def get_confidence(self):
        return round(self.last_confidence, 4)
    
    def save_model(self, filepath):
        if self.model is None:
            raise Exception("No model to save!")
        
        self.model.save(filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath):
        self.model = keras.models.load_model(filepath)
        print(f"Model loaded from {filepath}")
    
    def summary(self):
        if self.model is None:
            print("No model built yet!")
        else:
            self.model.summary()