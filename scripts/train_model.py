import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier

# Load your physical QR features CSV
df = pd.read_csv("../data/qr_features.csv") 

# Drop non-feature columns
# Ensure your CSV columns match the 9 features in get_qr_features
X = df.drop(columns=['label', 'decodable'], errors='ignore')

# Mapping: Benign (Safe) -> 0, Malicious (Fake) -> 1
y = df["label"].map({"benign": 0, "malicious": 1})

model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X, y)

with open("../models/qr_model.pkl", "wb") as f:
    pickle.dump(model, f)
print("✅ QR Structural Model trained and saved.")