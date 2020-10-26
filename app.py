import os
from flask import Flask, render_template, redirect, request, url_for
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
@app.route('/get_venture')
def get_venture():
    venture = mongo.db.Venture.find()
    return render_template("venture.html", venture=venture)

# investor form


@app.route('/new_investor')
def new_investor():
    return render_template("investor.html", venture=mongo.db.Venture.find())

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
def insert_investor():
    investor = mongo.db.Investor
    investor.insert_one(request.form.to_dict())
    return redirect(url_for('get_investor'))


@app.route('/edit_venture/<venture_id>')
def edit_venture(venture_id):
    the_venture = mongo.db.Venture.find_one({"_id": ObjectId(venture_id)})
    return render_template('editventure.html', venture=the_venture)


@app.route('/update_venture/<venture_id>', methods=["POST"])
def update_venture(venture_id):
    venture = mongo.db.Venture
    venture.update({'_id: ObjectId(venture_id)'},
                   {
        'Business_name': request.form.get('Business_name'),
        'net_worth': request.form.get('net_worth'),
        'Min_investment': request.form.get('Min_investment'),
        'percentage_return': request.form.get('percentage_return')
    })
    return redirect(url_for('get_venture'))


@app.route('/delete_venture/<venture_id>')
def delete_venture(venture_id):
    mongo.db.Venture.remove({'_id': ObjectId(venture_id)})
    return redirect(url_for('get_venture'))



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
