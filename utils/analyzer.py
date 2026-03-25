import cv2
import pickle
import os
from utils.qr_features import get_qr_features
from utils.url_analyzer import analyze_url

# Load QR Model
try:
    qr_model = pickle.load(open("models/qr_model.pkl", "rb"))
except:
    qr_model = None

detector = cv2.QRCodeDetector()

def analyze_qr(path, fallback_text=None):
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
    else:
        # Patch: Model missing -> fail safe
        return {"status": "Fake", "reason": "System Error: QR Security Model is currently unavailable."}

    # --- LAYER 2: DIGITAL CHECK ---
    data, _, _ = detector.detectAndDecode(img)
    
    # Advanced Backend Decoding Fallbacks (for dense, GPay, or blurry QRs)
    if not data:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        data, _, _ = detector.detectAndDecode(gray)
        
    if not data:
        # Increase contrast
        alpha = 1.5 # Contrast control
        beta = 0    # Brightness control
        adjusted = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)
        data, _, _ = detector.detectAndDecode(adjusted)
        
    if not data:
        # Otsu's thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        data, _, _ = detector.detectAndDecode(thresh)
        
    if not data and fallback_text:
        data = fallback_text
        
    if not data:
        # If structure is fine but we can't read it natively or via fallback
        return {
            "status": "Safe Structure", 
            "reason": "The physical QR is safe, but no readable URL/data was found inside."
        }
        
    # URL Check (Levenshtein + ML)
    # Redirect to UPI parser for payment QRs
    if data.lower().startswith("upi://pay") or "pa=" in data.lower():
        from utils.upi_analyzer import analyze_upi
        upi_verdict = analyze_upi(data)
        
        # Determine status prefix from UPI module
        status = upi_verdict["status"]
        if status == "Fake":
            prefix = "❌ FRAUD:"
        elif status == "Safe":
            prefix = "✅ SAFE:"
        else:
            prefix = "⚠️ WARNING:"
            
        return {
            "status": status,
            "reason": f"Physical structure is safe. {prefix} {upi_verdict['reason']}",
            "upi_details": upi_verdict.get("upi_details")
        }

    url_verdict = analyze_url(data)
    
    if "✅ SAFE" in url_verdict:
        return {
            "status": "Safe", 
            "reason": f"Physical structure is genuine and URL is verified: {data}",
            "url_data": data
        }
    else:
        # Here, the QR looks real, but the website it goes to is dangerous
        return {
            "status": "Fake", 
            "reason": f"Physical structure is safe, but URL is MALICIOUS: {url_verdict} ({data})",
            "url_data": data
        }