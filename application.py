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

    # Get user's current amount of cash
    users = db.execute(
        "SELECT cash FROM users WHERE id = :user_id", user_id=session["user_id"]
    )

    # Get the information from the user's wallet. Db.execute returns a list of dictionaries.
    stocks = db.execute(
        "SELECT symbol, name, SUM(shares) as total_shares FROM wallet WHERE user_id = ? GROUP BY symbol HAVING total_shares > 0",
        session["user_id"],
    )

    # Create a dictionary where the keys are the stocks symbols and the values are the dictionary
    # that function lookup returns (i.e. {'AAPL': {'name': 'Apple, Inc.', 'price': 307.71, 'symbol': 'AAPL'} )
    quotes = {}

    # Call the lookup function and populate the dictionary with the informations about the stocks
    # and to get the total value of all the stocks price * shares
    total_stocks = 0
    for stock in stocks:
        quotes[stock["symbol"]] = lookup(stock["symbol"])
        total_stocks += quotes[stock["symbol"]]["price"] * stock["total_shares"]

    # Store in a variable the remaining amount of cash that the user has
    total = users[0]["cash"]

    # Calculate the total of cash that users has counting stocks + cash in the wallet
    total_cash = total_stocks + total

    return render_template(
        "wallet.html", quotes=quotes, stocks=stocks, total=total, total_cash=total_cash,
    )


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Call the function lookup to check if it's a valid symbol
        quote = lookup(request.form.get("symbol"))

        # If the users type in a symbol that don't exist
        if quote == None:
            flash("Stock Symbol doesn't exist.", "error")
            return render_template("buy.html")

        # Gets stocks symbol, stocks current price, how many shares he wants to buy and company name
        stock_symbol = quote["symbol"]
        current_price = quote["price"]
        shares = int(request.form.get("shares"))
        company_name = quote["name"]

        # Gets user's current amount of cash
        users_cash = db.execute(
            "SELECT cash FROM users WHERE id = ?", session["user_id"]
        )

        # Do the calcul of the current price of stoks * the shares the user wants to buy
        total = current_price * shares

        # If the user doesn't have enough cash to buy it, return an error
        if total > users_cash[0]["cash"]:
            flash("You don't have enough cash to buy it.")
            return render_template("buy.html")

        else:
            # Subtract user's cash with the price of the shares and store it into a variable
            new_cash = users_cash[0]["cash"] - total
            # Query the database to update users current amount of cash
            db.execute(
                "UPDATE users SET cash = ? WHERE id = ?", new_cash, session["user_id"],
            )
            # Insert into the table "wallet" the number of stocks the user bought, its symbol, price and time
            db.execute(
                "INSERT INTO wallet (user_id, symbol, name, shares, price, time) VALUES (?, ?, ?, ?, ?, datetime('now', 'localtime'))",
                session["user_id"],
                stock_symbol,
                company_name,
                shares,
                total,
            )

            # Update the table "transactions"
            db.execute(
                "INSERT INTO transactions (user_id, symbol, shares, price_per_share, price, status, time) VALUES (?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))",
                session["user_id"],
                stock_symbol,
                shares,
                current_price,
                total,
                "BOUGHT",
            )

            # Display a flash message that the user just bought
            flash("Bought!")

            return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # Get information about stocks that the transactions
    transactions = db.execute(
        "SELECT symbol, shares, price_per_share, price, time FROM transactions WHERE user_id = ?",
        session["user_id"],
    )

    return render_template("history.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            flash("Invalid username and/or password.")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/change", methods=["GET", "POST"])
def change_password():
    """Allows user to change password"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # If password and confirmation don't match, accuse error
        if request.form.get("new_password") != request.form.get("new_confirmation"):
            flash("The New Password and the Confirmation don't match. Try again.")
            return render_template("change.html")

        else:

            # Query database for username
            rows = db.execute(
                "SELECT * FROM users WHERE username = ?", request.form.get("username")
            )

            # Ensure username exists and password is correct
            if len(rows) != 1 or not check_password_hash(
                rows[0]["hash"], request.form.get("old_password")
            ):
                flash("Invalid username and/or password.")
                return render_template("change.html")

            else:

                # Hashes new password before storying it into the database
                pass_hash = generate_password_hash(
                    request.form.get("new_password"),
                    method="pbkdf2:sha256",
                    salt_length=8,
                )

                # Store usersname and password into database
                db.execute(
                    "UPDATE users SET hash = ? WHERE username = ?",
                    pass_hash,
                    request.form.get("username"),
                )

                # Display a flash message that the password was changed
                flash("Password changed!")

                return render_template("change.html")

    # Request method = GET
    else:
        return render_template("change.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return render_template("index.html")


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
            flash("This symbol doesn't exist. Please tap a valid stock symbol.")
            return redirect("/quote")

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

        # Check if there isn't other identical username on the database
        # the result will be stored in roll
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username"),
        )
        # If the len of the row is equal to 0, that means the username the user gave is unique
        # otherwise, if the len is equal to 1, that means the username already exists on the database
        if len(rows) == 1:
            flash(
                "There is already an user with that username. Please select another one."
            )
            return redirect("/register")

        # If password and confirmation don't match, accuse error
        if request.form.get("password") != request.form.get("confirmation"):
            flash("Password anc Confirmation don't match. Try again.")
            return redirect("/register")

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

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Call the lookup function to get the current information about the selected stock
        quote = lookup(request.form.get("symbol"))

        # Store shares quantity input in a variable
        shares = int(request.form.get("shares"))

        # Check how many of the selected stock the user has on his/her wallet
        stocks_amount = db.execute(
            "SELECT SUM(shares) as total_shares FROM wallet WHERE user_id = ? AND symbol = ? GROUP BY symbol",
            session["user_id"],
            request.form.get("symbol"),
        )

        # If the user doesn't own the amount he wants to sell
        if stocks_amount[0]["total_shares"] < int(request.form.get("shares")):
            flash("You don't have the selected amount of shares to sell.")
            return redirect("/sell")

        # User gave valid inputs
        else:

            # Get the amount the user will receive for the sell
            new_cash = quote["price"] * shares

            # Query the database to update users current amount of cash
            db.execute(
                "UPDATE users SET cash = cash + ? WHERE id = ?",
                new_cash,
                session["user_id"],
            )
            # Update the table "wallet" the number of stocks the user has after the sell
            db.execute(
                "UPDATE wallet SET shares = shares - ? WHERE user_id = ? AND symbol = ?",
                shares,
                session["user_id"],
                request.form.get("symbol"),
            )

            # Update the table "transactions"
            db.execute(
                "INSERT INTO transactions (user_id, symbol, shares, price_per_share, price, status, time) VALUES (?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))",
                session["user_id"],
                request.form.get("symbol"),
                "-" + str(shares),
                quote["price"],
                new_cash,
                "SOLD",
            )

            # Delete all the entrances on wallet where shares = 0 to keep table clean
            db.execute("DELETE FROM wallet WHERE shares = 0")

            # Display a flash message that the user just sold
            flash("Sold!")

            return redirect("/")

    # Request method = GET
    else:
        # Query to get the user's wallet information
        stocks = db.execute(
            "SELECT symbol, SUM(shares) as total_shares FROM wallet WHERE user_id = ? GROUP BY symbol HAVING total_shares > 0",
            session["user_id"],
        )

        return render_template("sell.html", stocks=stocks)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
