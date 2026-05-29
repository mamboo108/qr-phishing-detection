import os
import html
import base64
import uuid
from flask import render_template, request, jsonify
from app import app
from utils.analyzer import analyze_qr
from utils.url_analyzer import analyze_url

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")



@app.route("/api/scan", methods=["POST"])
def api_scan():
    data = request.json.get("image", "")
    text_data = request.json.get("text", None)
    
    if not data:
        return jsonify({"status": "Error", "reason": "No image provided"})
        
    if data.startswith("data:image"):
        data = data.split(",")[1]
    
    filename = str(uuid.uuid4()) + ".png"
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        with open(path, "wb") as fh:
            fh.write(base64.b64decode(data))
    except Exception as e:
        return jsonify({"status": "Error", "reason": "Invalid image format"})
        
    report = analyze_qr(path, text_data)
    
    # Clean up the temporary file immediately after processing
    if os.path.exists(path):
        os.remove(path)
        
    if "reason" in report:
        report["reason"] = html.escape(report["reason"])
        
    return jsonify(report)
