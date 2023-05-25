from cs50 import SQL
from flask import redirect, render_template, request, session
from functools import wraps
import math

# Variable for how many products to display per page
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
    x = '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    if not x:
        return {'status':'failed','message':"Not allowed extension"}
    return x

# Function that gives how many pages in total : total products / number of products per page
def return_pages_number(products_length, product_by_page=PRODUCTS_PER_PAGE):
    return math.ceil(products_length / product_by_page)

# Function that query the database in depends of many paramaters
def return_products(pagination=False, counter=1, search=None, offset=None, session_enabled=False):
    user_id_q = ""
    pagination_q = ""
    search_q = ""

    # If there is a session we add to query the user_id
    if session_enabled:
        user_id_q = f"WHERE user_id = {session['user_id']}"

    # If there is pages to display we add the limit and the offset
    if pagination:
        pagination_q = f"limit {PRODUCTS_PER_PAGE} OFFSET {offset}"

    # If there is an input we add to query the input for search.
    if search:
        search_q = f"WHERE name LIKE ''||'{search}'||'%' COLLATE NOCASE"

    # Then we return the query.
    return db.execute(f"SELECT * FROM product {user_id_q} {search_q} {pagination_q};")