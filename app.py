import os

from sqlalchemy.exc import OperationalError, ProgrammingError, IntegrityError, InterfaceError, DatabaseError

from data_models import db, Author, Book
from datetime import datetime
from flask import Flask, render_template, request
from sqlalchemy import create_engine, text

app = Flask(__name__)

# creation of tables didn't work with relative path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'data', 'library.sqlite')}"

db.init_app(app)

#TODO create general query, check whether a button is pressed
# and which one it is, create extra query parameter and add that to the query



@app.route('/', methods=['GET'])
def home():
    """querying all books with respective authors and sending those rows into
    the index.html where they will be looped through"""

    order_by = request.form.get('order')
    if order_by == 'order by title':
        sorting_param = 'ORDER BY title DESC'
        message = 'books ordered by title!'
    elif order_by == 'order by author':
        sorting_param = 'ORDER BY author DESC'
        message = 'books ordered by author!'
    else:
        sorting_param = ''
        message = ''

    query_books_and_authors = f"""SELECT title, name AS author FROM authors JOIN books ON books.author_id = authors.id {sorting_param}"""


    engine = create_engine('sqlite:///data/library.sqlite')
    try:
        with engine.connect() as connection:
            results = connection.execute(text(query_books_and_authors))
            rows = results.fetchall()
            return render_template('index.html', message=message, rows=rows)
    except OperationalError as e:
        print(f"Operational error: {e}")
    except ProgrammingError as e:
        print(f"SQL syntax error: {e}")
    except IntegrityError as e:
        print(f"Integrity error: {e}")
    except InterfaceError as e:
        print(f"Interface error: {e}")
    except DatabaseError as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An error occurred with our database: {e}")
    return render_template('index.html', message='An error occurred with our database!', rows=[])


@app.route('/add_author', methods=['GET', 'POST'])
def handle_author():
    """allows user to add a new author. get request displays the page. user will enter name, birthdate and
    date of death. post request takes in data to create a new author. the author is then added to our database."""
    if request.method == 'POST':
        # getting data from the form
        name = request.form.get('name')
        birth_date = request.form.get('birth_date')
        death_date = request.form.get('date_of_death')

        # dates have to be datetime objects for SQLite to recognize them as dates
        birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
        if death_date:
            death_date = datetime.strptime(death_date, "%Y-%m-%d").date()
        else:
            death_date = None

        # creating new author
        new_author = Author(name=name, birth_date=birth_date, date_of_death=death_date)

        db.session.add(new_author)
        db.session.commit()

        return render_template('add_author.html', message='Author added successfully!')
    else:
        return render_template('add_author.html')


@app.route("/add_book", methods=['GET', 'POST'])
def add_book():
    """allows user to add a new book. get request displays the page. user will enter title, isbn, publication year
    and select an author from the dropdown menu that displays all authors from the authors table. the new book is
    then added to our database."""
    # getting all authors from the database
    authors = Author.query.all()
    if request.method == 'POST':
        # getting data from the form
        title = request.form.get('title')
        isbn = request.form.get('isbn')
        publication_year = request.form.get('publication_year')
        author_id = request.form.get('author_id')

        # creating new book
        new_book = Book(title=title, isbn=isbn, publication_year=publication_year, author_id=author_id)

        db.session.add(new_book)
        db.session.commit()

        return render_template('add_book.html', authors=authors, message='Book added successfully!')
    else:
        return render_template('add_book.html', authors=authors)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)

# with app.app_context():
#  db.create_all()
