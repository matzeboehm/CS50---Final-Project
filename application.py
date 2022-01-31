import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from PIL import Image
from functools import wraps
import random

# Configure application
app = Flask(__name__)
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'super secret key'

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
UPLOAD_FOLDER = "/receipts/pictures"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# Database
db = SQL("sqlite:///recipes.db")

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


###############################################################################
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


@app.route("/")
@login_required
def home():
    user_id = session.get("user_id")
    name = db.execute("SELECT name FROM users WHERE id = (?)", user_id)[0]["name"]

    amount_recipes = int(db.execute("SELECT COUNT (*) FROM receipts")[0]["COUNT (*)"])
    recipe_id = random.randint(1, amount_recipes)

    name_recipe = db.execute("SELECT name FROM receipts WHERE id = (?)", recipe_id)[0]["name"]

    return render_template("index.html", name=name, recipe_id=recipe_id, name_recipe=name_recipe)

@app.route("/receipt")
def receipt():
    query = request.args.get("q")

    name = db.execute("SELECT name FROM receipts WHERE id = (?)", query)[0]["name"]

    picture = "static/pictures/" + str(query) + ".jpg"
    with open("static/ingredients/" + str(query) + "_ingredients.txt", "r") as infile:
        ingredients_in = infile.readlines()
        ingredients = []
        for row in ingredients_in:
            ingredients.append(row.strip().strip("-"))

    with open("static/instructions/" + str(query) + "_instructions.txt", "r") as infile:
        instructions_in = infile.readlines()
        instructions = []
        for row in instructions_in:
            instructions.append(row.strip().strip("-"))

    return render_template("receipt.html", name=name, picture=picture, ingredients=ingredients, instructions=instructions)

@app.route("/receiptOverview")
@login_required
def receiptOverview():
    receipts_py = db.execute("SELECT * FROM receipts")

    receipts_export = []

    for row in receipts_py:
        temp = []
        temp.append(row["id"])
        temp.append(row["name"])
        if row["cookingTime"] != None:
            temp.append(row["cookingTime"])
        else:
            temp.append("")
        receipts_export.append(temp)

    return render_template("receiptOverview.html", receipts_export=receipts_export)

def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/generateReceipt", methods=["GET", "POST"])
@login_required
def generateReceipt():
    if request.method == "POST":
        name = request.form.get("name")
        picture = request.form.get("file")
        ingredients = request.form.get("ingredients")
        instructions = request.form.get("instructions")
        cookingTime = request.form.get("cookingTime")

        # Insert into database
        if name:
            if cookingTime:
                db.execute("INSERT INTO receipts (name, cookingTime) VALUES (?, ?)", name, cookingTime)
            else:
                db.execute("INSERT INTO receipts (name) VALUES (?)", name)

            id = db.execute("SELECT id FROM receipts WHERE name = (?)", name)[0]["id"]
        else:
            return redirect("/receiptOverview")

        # Handle picture and save file
        file = request.files["picture"]
        if file.filename != "":
            file.save(file.filename)
            os.rename(file.filename, "static/pictures/" + str(id) + ".jpg")

        # Handle ingredients txt
        if ingredients:
            with open("static/ingredients/" + str(id) + "_ingredients.txt", "w") as file:
                file.write(ingredients)

        # Handle instructions txt
        if instructions:
            with open("static/instructions/" + str(id) + "_instructions.txt", "w") as file:
                file.write(instructions)

        return redirect("/receiptOverview")
    else:
        # render html site
        return render_template("generateReceipt.html")


@app.route("/shoppingcart", methods=["GET", "POST"])
@login_required
def shoppingcart():
    if request.method == "POST":
        # returns a list of all names that were selected
        selected_names = request.form.getlist("name")

        # generate a dict of all ingredients needed based on going through ingredient list and add volume to it
        ingredientDict = {}

        for name in selected_names:
            # get id from database
            id_db = db.execute("SELECT id FROM receipts WHERE name = (?)", name)[0]["id"]
            with open("static/ingredients/" + str(id_db) + "_ingredients.txt", "r") as file:
                ingredients_in = file.readlines()
                ingredients = []
                for row in ingredients_in:
                    temp = row.strip().strip("-")
                    temp = temp.split()

                    if temp[2] in ingredientDict:
                        ingredientDict[temp[2]] = ingredientDict[temp[2]] + int(temp[0])
                    else:
                        ingredientDict[temp[2]] = int(temp[0])

        ingredientList = []
        for ingredient, mass in ingredientDict.items():
            temp = []
            temp.append(ingredient)
            temp.append(mass)
            ingredientList.append(temp)


        return render_template("shoppinglist.html", ingredientList=ingredientList)
    else:
        names_db = db.execute("SELECT id, name FROM receipts")
        names = []
        for name in names_db:
            temp = []
            temp.append(name["id"])
            temp.append(name["name"])
            names.append(temp)

        return render_template("shoppingcart.html", names=names)

#########################################
## insert login required at some point ##
##########################################
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # This code has been mostly copied by problem set 9 of CS50
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return redirect("/login")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return redirect("/login")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE name = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        # For now
        return render_template("login.html", error=1)



        # Ensure username and password were submitted and that confirmation matches password
        if not request.form.get("username"):
            return redirect("/")
        elif not request.form.get("password") or not request.form.get("confirmation"):
            return redirect("/")
        elif request.form.get("password") != request.form.get("confirmation"):
            return redirect("/")
        elif db.execute("SELECT COUNT(*) FROM users WHERE name=(?)", request.form.get("username"))[0]['COUNT(*)'] == 1:
            return redirect("/")

        # hash password and add to database
        hashed_password = generate_password_hash(request.form.get("password"))
        db.execute("INSERT INTO users (name, hash) VALUES (?, ?)", request.form.get("username"), hashed_password)

        hashed_password = None
        return render_template("login.html", registered=1)

    else:

        # For now
        return render_template("login.html", error=1)


        return render_template("register.html")