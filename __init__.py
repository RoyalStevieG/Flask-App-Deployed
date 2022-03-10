from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import json
import urllib3

app = Flask(__name__)
with open("/etc/config.json") as config_file:
    config = json.load(config_file)
app.config["SECRET_KEY"] = config.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = config.get("SQLALCHEMY_DATABASE_URI")
app.config["UPLOAD_FOLDER"] = "static\product_images"
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
from flask_app import routes
