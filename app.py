from flask import Flask, request, render_template, redirect, session, send_from_directory
from flask_session import Session
from email_validator import validate_email, EmailNotValidError

import hashlib
import os
import uuid
import pathlib

from helpers import error, login_required, allowed_file, return_pages_number, return_products, db, PRODUCTS_PER_PAGE


#CREATE TABLE product ( id INTEGER PRIMARY KEY, name TEXT NOT NULL, image TEXT NOT NULL, description TEXT NOT NULL, price INTEGER, created at DATE DEFAULT (datetime('now','localtime')), updated at DATE DEFAULT (datetime('now','localtime')), user_id INTEGER NOT NULL, categorie_id INTEGER NOT NULL, FOREIGN KEY (categorie_id) REFERENCES categorie(id), FOREIGN KEY (user_id) REFERENCES user(id)  ON DELETE CASCADE);
#CREATE TABLE categorie ( id INTEGER PRIMARY KEY, name TEXT NOT NULL;)
#CREATE TABLE user ( id INTEGER PRIMARY KEY NOT NULL, username TEXT NOT NULL, first_name TEXT NOT NULL, last_name TEXT NOT NULL, email TEXT NOT NULL, password BYTE NOT NULL, created at DATE DEFAULT (datetime('now','localtime')), updated at DATE DEFAULT (datetime('now','localtime')) );


# Configure application
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

# Configuration for upload image
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'media')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Function to check if an extension of input file is valid
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Global Variable to hash passwords, I used hashlib module:
salt = "5gz"

# Route for media : where uploaded images of user.
@app.route('/media/<path:filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

# Search for products : we don't need to register the session because accessible without login
@app.route("/")
def index():

    # We get the q: input of user to search product
    q = request.args.get("q")

    # Counter to track the index of active page
    counter = request.args.get("counter", default = 1, type = int)
    # If there is no input for search and counter == 1 (at first page / offset == 0), we  just rendering template and quering all products
    if q is None and counter == 1:
        all_products = return_products()
        
        # Determine the pages
        pages = return_pages_number(len(all_products))
        products = return_products(pagination=True, offset=0)
        if not products or pages == 1:
            return render_template("index.html", products = products, disabled = "disabled")
        return render_template("index.html", products = products, disabled = "")

   # If not the first page <=> counter != 1, we are using javascript to display and adding products with button more:
    else:

        # If there is an input from user to search:
        if q:

            # Query to display the products that start with the input of user
            all_products = return_products(search=q)
            all_products = db.execute("SELECT * FROM product WHERE name LIKE ''||?||'%'  COLLATE NOCASE ;", q)

            # Determine the pages
            pages = return_pages_number(len(all_products))

            if counter <= pages:

                # Disabled per default
                disabled = ""

                # If the index of active page not equal to total pages, we get rid of disabled in the variable disabled
                if counter == pages:
                    disabled = "disabled"

                # We determine the offset to query the PRODUCTS_PER_PAGE products of the page
                offset = counter * PRODUCTS_PER_PAGE - PRODUCTS_PER_PAGE

                # We pass the index of the next page to use it after in case the user click again on more as parameter in javascript with fetch(url + counter + q) and display again the next PRODUCTS_PER_PAGE products
                counter += 1

                # Query the PRODUCTS_PER_PAGE product of active page
                # products = db.execute("SELECT * FROM product WHERE name LIKE ''||?||'%' COLLATE NOCASE limit ? OFFSET ?;", q, PRODUCTS_PER_PAGE, offset)

                products = return_products(pagination=True, search=q, offset=offset)

            # Content is a dict of objects we need in javascript to display contents
            content = {'products': products, 'counter': counter, 'disabled':disabled}
            return content

        # If not q and we are not in the first page so we display PRODUCTS_PER_PAGE more products of all product
        else:
            all_products = return_products()
            pages = return_pages_number(len(all_products))
            if counter <= pages:
                disabled = ""
                if counter == pages:
                    disabled = "disabled"
                offset = counter * PRODUCTS_PER_PAGE - PRODUCTS_PER_PAGE
                counter += 1
                products = return_products(pagination=True, offset=offset)
                content = {'products': products, 'counter': counter, 'disabled':disabled}
                return content


# Login
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        row = db.execute("SELECT * FROM user WHERE username = ?;", request.form.get("username"))

        # Check if username exist and correct
        if not request.form.get("username"):
            return error("must provide username")
        if not row :
            return error("wrong username")

        # Check if password is correct :
        password = request.form.get("password") + salt
        password = hashlib.md5(password.encode())
        password = password.digest()
        if  password != row[0]["password"]:
            return error("wrong password")

        # Register session
        session["user_id"] = row[0]["id"]

        return redirect("/my-products")

    else:
        return render_template("login.html")


# Check user params
def check_user_params(request):
    first_name = request.form.get('firstname')
    last_name = request.form.get('lastname')
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirmation')

    # Check if all the inputs are filled:
    if not (first_name and last_name and username and email and password and confirm_password):
        return {'status': 'failed', 'message': "input is missing"}

    # Check if username is unique in database:
    user_check_username = db.execute("SELECT * FROM user WHERE username = ? ", username)
    if user_check_username:

        # If user is registred and going to edit his profile
        if session:
            if user_check_username[0]['id'] != session['user_id']:
                return {'status': 'failed', 'message':"username exist"}

        # If user going to register
        else:
            return {'status': 'failed', 'message':"username exist"}

    # Check if email is valid and not in the database
    try:
        validation = validate_email(email, check_deliverability = True)
        email = validation.email
    except EmailNotValidError as e:
        return {'status': 'failed', 'message': str(e)}

    user_check_email = db.execute("SELECT * FROM user WHERE email = ? ", email)
    if user_check_email:
        if session:
            if user_check_email[0]['id'] != session['user_id']:
                return {'status': 'failed', 'message': "email exist"}
        else:
            return {'status': 'failed', 'message': "email exist"}

    # check if passwords matched
    if password != confirm_password :
        return {'status': 'failed', 'message':"passwords don't match"}

    # Adding salt at the last of the password
    salty_password = password + salt

    # Encoding the password
    hashed_password = hashlib.md5(salty_password.encode())
    hashed_password = hashed_password.digest()


    user = {'first_name': first_name, 'last_name': last_name, 'username': username, 'email': email, 'hashed_password': hashed_password}

    return {'status': 'success', 'content': user}

# Register new user
@app.route("/register", methods=["POST","GET"])
def register():
    if request.method == "POST":
        # Register new user in db:

        response_check = check_user_params(request)
        if response_check['status'] == 'failed':
            return error(response_check['message'])
        user = response_check['content']
        db.execute("INSERT INTO user(username,first_name,last_name,email,password)"
                   " VALUES (?,?,?,?,?); ", user['username'],
                   user['first_name'], user['last_name'], user['email'],
                   user['hashed_password'])

        return render_template("login.html")

    else:
        return render_template("register.html")


# My products
    # Display the user products
@app.route ("/my-products", methods=["POST","GET"])
@login_required
def my_products():

    # Counter: to track the index of active page we get it from args.get to determine the offset of the PRODUCTS_PER_PAGE products to display it and track the end of products.
    # We get the counter we can determine the offset of the next PRODUCTS_PER_PAGE products in queries and check if it's the end.
    counter = request.args.get("counter", default = 1, type = int)
    all_products = return_products(session_enabled=True)

    # How much pages of PRODUCTS_PER_PAGE products
    pages = return_pages_number(len(all_products))

    # If the first page, we display the PRODUCTS_PER_PAGE first products and we use jinja in html
    if counter == 1:
        offset = 0
        disabled = ""
        products = return_products(pagination=True, offset=offset, session_enabled=True)
        if not products or pages == 1:
            return render_template("my_products.html", products = products, disabled = "disabled")
        return render_template("my_products.html", products = products, disabled = disabled)

    # If not the first page
    elif counter <= pages:
        disabled = ""

        # We check counter == pages to track the end of products to disable the button.
        if counter == pages:
            disabled = "disabled"
        offset = counter * PRODUCTS_PER_PAGE - PRODUCTS_PER_PAGE


        # We pass always the index of the next page (counter += 1) in the dict content and we use it in "my_products.html" as parameter in href of #button.
        counter += 1
        products = return_products(pagination=True, offset=offset, session_enabled=True)
        content = {'products': products, 'disabled':disabled, 'counter': counter}
        return content


# Function to check product params
def check_product_params(request):
    product_name = request.form.get("product")
    categorie = request.form.get("categorie")
    price = request.form.get("price")
    description = request.form.get("description")
    file = request.files['file']
    if not product_name :
        return {'status': 'failed', 'message':"Product's name is missing"}
    if not categorie:
        return {'status': 'failed', 'message':"A categorie is missing"}
    if not description:
        return {'status': 'failed', 'message':"A description for the product is missing"}
    if not price:
        return {'status': 'failed', 'message':"Product's price is missing"}
    try:
        "{:.2f}".format(float(price))
    except ValueError:
        return {'status': 'failed', 'message':"invalid price format"}

    # Check if the post request has the file part
    if 'file' not in request.files:
        return {'status': 'failed','message':"No file part"}

    # If the user does not select a file, the browser submits an
    # Empty file without a filename.
    if file.filename == '':
        return {'status': 'failed', 'message':"No selected file"}
    
    # Convert price to int
    price = int( float(price) * 100)
    
    # If file exist and valid we are going to load it in folder uploads
    if file and allowed_file(file.filename):
        file_extension = pathlib.Path(file.filename).suffix
        filename = str(uuid.uuid4())+file_extension
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    # Get product categorie id
    categorie_id = db.execute("SELECT id FROM categorie WHERE name = ?;", categorie)
    product = {
        'name': product_name,
        'price': price,
        'description': description,
        'filename': filename,
        'categorie_id': categorie_id[0]['id'],
        }
    return {'status':'sucess', 'content': product}


# Add product
@app.route ("/add-a-product", methods = ["POST","GET"])
@login_required
def add():
    if request.method == "POST":
        response_check = check_product_params(request)
        if response_check['status'] == 'failed':
            return error(response_check['message'])
        product = response_check['content']
        db.execute("INSERT INTO product (name, categorie_id,"
                   "description, image, price, user_id)"
                   "VALUES(?,?,?,?,?,?);",
                   product['name'], product['categorie_id'],
                   product['description'], product['filename'],
                   product['price'], session["user_id"])
        return redirect("/my-products")
    else:
        categories = db.execute("SELECT * FROM categorie;")
        return render_template("add_product.html", categories = categories)


# Edit product
@app.route ("/edit-product", methods=["POST","GET"])
@login_required
def edit_product():
    if request.method == "POST":
        id = request.args.get('id', type = int)
        response_check = check_product_params(request)
        if response_check['status'] == 'failed':
            return error(response_check['message'])
        product = response_check['content']
        db.execute("UPDATE product SET name = ?, categorie_id = ?,"
                "description = ?, image = ?, price = ? "
                "WHERE user_id = ? and id = ?;",
                product['name'], product['categorie_id'],
                product['description'], product['filename'],
                product['price'], session["user_id"],id)
        return redirect("/my-products")
    else:
        # Passing parameters HTTP of previous inputs of users from database in href  = URL in my_products.html
        categories = db.execute("SELECT * FROM categorie;")
        id = request.args.get('id', type = int)
        name_product = request.args.get('name_product')
        description = request.args.get('description')
        price = request.args.get('price')
        image = request.args.get('image')
        categorie_id = request.args.get('categorie_id')
        return render_template("edit_product.html",
            categories = categories,
            id=id,
            name_product=name_product,
            description=description,
            price=int(price),
            image=image,
            categorie_id=categorie_id,
            )


# Delete
@app.route("/delete-product")
@login_required
def delete_product():
    # Delete product from db
    id = request.args.get('id', type = int)
    db.execute("DELETE FROM product WHERE user_id =? AND id =?;", session["user_id"], id)
    return redirect("/my-products")


@app.route("/edit-profile", methods=["POST","GET"])
@login_required
def edit_profile():
    # Edit Profile
    if request.method == "POST":
        response_check = check_user_params(request)
        if response_check['status'] == 'failed':
            return error(response_check['message'])
        user = response_check['content']
        db.execute("UPDATE user SET username = ? ,first_name = ?, last_name = ?,"
                   "email = ?,password = ? WHERE id = ?;", user['username'], user['first_name'],
                     user['last_name'], user['email'], user['hashed_password'],
                     session["user_id"])
        return redirect("/my-products")
    else:
        dict = db.execute("SELECT * FROM user WHERE id = ?;", session["user_id"])
        return render_template("edit_profile.html", dict = dict)


@app.route("/delete-account")
@login_required
def delete_account():
    # Delete user from db
    db.execute("DELETE FROM user WHERE id = ?;", session["user_id"])
    session.clear()
    return redirect("/")


# Logout
@app.route("/logout")
@login_required
def logout():
    # Session clear
    session.clear()
    return redirect("/login")


