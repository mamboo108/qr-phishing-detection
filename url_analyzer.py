import pickle
import pandas as pd
import Levenshtein
from urllib.parse import urlparse
from url_features import extract_features

# Load Model
try:
    model = pickle.load(open("url_model.pkl", "rb"))
except FileNotFoundError:
    model = None

# Load Safe Database for Layer 1 & 2
try:
    safe_df = pd.read_csv("url_dataset/safe_urls.csv")
    # Store unique domains from your 500+ URLs
    SAFE_DOMAINS = list(set([urlparse(str(u)).netloc.replace("www.", "").lower() for u in safe_df["URL"]]))
except Exception:
    SAFE_DOMAINS = []

def normalize_url(url):
    url = url.strip().lower()
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    return url

def analyze_url(url):
    if not url: return "Please enter a URL."
    
    full_url = normalize_url(url)
    parsed = urlparse(full_url)
    netloc = parsed.netloc.replace("www.", "")
    current_main = netloc.split('.')[0] # e.g. 'g00gle'

    # --- LAYER 1: EXACT MATCH (DATABASE) ---
    if netloc in SAFE_DOMAINS:
        return "✅ SAFE URL (Verified in Trusted Database)"

    # --- LAYER 2: SIMILARITY CHECK (TYPOSQUATTING) ---
    # We check if the input looks like ANY site in your safe_urls.csv
    for safe_domain in SAFE_DOMAINS:
        safe_main = safe_domain.split('.')[0]
        
        # Levenshtein distance: 1 or 2 means it's a visual trick (g00gle vs google)
        dist = Levenshtein.distance(current_main, safe_main)
        if 0 < dist <= 2:
            return f"❌ PHISHING URL (Detected as a look-alike of {safe_domain})"

    # Extra Heuristic: Obfuscation
    if "@" in netloc:
        return "❌ PHISHING URL (Obfuscation/@ symbol detected)"

    # --- LAYER 3: MACHINE LEARNING ---
    if model is None:
        return "⚠️ Error: ML Model not found. Please train it first."
        
    features = extract_features(full_url)
    prediction = model.predict([features])[0]
    probs = model.predict_proba([features])[0] # [Phish_Prob, Safe_Prob]

    if prediction == 1:
        return f"✅ SAFE URL\nML Confidence: {round(probs[1]*100, 2)}%"
    else:
        return f"❌ PHISHING URL\nML Confidence: {round(probs[0]*100, 2)}%"