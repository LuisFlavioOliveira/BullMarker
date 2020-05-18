import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    
    
    return apology("TODO")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Call the function lookup to check if it's a valid symbol
        quote = lookup(request.form.get("symbol"))

        # Gets stocks symbol, stocks current price and how many shares he wants to buy
        stock_symbol = quote["symbol"]
        current_price = quote["price"]
        shares = int(request.form.get("shares"))

        # If the user don't type anything on the "symbol" field
        if not request.form.get("symbol"):
            return apology("Stock Symbol invalid.")

        # If the users type in a symbol that don't exist
        elif quote == None:
            return apology("Stock Symbol doesn't exist.")

        # If the user don't type anything on the "shares" field
        if not request.form.get("shares"):
            return apology("You must type a number of shares that you want buy.")

        # If the user don't type a non positive number
        elif shares < 1:
            return apology("The value must be equal or superior to 1")

        # Gets user's current amount of cash
        users_cash = db.execute(
            "SELECT cash FROM users WHERE id = ?", session["user_id"]
        )

        # Do the calcul of the current price of stoks * the shares the user wants to buy
        total = current_price * shares

        # If the user doesn't have enoigh cash to buy it, return an error
        if total > users_cash[0]["cash"]:
            return apology("You don't have enough cash to buy it.")

        else:
            # Subtract user's cash with the price of the shares and store it into a variable
            new_cash = users_cash[0]["cash"] - total
            # Query the database to update users current amount of cash
            db.execute(
                "UPDATE users SET cash = ? WHERE id = ?", new_cash, session["user_id"],
            )
            # Insert into the table "wallet" the number of stocks the user bought, its symbol, price and time
            db.execute(
                "INSERT INTO wallet (user_id, symbol, shares, price, time) VALUES (?, ?, ?, ?, datetime('now', 'localtime'))",
                session["user_id"],
                stock_symbol,
                shares,
                total,
            )
            return redirect("/buy")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Run lookup function to get the informations about the stock. The return value of function
        # lookup is a dictionary with where the keys are 'Name', 'Symbol' and 'Price'
        quote = lookup(request.form.get("symbol"))

        # If users tap an invalid symbol, return an error message
        if quote == None:
            return apology("invalid symbol", 403)

        # If users gave a valid symbol
        else:
            # Call the usd function price to transform the price in US Dollars and store it into 'value'
            value = usd(quote["price"])
            # Render the template to print to the user the informations about the quote
            return render_template(
                "quoted.html", name=quote["name"], symbol=quote["symbol"], price=value
            )

    # Request method = GET
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # if not username provided, return error
        if not request.form.get("username"):
            return apology("must provide a name for register", 403)

        # Check if there isn't other identical username on the database
        # the result will be stored in roll
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username"),
        )
        # If the len of the row is equal to 0, that means the username the user gave is unique
        # otherwise, if the len is equal to 1, that means the username already exists on the database
        if len(rows) == 1:
            return apology("username already taken, try another one!", 403)

        # Ensure user typed a password
        if not request.form.get("password"):
            return apology("you must provid a valid password.", 403)

        # Ensure user typed the confirmation of the password
        if not request.form.get("confirmation"):
            return apology("you must confirm your password.", 403)

        # If password and confirmation don't match, accuse error
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("the passwords don't match. Try again", 403)

        else:
            # Hashes password before storying it into the database
            pass_hash = generate_password_hash(
                request.form.get("password"), method="pbkdf2:sha256", salt_length=8
            )

            # Store usersname and password into database
            new_user = db.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)",
                request.form.get("username"),
                pass_hash,
            )

            # Start a session for the user after register
            session["user_id"] = new_user

            # Display a flash message that the registration occured
            flash("Registered!")

            return redirect("/")

    # Request method = GET
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    return apology("TODO")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
