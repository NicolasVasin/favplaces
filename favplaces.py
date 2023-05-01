from data.places import Place
from data import db_session
from flask import Flask, request, render_template, redirect, send_file
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
# Этот класс нужен сделать картинку из потока байт
from io import BytesIO
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

# форма с полями места


class PlaceForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    address = StringField('Адрес')
    notes = TextAreaField('Заметки')
    submit = SubmitField('Сохранить')

# главная страница


@app.route('/')
@app.route('/index')
def index():
    db_sess = db_session.create_session()
    places = db_sess.query(Place)
    return render_template('index.html', title='Любимые места', places=places)

# удаление места


@app.route('/del/<int:id>', methods=['POST', 'GET'])
def del_id(id):
    db_sess = db_session.create_session()
    place = db_sess.query(Place).filter(Place.id == id).first()
    db_sess.delete(place)
    db_sess.commit()
    return redirect('/index')


# редактирование существующего места
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
    return render_template('place.html', title='Место', form=form, id=id)


# добавление нового места
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
    return render_template(
        'place.html',
        title='Добавление места',
        form=form,
        id=0)

# запрос к API Яндекса для получения карты


@app.route('/map/<int:id>', methods=['POST', 'GET'])
def map_id(id):
    db_sess = db_session.create_session()
    place = db_sess.query(Place).filter(Place.id == id).first()
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": place.address,
        "format": "json"}

    response = requests.get(geocoder_api_server, params=geocoder_params)

    if not response:
        # обработка ошибочной ситуации
        pass

    # Преобразуем ответ в json-объект
    json_response = response.json()
    # Получаем первый топоним из ответа геокодера.
    toponym = json_response["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]
    # Координаты центра топонима:
    toponym_coodrinates = toponym["Point"]["pos"]
    # Долгота и широта:
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

    delta = "0.005"

    # Собираем параметры для запроса к StaticMapsAPI:
    map_params = {
        "ll": ",".join([toponym_longitude, toponym_lattitude]),
        "spn": ",".join([delta, delta]),
        "l": "map"
    }

    map_api_server = "http://static-maps.yandex.ru/1.x/"
    # ... и выполняем запрос
    response = requests.get(map_api_server, params=map_params)

    return send_file(
        BytesIO(response.content),
        mimetype='image/jpeg',
        as_attachment=True,
        download_name='%d.jpg' % id)

# страница о приложении


@app.route('/about')
def about():
    return render_template('about.html', title='О приложении')


def main():
    db_session.global_init("db/places.db")
    app.run()


if __name__ == '__main__':
    main()
