import os
from data_models import db, Author, Book
from datetime import datetime
from flask import Flask, render_template, request
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError, IntegrityError, InterfaceError, DatabaseError

app = Flask(__name__)

# creation of tables didn't work with relative path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'data', 'library.sqlite')}"

db.init_app(app)

#global variable to be able to save search for ordering
latest_search_term = ''

@app.route('/', methods=['GET'])
def home():
    """Checking whether one of the ordering buttons has been pressed and adding ordering logic
    to the query with the sorting_param. Querying and sending those rows into the index.html
    where they will be looped through. the latest search term exists so that the search term will
    still be considered (and not reset to empty string) if the user decides to order right after searching"""

    global latest_search_term

    sorting_param = ''
    searching_param = ''
    params = {}
    message = ''

    if not Book.query.all() and not Author.query.all():
        message = 'No books or authors available in the database!'

    order_by = request.args.get('order', '')

    if order_by == 'order by title':
        sorting_param = 'ORDER BY title ASC'
        message = 'Books ordered by title!'
    elif order_by == 'order by author':
        sorting_param = 'ORDER BY author ASC'
        message = 'Books ordered by author!'

    # getting search term from URL
    search_term = request.args.get('search')
    if search_term is not None:
        search_term = search_term.strip()

    if search_term is None:
        if latest_search_term:
            searching_param = "WHERE title LIKE :latest_search_term OR author LIKE :latest_search_term"
            params["latest_search_term"] = f"%{latest_search_term}%"
        else:
            searching_param = ''
            params = {}
    elif search_term == '':
        latest_search_term = ''
        searching_param = ''
        params = {}
    else:
        latest_search_term = search_term
        searching_param = "WHERE title LIKE :latest_search_term OR author LIKE :latest_search_term"
        params["latest_search_term"] = f"%{latest_search_term}%"

    #different additions to the query depending on whether searching param and query param exist
    if searching_param and sorting_param:
        query = f"{searching_param} {sorting_param}"
    elif searching_param:
        query = f"{searching_param}"
    elif sorting_param:
        query = f"{sorting_param}"
    else:
        query = ""

    print(search_term, latest_search_term)

    rows = get_authors_and_books_from_database(query, params)

    if search_term and not rows:
        message = 'No results found to match your search!'

    if sorting_param and not rows:
        message = 'No results to order!'

    return render_template('index.html', message=message, rows=rows)


def get_authors_and_books_from_database(query, params):
    """helper method that takes the last part of the query (query) and the latest search term as 'param'.
    it returns the result of the query if the query goes well, otherwise it returns an empty list"""
    query_books_and_authors = f"""SELECT books.title, authors.name AS author, books.id, books.isbn
    FROM authors JOIN books ON books.author_id = authors.id {query}"""

    engine = create_engine('sqlite:///data/library.sqlite')
    try:
        with engine.connect() as connection:
            results = connection.execute(text(query_books_and_authors), params)
            rows = results.fetchall()
            return rows
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
    return []


@app.route('/add_author', methods=['GET', 'POST'])
def handle_author():
    """allows user to add a new author. get request displays the page. user will enter name, birthdate and
    date of death. post request takes in data to create a new author. the author is then added to our database."""
    message = ''
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
        message = 'Author added successfully!'
        db.session.add(new_author)
        db.session.commit()

    return render_template('add_author.html', message=message)


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    """allows user to add a new book. get request displays the page. user will enter title, isbn, publication year
    and select an author from the dropdown menu that displays all authors from the authors table. the new book is
    then added to our database."""
    # getting all authors from the database
    message = ''
    global latest_search_term
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
        message = 'Book added successfully!'
        # resetting latest_search_term, because otherwise only books including the latest search will be shown when going back to home
        latest_search_term = ''

    return render_template('add_book.html', authors=authors, message=message)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete(book_id):
    book = Book.query.get(book_id)
    author_id = book.author_id

    if not book:
        message = 'Book not found!'
    else:
        db.session.delete(book)
        db.session.commit()
        message = 'Book deleted successfully!'
        books_by_the_same_author = Book.query.filter(Book.author_id == author_id).all()
        if not books_by_the_same_author:
            author = Author.query.get(author_id)
            db.session.delete(author)
            db.session.commit()
            message = 'Book deleted successfully. Author deleted as well because no other books from this author are available!'

    return render_template('index.html', message=message, rows=get_authors_and_books_from_database('', {}))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)

# with app.app_context():
#  db.create_all()
