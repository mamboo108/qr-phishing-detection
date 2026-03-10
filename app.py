from flask import Flask, render_template, request
import os
from analyzer import analyze_qr

# 1. Initialize the Flask application
app = Flask(__name__)

# 2. Ensure the uploads folder exists
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 3. Define the routes
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
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        # Get the detailed result dictionary from your analyzer
        # This will follow your: Structure -> URL logic
        report = analyze_qr(path)
        
        # Pass the report dictionary to result.html
        return render_template("result.html", report=report)

    return render_template("index.html")

# 4. Run the app
if __name__ == "__main__":
    app.run(debug=True)