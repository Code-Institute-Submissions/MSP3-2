import os
from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGODBNAME"] = 'InvestSmart'
app.config["MONGO_URI"] = 'mongodb+srv://rooot:ovJpdy6ZxuMmEtWB@myfirstcluster.jwwdc.mongodb.net/InvestSmart?retryWrites=true&w=majority'
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route('/')
@app.route('/get_venture')
def get_venture():
    venture = mongo.db.Venture.find()
    return render_template("venture.html", venture=venture)


@app.route('/new_investor')
def new_investor(): 
    # investor = mongo.db.Investor.find()
    return render_template("investor.html")


if __name__ == '__main__':
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
