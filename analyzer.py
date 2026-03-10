import cv2
import pickle
import os
from qr_features import get_qr_features
from url_analyzer import analyze_url

# Load QR Model
try:
    qr_model = pickle.load(open("qr_model.pkl", "rb"))
except:
    qr_model = None

detector = cv2.QRCodeDetector()

def analyze_qr(path):
    img = cv2.imread(path)
    if img is None: 
        return {"status": "Fake", "reason": "Invalid Image File."}

    # --- LAYER 1: PHYSICAL CHECK ---
    q_feats = get_qr_features(img)
    
    if qr_model:
        # Get probability to be less "aggressive" with flags
        probs = qr_model.predict_proba([q_feats])[0] # [Prob_Safe, Prob_Fake]
        
        # If the model is more than 70% sure it's a fake/sticker
        if probs[1] > 0.70:
            return {
                "status": "Fake",
                "reason": f"Physical Structure Anomaly: Potential sticker overlay detected (Confidence: {round(probs[1]*100, 1)}%)."
            }

    # --- LAYER 2: DIGITAL CHECK ---
    data, _, _ = detector.detectAndDecode(img)
    
    if not data:
        # If structure is fine but we can't read it
        return {
            "status": "Safe Structure", 
            "reason": "The physical QR is safe, but no readable URL/data was found inside."
        }

    # URL Check (Levenshtein + ML)
    url_verdict = analyze_url(data)
    
    if "✅ SAFE" in url_verdict:
        return {
            "status": "Safe", 
            "reason": f"Physical structure is genuine and URL is verified: {data}"
        }
    else:
        # Here, the QR looks real, but the website it goes to is dangerous
        return {
            "status": "Fake", 
            "reason": f"Physical structure is safe, but URL is MALICIOUS: {url_verdict}"
        }