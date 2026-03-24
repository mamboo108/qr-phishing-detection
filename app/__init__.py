import os
from flask import Flask

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "uploads"

# Ensure the uploads folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

from app import routes
