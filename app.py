from data_models import db, Author, Book
from datetime import datetime
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'data', 'library.sqlite')}"


db.init_app(app)

@app.route('/', methods = ['GET'])
def home():
    return render_template('index.html')


@app.route('/add_author', methods = ['GET', 'POST'])
def handle_author():
    if request.method == 'POST':
        name = request.form.get('name')
        birth_date = request.form.get('birth_date')
        death_date = request.form.get('date_of_death')

        birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
        if death_date:
            death_date = datetime.strptime(death_date, "%Y-%m-%d").date()
        else:
            death_date = None

        new_author = Author(name=name, birth_date=birth_date, date_of_death=death_date)

        db.session.add(new_author)
        db.session.commit()

        return render_template('add_author.html', message = 'Author added successfully!')
    else:
        return render_template('add_author.html')


@app.route("/add_book", methods = ['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        authors = Author.queery.all()
        title = request.form.get('title')
        isbn = request.form.get('isbn')
        publication_year = request.form.get('publication_year')

        new_book = Book(title=title, isbn=isbn, publication_year=publication_year)

        db.session.add(new_book)
        db.session.commit()

        return render_template('add_book.html', authors=authors, message = 'Book added successfully!')
    else:
        return render_template('add_book.html')




if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)

#with app.app_context():
#  db.create_all()