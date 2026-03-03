from flask import Flask, render_template, request
from url_analyzer import analyze_url

app = Flask(__name__)

@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]
        result = analyze_url(url)
        return render_template("urlresult.html", result=result)
    return render_template("urlindex.html")

if __name__ == "__main__":
    app.run(debug=True)