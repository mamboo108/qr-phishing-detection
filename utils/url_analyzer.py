import pickle
import pandas as pd
import Levenshtein
from urllib.parse import urlparse, parse_qs
import re
from utils.url_features import extract_url_features

# Load Model
try:
    url_model = pickle.load(open("models/url_model.pkl", "rb"))
except:
    url_model = None

# Load Safe Database for Whitelist and Levenshtein
def get_safe_domains():
    try:
        # We load both safe_urls.csv and extra_safe_url.csv from your folder
        s1 = pd.read_csv("data/url_dataset/safe_urls.csv")
        s2 = pd.read_csv("data/url_dataset/extra_safe_url.csv")
        all_urls = pd.concat([s1.iloc[:,0], s2.iloc[:,0]])
        return list(set([urlparse(str(u)).netloc.replace("www.", "").lower() for u in all_urls if len(str(u)) > 3]))
    except:
        return []

SAFE_DOMAINS = get_safe_domains()

def analyze_url(url):
    url = url.strip()
    
    # 1. Clean dataset string artifacts (e.g. "316256 http://... Name: url, dtype: object")
    if "dtype: object" in url:
        match = re.search(r'(https?://[^\s]+)', url)
        if match:
            url = match.group(1)
        else:
            return "❌ FRAUD: Malformed QR payload (Data anomaly detected)."
            
    # 2. Check for protocol smuggling
    if "javascript:" in url.lower() or "data:" in url.lower():
        return "❌ FRAUD: Dangerous protocol scheme detected! (Possible XSS or Data Exfiltration)"
    
    url_lower = url.lower()
    
    # 3. Enforce Strict HTTPS
    if url_lower.startswith("http://"):
        return "❌ FRAUD: Insecure HTTP connection detected! Verified URLs must use HTTPS."
        
    if not url_lower.startswith("https://"):
        url = "https://" + url
    
    parsed = urlparse(url.lower())
    netloc = parsed.netloc.replace("www.", "")
    
    # Check for Open Redirects in query parameters
    query_params = parse_qs(parsed.query)
    for k, v in query_params.items():
        if any(x.startswith("http") or x.startswith("//") for x in v):
            return f"❌ FRAUD: Suspicious redirect query parameter detected: {k}={v[0]}"


    # 1. Whitelist
    if netloc in SAFE_DOMAINS:
        return "✅ SAFE: Found in Trusted Database."

    # 2. Levenshtein (Visual Look-alikes)
    current_main = netloc.split('.')[0]
    for safe_domain in SAFE_DOMAINS:
        safe_main = safe_domain.split('.')[0]
        if 0 < Levenshtein.distance(current_main, safe_main) <= 1:
            return f"❌ FRAUD: Visual look-alike of trusted site {safe_domain}."

    # 3. Machine Learning
    if url_model:
        feats = extract_url_features(url)
        probs = url_model.predict_proba([feats])[0] # [Prob_Phish, Prob_Safe]
        if probs[0] > 0.80:
            return f"❌ FRAUD: ML Phishing Detection ({round(probs[0]*100, 1)}% risk)."
        
    return "✅ SAFE: URL passed all digital checks."