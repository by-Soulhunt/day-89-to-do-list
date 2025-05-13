from flask_bootstrap import Bootstrap5
from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import  DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField,  TextAreaField
from wtforms.validators import DataRequired,  Length
from datetime import datetime
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
    creation_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    finish_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)


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

    return render_template("index.html", items=all_items)


@app.route("/add", methods=["GET", "POST"])
def add_new_todo():
    form = AddToDoForm()

    if form.validate_on_submit():
        new_to_do = ToDo(
        item = request.form.get("item"),
        description = request.form.get("description"),
        status = request.form.get("status"),
        creation_date = datetime.now().replace(microsecond=0)
        )

        db.session.add(new_to_do)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template("add.html", form=form)

@app.route("/item/<int:item_id>", methods=["GET", "POST"])
def show_item(item_id):
    """
    Show current To-Do item
    :param item_id: id of current item
    :return: template item.html
    """
    current_item = ToDo.query.get_or_404(item_id)

    # Change Finish data block regarding status
    finish_date = False
    if current_item.finish_date:
        finish_date = True

    return render_template("item.html", item=current_item, finish=finish_date)


@app.route("/delete", methods=["POST"])
def delete_item():
    """
    Delete current item
    :return: redirect to index
    """
    item_id = request.form.get("item_id")
    current_item = ToDo.query.get_or_404(item_id)
    if current_item:
        db.session.delete(current_item)
        db.session.commit()

    return redirect(url_for("index"))


@app.route("/finish_item", methods=["GET"])
def finish_item():
    """
    Change item status to Finish
    :return: refresh current page
    """
    # Take current item ID
    item_id = request.args.get("item_id")
    print(item_id)
    current_item = ToDo.query.get_or_404(item_id)

    # Change object status and save into database
    current_item.status = "Finish"
    current_item.finish_date = datetime.now().replace(microsecond=0)
    db.session.commit()

    return redirect(url_for('show_item', item_id=item_id))


@app.route("/edit_item/<int:item_id>", methods=["GET","POST"])
def edit_item(item_id):
    # Find current item
    current_item = ToDo.query.get_or_404(item_id)
    # Create edit form based on add form and show current item information
    edit_form = AddToDoForm(obj=current_item)


    if edit_form.validate_on_submit():
        # Update the fields
        current_item.item = edit_form.item.data
        current_item.description = edit_form.description.data
        current_item.status = edit_form.status.data

        db.session.commit()

        return render_template("item.html", item=current_item)

    return render_template("add.html", edit=True, form=edit_form)



if __name__ == "__main__":
    app.run(debug=True, port=5006)