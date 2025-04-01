from data_models import db, Author, Book
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'data', 'library.sqlite')}"


db.init_app(app)

@app.route("/", methods = ['GET'])
def home():
    return render_template("home.html")


@app.route("/add_author", methods = ['GET', 'POST'])
def handle_author():
    if request.method == 'POST':

    else:
        return render_template("add_author.html")


@app.route("/add_book", methods = ['GET', 'POST'])
def add_book():



#with app.app_context():
#  db.create_all()