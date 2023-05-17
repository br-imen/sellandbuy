# SELL&BUY

## Table of contents:
1. [Description](#description)
2. [Video Demo](#demo)
3. [Usage](#usage)
5. [Technologies used](#technologies)
6. [Installation](#installation)
7. [Implementation](#implementation)
8. [Project status](#status)
9. [Roadmap](#roadmap)
10. [Documentation](#documentation)
12. [Contributing](#contributing)
13. [Authors and acknowledgments](#acknowledgements)


<a name="description"></a>
### Description:
SELL&BUY is a web application where users can sell their creations and buy handmade products.

This project helps:
* the user who practice a hobby, to get an opportunity to sell the production of his practice.
* the user who wants to buy an unique and handmade products.

This is my final project for the certification of CS'50:"Introduction to computer science".

I've got the chance to apply what I've learned from the course. I really enjoyed creating this project.

<a name="demo"></a>
### Video Demo: TODO


<a name="usage"></a>
### Usage:
1. User-flow to sell a handmade product:
    - The user access to the web-app by the URL "#"
    - He should register if not registred before
    - He logs in
    - He already took a photo of the product to add
    - He goes to '/my products'
    - He clicks on button add a product
    - He should add the name of his product, select the categorie and the file picture of product, add a description and a price for his creation and then click on add.
    - He can edit and delete the product
    - He can edit his profile.
    - He can search for products and buy it.

2. User-flow to buy a hand-made product:
    - The user can access to the web-app at URL "#".
    - He search for product
    - He gets a list of products with a picture, price and description.
    - He can choose a product and add it to the basket and buy it. (this feature add to basket and online payment still working on)


- Register:
![register](register.gif)

- Login:
![login](login.gif)


- add-product to sell:
![add_product](add_product.gif)


- edit-delete-product:
![edit_delete_product](edit_delete_product.gif)


- Logout:
![logout](logout.gif)


- edit_profile:
![edit_profile](edit_profile.gif)


- delete_profile:
![delete_profile](delete_profile.gif)


- search to buy:
![search](search.gif)


<a name="technologies"></a>
### Technologies used:
This web application built with a famework Flask 2.2.3 (Python), SQLITE3, Javascript, Bootstrap 5.0.

I choosed these technologies to practice the basics that I got from the course.

I choosed to use CS'50 library to manage the database with row sql queries.

In further steps, the database will be switched to postgresql for more resilient and consistent database.


<a name="installation"></a>
### Installation
To run the app, prepare the environement and install requirements.txt

```
python -m venv venv
```
```
source ven/bin/activate
```
```
pip -r requirements.txt
```
```
flask run
```


<a name="implementation"></a>
### Implementation:

#### 1- project.db:
The database structures has 3 tables.
 * First table to register the user's data, has a relation one to many products: an id primary key , names, email and hashed password
 (bytes type), created at and upadated at.

 * Second table to define categories, has a relation one to many (one categorie has many products) : id of categorie is a primary key, name

 * Third table to insert product's data, has a relation many to one, one user and one categorie to many products, so there is : an id , the user id (a foreign key), categorie id (a foreign key), the filename image, a description and a price in int and dates of create and update. Note: when the user delete his account the product will be deleted too/

To learn more about the schema of database:
```
sqlite3 project.db
```
```
.schema
```

#### 2- app.py:
This is the core of my web application. There is a bunch of imports, some functions and routes.

**The two functions to check inputs:**

- check_user_params:
    - We need it in two routes ("/register") and ("/edit-profile").
    - It should take an input "request" so that we get all inputs and check conditions:
        - All the inputs are filled.
        - the username is unique in database, I use db.execute (from CS50’s library) to query project.db, I configure CS50 library to use SQLite database in helpers.py
        - Email is valid and unique in database, I used email_validator
        - Passwords matched
    - If all checks are passed:
        - The password will be hashed (I used hashlib by adding salt to input and then encoding)
        - An output of a dict with 2 keys-values => key 'status' value 'success' and a key 'content' with value a dict user{} that contains keys-values of all inputs.
    - If wrong inputs :
        - It will return a dict with key 'status' his value 'failed' and key 'message' his value a string contains the message of error will be prompt to user.


- check_product_params:
    - We need it in two routes ("/add_a_product") ("/edit").
    - It takes an input 'request' so that we can get all inputs that describe the new product and checks if the user filled all inputs and then will check:
        - if the price has valid format
        - if filename has an allowed extension with a function allowed_file that takes an input filename and then split the name from the extension and then check if the extension part of the file exist in the set ALLOWED_EXTENSIONS.
    - If all checks passed:
        - convert price to int
        - use a string uuid to get an unique filename -> join the filename to the path to save it (upload)
        - we get the id of the selected categorie from the project.db
        - The function will return a dict product{} that contains key-values of inputs
    - If there is an error:
        - the function return a message of error a string, I create a function error() in helpers.py that prompts the error with a picture of cat.

**Routes:**

- /register:
    - to register new user should support two methods:
      - GET to render_template("register.html")
      - POST to Check the user inputs with the function :
         - If the dict output of check_user_params contains key 'status' with a value "failed" , the function return a string an error(message).
         - If the value of key 'status' == 'success' the function will insert the user's data in database and then return render_template("login.html") to do login.

- /login:
    - support two methods:
        - GET : that render_template("login.html").
        - POST:
            - Check inputs of user are filled and valid by getting the username input and check if exists by query project.db.
            - Check the password if it's correct by adding the salt and then hash it and compare it to the one that exist in project.db.
            - If all checks are passed and no error, the session is registred to remembers the user is logged in by storing user_id, an INTEGER, in session and redirect to the route /my-products
            - If there is an error, will prompt an error(message) to the user.

- /my-products:
    - shows all products of the user logged in. The user can see, add, edit and delete products.
    - The login is required by a decorate function login_required that is in the helpers.py to redirect the user who's not logged in (session is None)
    - Pagination :
        - we calculate total number of page by dividing the number of all products / number of PRODUCTS_PER_PAGE.
        - we calculte the offset with the counter received from the frontend then we incremente it by 1 and pass it again in frontend for the pagination of the next page.
        - If first page:
            - we simply return render_template ("my_products.html", products="list of dict of product's content" and disabled ="") we used jinja to display data in my_products.html.
        - If not the first page:
            - we return dict of new products that will be rendred in the page containing and will be displayed by javascript in frontend on event 'click' button "more" :
                - key 'products' his value is a list of dict of every product with their data

                - key 'disabled' with value that takes space "" if there is more and takes a string "disabled" if it's the end of products to disable the button tag more

                - key 'counter' with an int value that references to the next page: on click of button more, it will await for response.json() so that we can get more products  to display and If there is no more products:
                    - key 'disabled' should have the value "disabled" to disable the button.
    - In my-product.html:
        - click on edit: will direct you to route /edit

        - click on add a product: will direct you to route /add-a-product
        - click on delete: will direct you to route /delete

- /add-a-product:
    - login is required
    - support two methods:
        - GET :
            - will render_template "add_product.html" and will get all categories from the table categories in project.db and pass it in render_template and we use jinja in add_product.html to display categories in select tag.
        - POST :
            - will check all inputs with the function check_product_params(request).
                - if passed and no errors, we insert in project.db product's data and then redirect to /my-products.
- /edit:
    - login is required
    - Supports two methods:
    - GET:
        - we get parameters HTTP of products data that is filled in attribute href of <a> tag edit in my_products.html and that is passed to the edit.html by the attribute of action in form tag <form action ="/edit?id={{product.id}}&name_product={{product.name}}&description={{product.description}}&price={{product.price}}&image={{product.image}}&categorie_id={{product.categorie_id}}"...> so that we can get previous data with request.args.get() and render_template("edit.html", variables = previous values) and display it with jinja so that the user know what he putted previously and what he wants to change.
    - POST:
        - we get the changes that the users made. we check always with the function check_product_params and then we do updates in project.db and redirect to the route /my-products to display all the products and see his changes.


- /delete:
    - this route to delete the product from the project.db
    - we get the id of product from the HTTP params and execute the query delete of product then return redirect /my-products


- /edit-profile:
    - support two methods
    - login is required
    - GET:
        - will get data of user from the database and render_template("edit_profile.html", dict = dict)
    - POST:
        - will check inputs with check_user_params(request) and if pass all checks, It will execute the update in database and return redirect to /my-products

    - In edit_profile.html in templates folder:
        - If the user click on delete profile will direct to the route /delet-account.

- /logout:
    - login required
    - session will be clear
    - return redirect to /login


- /delete-account :
    - Support GET
    - Login required
    - Will delete the user from database with his products
    - Session clear
    - Then redirect to the index route / wich is where the user can do the search to buy products.


- /:
    - the index page is where the user can do the search.
    - Login isn't required.
    - If the  user type for something:
        we will display products that start with the input of the user.
    - If the user doesn't type for search:
        will display all products.

<a name="status"> </a>
### Project status:
Work in progress

<a name="roadmap"> </a>
### Roadmap:
In my project there is fixes to do and I'm still completing the feature online payment:

1- payment system

2- unit tests

3- use postgresql in database

4- use ORM SQLAlchemy

5- use builtin pagination

6- fix validation errors will redirect to the form page after and it's better to do real time validation errors with javascript

7- add owner username to the product

8- add an username in nav

9- filter in search

10- add icons to edit and delete

11- enhance product's photo display

12- the footer in html sticks in buttom

13- improve  ux/ui of web application.

14- a Mobile app.



-------------------------------NOW-----------------------------------------


1- change /edit to /edit-product and /delete to delete-product
4- deploiement


<a name="documentation"></a>
### Documentation
To learn about sessions and basics of flask:

https://flask.palletsprojects.com/en/2.3.x/

Sqlite:

https://www.sqlite.org/index.html

The CS'50 SQL library:

https://cs50.readthedocs.io/libraries/cs50/python/?getting-started/introduction/highlight=sqlite#cs50.SQL

Validate email:

https://pypi.org/project/email-validator/

Hash-password tutorial hashlib:

https://pythonprogramming.net/password-hashing-flask-tutorial/

Hashlib:

https://docs.python.org/3/library/hashlib.html

How to upload files:

https://flask.palletsprojects.com/en/2.2.x/patterns/fileuploads/

To get an unique filname in uploads image:

https://www.npmjs.com/package/uuid

Bootstrap 5.0:

https://getbootstrap.com/docs/5.0/

To write README.md:

https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax


<a name="contributing"> </a>
### Contributing
Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.


<a name=" acknowledgments"></a>
### Authors and acknowledgments
Thank you for all CS50.

CS50 is an open course from Havard University and taught by David J. Malan
