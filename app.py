# app.py

from flask import Flask, request, jsonify
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
app.config['RESTX_JSON'] = {'ensure_ascii': False, 'indent': 3}
db = SQLAlchemy(app)
api = Api(app)
movies_ns = api.namespace('movies')
directors_ns = api.namespace('directors')
genres_ns = api.namespace('genres')


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Str()
    genre = fields.Method("get_genre", dump_only=True)
    director = fields.Method("get_director", dump_only=True)

    def get_genre(self, movie):
        cl = Genre.query.get(movie.genre_id)
        return cl.name

    def get_director(self, movie):
        cl = Director.query.get(movie.director_id)
        return cl.name


class NameSchema(Schema):
    id = fields.Int()
    name = fields.Str()


sch = MovieSchema()
sch2 = NameSchema()

@movies_ns.route('/')
class MovieView(Resource):
    def get(self):
        try:
            list_movie = []
            dd = request.args.get("director_id")
            gg = request.args.get("genre_id")
            if dd == None and gg == None:
                movie = Movie.query.all()
                for i in movie:
                    list_movie.append(sch.dump(i))
                return list_movie, 200
            elif gg == None and dd != None:
                mm = db.session.query(Movie).filter(Movie.director_id == int(dd))
                for i in mm:
                    list_movie.append(sch.dump(i))
                return list_movie, 200
            elif dd == None:
                mm = db.session.query(Movie).filter(Movie.genre_id == int(gg))
                for i in mm:
                    list_movie.append(sch.dump(i))
                return list_movie, 200
            else:
                mm = db.session.query(Movie).filter(Movie.genre_id == int(gg), Movie.director_id == int(dd))
                for i in mm:
                    list_movie.append(sch.dump(i))
                return list_movie, 200
        except ValueError:
            return '', 201


    def post(self):
        try:
            my_movie = request.json
            my_movie2 = Movie(**my_movie)
            db.session.add(my_movie2)
            db.session.commit()
            return '', 201
        except TypeError as e:
            return "значения выбраны неправильно"


@movies_ns.route('/<int:uid>')
class MovieView2(Resource):
    def get(self, uid):
        try:
            genre = Genre.query.get(uid)
            return sch2.dump(genre), 200
        except AttributeError:
            return '', 201

    def put(self, uid):
        movie = Movie.query.get(uid)
        my_movie = request.json
        movie.title = my_movie.get('title')
        movie.description = my_movie.get('description')
        movie.trailer = my_movie.get('trailer')
        movie.year = my_movie.get('year')
        movie.rating = my_movie.get('rating')
        movie.genre_id = my_movie.get('genre_id')
        movie.director_id = my_movie.get('director_id')
        db.session.add(movie)
        db.session.commit()
        return '', 204

    def delete(self, uid):
        try:
            movie = Movie.query.get(uid)
            db.session.delete(movie)
            db.session.commit()
            return '', 204
        except:
            return 'нет', 201


@directors_ns.route('/')
class DirectorView(Resource):
    def get(self):
        directors_list = []
        directors = Director.query.all()
        for i in directors:
            directors_list.append(sch2.dump(i))

        return directors_list


@directors_ns.route('/<int:uid>')
class DirectorIdView(Resource):
    def get(self, uid):
        g2 = Director.query.get(uid)
        if g2 == None:
            return {"режиссёр": "не найден"}
        return sch2.dump(g2)



@genres_ns.route('/')
class GenreView(Resource):
    def get(self):
        g = []
        g2 = Genre.query.all()
        for i in g2:
            g.append(sch2.dump(i))
        return jsonify(g)


@genres_ns.route('/<int:uid>')
class GenreView(Resource):
    def get(self, uid):
        g2 = Genre.query.get(uid)
        if g2 == None:
            return {"жанр": "не найден"}
        return sch2.dump(g2)

if __name__ == '__main__':
    app.run(debug=True)
