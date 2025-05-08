from flask_bootstrap import Bootstrap5
from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import  DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, Date
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, IntegerField, FloatField, TextAreaField, DateField
from wtforms.validators import DataRequired,  Length, URL
from datetime import date
import os


# Flask configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("FLASK_KEY")
Bootstrap5(app)


# Create DataBase
class Base(DeclarativeBase):
    """Declarative class"""
    pass

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# To Do table Configuration
class ToDo(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(250), nullable=False)
    creation_date: Mapped[date] = mapped_column(Date, nullable=False)
    finish_date: Mapped[date] = mapped_column(Date, nullable=True)


with app.app_context():
    db.create_all()


# Forms initialization
class AddToDoForm(FlaskForm):
    item = StringField("Item Description", validators=[DataRequired(), Length(min=1, max=250)])
    description = TextAreaField("Full description", validators=[DataRequired(), Length(min=1, max=1000)])
    status = SelectField(
        "Status",
        choices=[("New", "New"),
                 ("In Progress", "In Progress"),
                 ("Done", "Done"),
                 ("Canceled", "Canceled"),
                 ]
    )
    save_button = SubmitField("Save")


# Routs
@app.route("/")
def index():
    items = db.session.execute(db.Select(ToDo))
    all_items = items.scalars().all()
    print(all_items)

    return render_template("index.html", items=all_items)


@app.route("/add", methods=["GET", "POST"])
def add_new_todo():
    form = AddToDoForm()

    if form.validate_on_submit():
        new_to_do = ToDo(
        item = request.form.get("item"),
        description = request.form.get("description"),
        status = request.form.get("status"),
        creation_date = date.today()
        )

        db.session.add(new_to_do)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template("add.html", form=form)


if __name__ == "__main__":
    app.run(debug=True, port=5006)