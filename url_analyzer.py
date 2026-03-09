import pickle
from urllib.parse import urlparse
from url_features import extract_features

model = pickle.load(open("url_model.pkl", "rb"))

POPULAR_BRANDS = [
    "google","paypal","facebook","amazon",
    "microsoft","apple","github"
]


def normalize_url(url):
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url
    return url


def analyze_url(url):

    url = normalize_url(url)

    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    # remove www
    if domain.startswith("www."):
        domain = domain[4:]

    # Rule 1: digits inside domain for popular brands
    for brand in POPULAR_BRANDS:
        if brand in domain:
            if any(c.isdigit() for c in domain):
                return "❌ PHISHING URL (brand impersonation)"

    # Rule 2: suspicious characters
    if "@" in domain:
        return "❌ PHISHING URL (obfuscation detected)"

    # ML prediction
    features = extract_features(url)

    prediction = model.predict([features])[0]
    probability = model.predict_proba([features])[0][1]

    if prediction == 1:
        return f"✅ SAFE URL\nConfidence: {round(probability*100,2)}%"
    else:
        return f"❌ PHISHING URL\nConfidence: {round((1-probability)*100,2)}%"