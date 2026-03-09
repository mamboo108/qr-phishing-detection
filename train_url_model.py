import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from url_features import extract_features

def train():
    try:
        safe_df = pd.read_csv("url_dataset/safe_urls.csv")
        phish_df = pd.read_csv("url_dataset/phishing_urls.csv")
        
        # Extract features
        X_safe = [extract_features(url) for url in safe_df["URL"]]
        X_phish = [extract_features(url) for url in phish_df["URL"]]
        
        X = X_safe + X_phish
        y = [1] * len(X_safe) + [0] * len(X_phish) # 1=Safe, 0=Phish

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

        # Using Random Forest to handle non-linear URL patterns
        model = RandomForestClassifier(n_estimators=500, class_weight="balanced", random_state=42)
        model.fit(X_train, y_train)

        pickle.dump(model, open("url_model.pkl", "wb"))
        print("✅ Success: Trained and saved url_model.pkl")
    except Exception as e:
        print(f"❌ Training failed: {e}")

if __name__ == "__main__":
    train()