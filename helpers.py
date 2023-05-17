from cs50 import SQL
from flask import redirect, render_template, request, session
from functools import wraps
import math


PRODUCTS_PER_PAGE = 9

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")

# Function to display the cat error for the user
def error(message):
    return render_template("error.html", erreur = message)


# Login_required
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# Function to check if an extension of input file is valid
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def return_pages_number(products_length, product_by_page=PRODUCTS_PER_PAGE):
    return math.ceil(products_length / product_by_page)


def return_products(pagination=False, counter=1, search=None, offset=None, session_enabled=False):
    user_id_q = ""
    pagination_q = ""
    search_q = ""

    if session_enabled:
        user_id_q = f"WHERE user_id = {session['user_id']}"

    if pagination:
        pagination_q = f"limit {PRODUCTS_PER_PAGE} OFFSET {offset}"

    if search:
        search_q = f"WHERE name LIKE ''||'{search}'||'%' COLLATE NOCASE"

    return db.execute(f"SELECT * FROM product {user_id_q} {search_q} {pagination_q};")