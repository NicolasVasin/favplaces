from data.places import Place
from data import db_session
from flask import Flask, request, render_template, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


class PlaceForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    address = StringField('Адрес')
    notes = TextAreaField('Заметки')
    submit = SubmitField('Сохранить')


@app.route('/')
@app.route('/index')
def index():
    db_sess = db_session.create_session()
    places = db_sess.query(Place)
    return render_template('index.html', title='Любимые места', places=places)


@app.route('/place/<int:id>', methods=['POST', 'GET'])
def place_id(id):
    form = PlaceForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        place = db_sess.query(Place).filter(Place.id == id).first()
        place.name = form.name.data
        place.address = form.address.data
        place.notes = form.notes.data
        db_sess.commit()
    else:
        db_sess = db_session.create_session()
        place = db_sess.query(Place).filter(Place.id == id).first()
        form.name.data = place.name
        form.address.data = place.address
        form.notes.data = place.notes

    return render_template('place.html', title='Добавление места', form=form)


@app.route('/place', methods=['POST', 'GET'])
def place():
    form = PlaceForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()

        place = Place(
            name=form.name.data,
            address=form.address.data,
            notes=form.notes.data
        )
        db_sess.add(place)
        db_sess.commit()
        return redirect('/index')
    # if request.method == 'POST':

    return render_template('place.html', title='Добавление места', form=form)


def main():
    db_session.global_init("db/places.db")
    app.run()


if __name__ == '__main__':
    main()
