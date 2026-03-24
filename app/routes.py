import os
import html
import base64
import uuid
from flask import render_template, request, jsonify
from app import app
from utils.analyzer import analyze_qr
from utils.url_analyzer import analyze_url

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Check if the file was actually uploaded
        if 'qr' not in request.files:
            return "No file part in the request"
            
        file = request.files["qr"]
        
        if file.filename == '':
            return "No file selected"

        # Save the file to the uploads folder
        path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(path)

        # Get the detailed result dictionary from your analyzer
        report = analyze_qr(path)
        
        # Sanitize reason output to prevent XSS manually, just in case template isn't doing it.
        # Although Jinja auto-escapes, double sanitizing or preparing for safe rendering:
        if "reason" in report:
            report["reason"] = html.escape(report["reason"])

        # Pass the report dictionary to result.html
        return render_template("result.html", report=report)

    return render_template("index.html")

@app.route("/url", methods=["GET", "POST"])
def url_index():
    result = None
    if request.method == "POST":
        url = request.form.get("url")
        if url:
            result = analyze_url(url)
            # Sanitize result to prevent XSS
            result = html.escape(result)
    return render_template("urlindex.html", result=result)

@app.route("/api/scan", methods=["POST"])
def api_scan():
    data = request.json.get("image", "")
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
        
    report = analyze_qr(path)
    
    # Optional cleanup of the file if not needed:
    # os.remove(path)
    
    if "reason" in report:
        report["reason"] = html.escape(report["reason"])
        
    return jsonify(report)
