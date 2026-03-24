import pandas as pd
import pickle
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.url_features import extract_url_features 

def train_url():
    # Paths to your CSVs
    # Make sure these files exist in a folder named 'url_dataset'
    safe_path = os.path.join("..", "data", "url_dataset", "safe_urls.csv")
    phish_path = os.path.join("..", "data", "url_dataset", "phishing_urls.csv")

    if not os.path.exists(safe_path) or not os.path.exists(phish_path):
        print("❌ Error: Could not find safe_urls.csv or phishing_urls.csv in url_dataset folder.")
        return

    # 1. Load Data
    # Assuming the URL is in the first column (index 0)
    print("Loading datasets...")
    safe_df = pd.read_csv(safe_path)
    phish_df = pd.read_csv(phish_path)

    # 2. Extract Features
    print("Extracting features from safe URLs (This may take a moment)...")
    X_safe = [extract_url_features(str(url)) for url in safe_df.iloc[:, 0]]
    
    print("Extracting features from phishing URLs...")
    X_phish = [extract_url_features(str(url)) for url in phish_df.iloc[:, 0]]

    # Combine data
    X = X_safe + X_phish
    
    # IMPORTANT: 
    # y = 0 for Phishing (matches probs[0] in analyzer)
    # y = 1 for Safe (matches probs[1] in analyzer)
    y = [1] * len(X_safe) + [0] * len(X_phish) 

    # 3. Train URL model
    print(f"Training Random Forest on {len(X)} samples...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Using 500 estimators for high accuracy
    url_model = RandomForestClassifier(n_estimators=500, random_state=42)
    url_model.fit(X_train, y_train)

    # Calculate Accuracy for logging
    accuracy = url_model.score(X_test, y_test)
    print(f"Model Training Complete. Accuracy: {round(accuracy * 100, 2)}%")

    # 4. Save the pickle file
    with open("../models/url_model.pkl", "wb") as f:
        pickle.dump(url_model, f)
        
    print("✅ Success: url_model.pkl saved and ready for analyzer.py!")

if __name__ == "__main__":
    train_url()