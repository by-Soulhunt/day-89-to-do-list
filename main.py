from flask_bootstrap import Bootstrap5
from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import  DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, IntegerField, FloatField
from wtforms.validators import DataRequired,  Length, URL
import os


# Flask configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("FLASK_KEY")
Bootstrap5(app)


# Create DataBase
class Base(DeclarativeBase):
    """Declarative class"""
    pass

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cafes.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)

@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, port=5006)