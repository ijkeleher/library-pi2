from flask import Flask, Blueprint, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os, requests, json
from flask import current_app as app

api = Blueprint("api", __name__)

db = SQLAlchemy()
ma = Marshmallow()

# Declaring the model.
class Book(db.Model):
    __tablename__ = "Book"
    BookID = db.Column(db.Integer, primary_key = True, autoincrement = True)
    Title = db.Column(db.Text)
    Author = db.Column(db.Text)
    PublishedDate = db.Column(db.Text)
    # Username = db.Column(db.String(256), unique = True)
    def __init__(self, Title, Author, PublishedDate, BookID = None):
        self.BookID = BookID
        self.Title = Title
        self.Author = Author
        self.PublishedDate = PublishedDate

class BookSchema(ma.Schema):
    # Reference: https://github.com/marshmallow-code/marshmallow/issues/377#issuecomment-261628415
    def __init__(self, strict = True, **kwargs):
        super().__init__(strict = strict, **kwargs)
    
    class Meta:
        # Fields to expose.
        fields = ("BookID", "Title", "Author", "PublishedDate")

bookSchema = BookSchema()
booksSchema = BookSchema(many = True)

# Endpoint to show all books.
@api.route("/book", methods = ["GET"])
def getPeople():
    books = Book.query.all()
    result = booksSchema.dump(books)

    return jsonify(result.data)

# Endpoint to get a single book by id.
@api.route("/book/<id>", methods = ["GET"])
def getBook(id):
    book = Book.query.get(id)

    return bookSchema.jsonify(book)

# Endpoint to create new book.
@api.route("/book", methods = ["POST"])
def addBook():
    title = request.json["title"]
    author = request.json["author"]
    publisheddate = request.json["publisheddate"]

    newBook = Book(Title = title, Author=author, PublishedDate=publisheddate)

    db.session.add(newBook)
    db.session.commit()

    return bookSchema.jsonify(newBook)

# Endpoint to update book.
@api.route("/book/<id>", methods = ["PUT"])
def bookUpdate(id):
    book = Book.query.get(id)
    title = request.json["title"]
    author = request.json["author"]
    publisheddate = request.json["publisheddate"]

    book.Title = title
    book.Author = author
    book.PublishedDate = publisheddate

    db.session.commit()

    return bookSchema.jsonify(book)

# Endpoint to delete book.
@api.route("/book/<id>", methods = ["DELETE"])
def bookDelete(id):
    book = Book.query.get(id)

    db.session.delete(book)
    db.session.commit()

    return bookSchema.jsonify(book)
