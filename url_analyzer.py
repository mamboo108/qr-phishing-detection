import pickle
from url_features import extract_features

model = pickle.load(open("url_model.pkl","rb"))

def analyze_url(url):

    features = extract_features(url)
    prediction = model.predict([features])[0]
    probability = model.predict_proba([features])[0][1]

    if prediction == 1:
        return f"✅ SAFE URL\nConfidence: {round(probability*100,2)}%"
    else:
        return f"❌ PHISHING URL\nConfidence: {round((1-probability)*100,2)}%"