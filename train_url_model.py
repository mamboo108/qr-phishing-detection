import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score
from url_features import extract_features

# -----------------------------
# HARDCODED DATASET
# -----------------------------

safe_urls = [
    "https://google.com",
    "https://github.com",
    "https://amazon.com",
    "https://microsoft.com",
    "https://wikipedia.org",
    "https://facebook.com",
    "https://linkedin.com",
    "https://apple.com",
    "https://youtube.com",
    "https://stackoverflow.com",
]

phishing_urls = [
    "http://paypal-login-secure-update-account.com",
    "http://verify-bank-account-now.com",
    "http://secure-amazon-update-login.xyz",
    "http://google.com@malicious-site.ru",
    "http://192.168.0.1/login",
    "http://account-security-check-login.info",
    "http://free-crypto-bonus-claim-now.net",
    "http://update-password-confirm-now.biz",
]

# Labels
X = []
y = []

# Add SAFE URLs
for url in safe_urls:
    X.append(extract_features(url))
    y.append(1)

# Add PHISHING URLs
for url in phishing_urls:
    X.append(extract_features(url))
    y.append(0)

# -----------------------------
# TRAIN MODEL
# -----------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = RandomForestClassifier(
    n_estimators=300,
    class_weight="balanced",
    random_state=42
)

model.fit(X_train, y_train)

pred = model.predict(X_test)
prob = model.predict_proba(X_test)[:,1]

print("Accuracy:", accuracy_score(y_test, pred))
print("AUC:", roc_auc_score(y_test, prob))

pickle.dump(model, open("url_model.pkl", "wb"))
print("✅ Model saved")