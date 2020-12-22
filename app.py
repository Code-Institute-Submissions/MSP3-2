import os
from flask import Flask, render_template, flash, redirect, request, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env
from bson.objectid import ObjectId


app = Flask(__name__)

app.config["MONGODBNAME"] = 'InvestSmart'
app.config["MONGO_URI"] = 'mongodb+srv://rooot:ovJpdy6ZxuMmEtWB@myfirstcluster.jwwdc.mongodb.net/InvestSmart?retryWrites=true&w=majority'
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)



@app.route('/')
# display venture
@app.route('/top_venture')
def top_venture():
    venture = mongo.db.Venture.find()
    Investor = mongo.db.Investor.find()
    return render_template("home.html", venture=venture, Investor=Investor)


# display investemnts
@app.route('/investments')
def investments():
    Investor = mongo.db.Investor.find()
    venture = mongo.db.Venture.find()
    return render_template("investments.html", Investor=Investor, venture=venture)
    

# all venture
@app.route('/all_ventures')
def all_ventures():
    venture = mongo.db.Venture.find()
    Investor = mongo.db.Investor.find()
    return render_template("all_ventures.html", venture=venture, Investor=Investor)

# investor form


@app.route('/new_investment')
def new_investment():
    return render_template("investor.html", Investor=mongo.db.Investor.find(), venture=mongo.db.Venture.find())

# venture form


@app.route('/new_venture')
def new_venture():
    return render_template("new_venture.html", venture=mongo.db.Venture.find())


# post venture
@app.route('/insert_venture', methods=['POST'])
def insert_venture():
    venture = mongo.db.Venture
    venture.insert_one(request.form.to_dict())
    return redirect(url_for('get_venture'))


# submit investment
@app.route('/insert_investment', methods=['POST'])
def insert_investment():
    Investor = mongo.db.Investor
    Investor.insert_one(request.form.to_dict())
    return redirect(url_for('investments'))


@app.route('/edit_Investment/<Investor_id>')
def edit_Investment(Investor_id):
    the_invest = mongo.db.Investor.find_one({"Investor_id": ObjectId(Investor_id)})
    venture = mongo.db.Venture
    return render_template('editinvestment.html', Invest=the_invest, venture=venture)


@app.route('/update_investment/<Invest_id>', methods=["POST"])
def update_investment(Invest_id):
    invest = mongo.db.Investor
    venture = mongo.db.Venture.find().sort("Business_name", 1)
    invest.update({'_id: ObjectId(Invest_id)'},
                  {
        'First_name': request.form.get('First_name'),
        'Last_name': request.form.get('Last_name'),
        'Business_name': request.form.get('Business_name'),
        'actual_profit': request.form.get('actual_profit'),
        'money_invested': request.form.get('money_invested'),
        'estimated_Profit': request.form.get('estimated_Profit')
    })
    return render_template('investments.html', invest=invest, venture=venture)


@app.route('/delete_Investment/<Investor_id>')
def delete_Investment(Investor_id):
    mongo.db.Investor.remove({'_id': ObjectId(Investor_id)})
    flash("Investment Deleted")
    return redirect(url_for('investments'))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["Users"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["Users"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.Users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                        session["Users"] = request.form.get("username").lower()
                        flash("Hello, {}".format(
                            request.form.get("username")))
                        return redirect(url_for(
                            "profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.Users.find_one(
        {"username": session["Users"]})["username"]

    if session["Users"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("Users")
    return redirect(url_for("login"))


if __name__ == '__main__':
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
