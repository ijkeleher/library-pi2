from flask import Flask, Blueprint, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os, requests, json
from flask import current_app as app

api = Blueprint("api", __name__)

db = SQLAlchemy()
ma = Marshmallow()

# Declaring the model.

# LmsUser class for the users of the library system

class LmsUser(db.Model):
    __tablename__= "LmsUser"
    LmsUserID = db.Column(db.Integer, primary_key = True, autoincrement = True)
    UserName = db.Column(db.String(256), unique = True)
    Name = db.Column(db.Text)
    def __init__(self, UserName, Name, LmsUserID = None):
        self.LmsUserID = LmsUserID
        self.UserName = UserName
        self.Name = Name

class LmsUserSchema(ma.Schema):
    def __init__(self, strict = True, **kwargs):
        super().__init__(strict = strict, **kwargs)
    
    class Meta:
        # Fields to expose.
        fields = ("LmsUserID", "Name", "UserName")

lmsUserSchema = LmsUserSchema()
lmsUsersSchema = LmsUserSchema(many = True)


# This class is for the book db

class Book(db.Model):
    __tablename__ = "Book"
    BookID = db.Column(db.Integer, primary_key = True, autoincrement = True)
    Title = db.Column(db.Text)
    Author = db.Column(db.Text)
    PublishedDate = db.Column(db.Text)
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

#######################
# FETCH ENDPOINTS
#######################

# Endpoint to show all books.
@api.route("/book", methods = ["GET"])
def getBooks():
    books = Book.query.all()
    result = booksSchema.dump(books)

    return jsonify(result.data)

# Endpoint to show all users
@api.route("/user", methods = ["GET"])
def getUsers():
    users = LmsUser.query.all()
    result = lmsUsersSchema.dump(users)

    return jsonify(result.data)

# Endpoint to get a single book by id.
@api.route("/book/<id>", methods = ["GET"])
def getBook(id):
    book = Book.query.get(id)

    return bookSchema.jsonify(book)

# Endpoint to get a single user by id.
@api.route("/user/<id>", methods = ["GET"])
def getUser(id):
    user = LmsUser.query.get(id)

    return lmsUserSchema.jsonify(user)

#######################
# INSERTION ENDPOINTS
#######################

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

# Endpoint to create a new user.
@api.route("/user", methods = ["POST"])
def addUser():
    username = request.json["username"]
    name = request.json["name"]

    newLmsUser = LmsUser(UserName = username, Name=name)

    db.session.add(newLmsUser)
    db.session.commit()

    return lmsUserSchema.jsonify(newLmsUser)

#######################
# UPDATE ENDPOINTS
#######################

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

# Endpoint to update a user.
@api.route("/user/<id>", methods = ["PUT"])
def userUpdate(id):
    lmsUser = LmsUser.query.get(id)

    username = request.json["username"]
    name = request.json["name"]

    lmsUser.UserName = username
    lmsUser.Name = name

    db.session.commit()

    return bookSchema.jsonify(lmsUser)

#######################
# DELETION ENDPOINTS
#######################

# Endpoint to delete book.
@api.route("/book/<id>", methods = ["DELETE"])
def bookDelete(id):
    book = Book.query.get(id)

    db.session.delete(book)
    db.session.commit()

    return bookSchema.jsonify(book)

# Endpoint to delete a user.
@api.route("/user/<id>", methods = ["DELETE"])
def userDelete(id):
    lmsUser = LmsUser.query.get(id)

    db.session.delete(lmsUser)
    db.session.commit()

    return bookSchema.jsonify(lmsUser)
