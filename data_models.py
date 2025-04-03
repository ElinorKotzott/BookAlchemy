from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Date, Integer, ForeignKey

db = SQLAlchemy()


class Author(db.Model):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    birth_date = Column(Date)
    date_of_death = Column(Date)


    def __str__(self):
        """represents instance of author as a string"""
        representation = f"{self.name}, id: {self.id}, born in {self.birth_date}"
        if self.date_of_death:
            representation = representation + f", died in {self.date_of_death}"
        return representation


class Book(db.Model):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, autoincrement=True)
    isbn = Column(String)
    title = Column(String)
    publication_year = Column(Integer)
    author_id = Column(Integer, ForeignKey("authors.id", ondelete="CASCADE"), nullable=False)


    def __str__(self):
        """represents instance of book as a string"""
        return (f"{self.id}, id: {self.id}, isbn: {self.isbn}, title: '{self.title}', published "
                f"in: {self.publication_year}, author_id: {self.author_id}")
