from flask import Flask,render_template,request
import os
from analyzer import analyze_qr

app = Flask(__name__)
os.makedirs("uploads",exist_ok=True)

@app.route("/",methods=["GET","POST"])
def index():
    if request.method=="POST":
        file = request.files["qr"]
        path = os.path.join("uploads",file.filename)
        file.save(path)

        result = analyze_qr(path)
        return render_template("result.html",result=result)

    return render_template("index.html")

app.run(debug=True)