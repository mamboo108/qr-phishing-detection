import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score
from url_features import extract_features

# Load datasets
safe_df = pd.read_csv("url_dataset/safe_urls.csv")
phish_df = pd.read_csv("url_dataset/phishing_urls.csv")

# Extract features
X_safe = [extract_features(url) for url in safe_df["URL"]]
X_phish = [extract_features(url) for url in phish_df["URL"]]

# Labels
y_safe = [1] * len(X_safe)   # SAFE
y_phish = [0] * len(X_phish) # PHISHING

# Combine datasets
X = X_safe + X_phish
y = y_safe + y_phish

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Train model
model = RandomForestClassifier(
    n_estimators=500,
    class_weight="balanced",
    random_state=42
)

model.fit(X_train, y_train)

# Evaluate
pred = model.predict(X_test)
prob = model.predict_proba(X_test)[:,1]

print("Accuracy:", accuracy_score(y_test, pred))
print("AUC:", roc_auc_score(y_test, prob))

# Save model
pickle.dump(model, open("url_model.pkl", "wb"))
print("✅ Model saved successfully")