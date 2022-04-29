from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

from update_form import MyForm, MyForm_2
import requests

api_key_movies = "50c55907bb0d47b9d0d944f0e493dd4b"
search_movies_url = "https://api.themoviedb.org/3/search/movie"
search_movie_url = "https://api.themoviedb.org/3/movie/"
search_movie_img_url = "https://image.tmdb.org/t/p/w500"

app = Flask(__name__)
app.config['SECRET_KEY'] = "8BYkEfBA6O6donzWlSihBXox7C0sKR6b"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///top-10-films.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Bootstrap(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(50), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return f"Movie {self.title}"

# db.create_all()


@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating.desc())
    ranking = 0
    for movie in all_movies:
        ranking += 1
        movie.ranking = ranking
    db.session.commit()
    return render_template("index.html", movies=all_movies)


# Updates rating and review
@app.route("/update", methods=["GET", "POST"])
def update():
    form = MyForm()

    if form.validate_on_submit():
        movie_id = request.args.get("id")
        try:
            new_rating = float(form.rating.data)
            new_review = form.review.data

        except ValueError:
            return "Please, provide the relevant information"

        else:
            movie_to_edit = Movie.query.get(movie_id)
            movie_to_edit.review = new_review
            movie_to_edit.rating = new_rating
            db.session.commit()
            return redirect(url_for("home"))



    return render_template("edit.html", form=form)


# Deletes record from library
@app.route("/delete", methods=["GET", "POST"])
def delete():
    movie_id = request.args.get("id")
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


# Finds a movie by a title
@app.route("/add", methods=["GET", "POST"])
def add():
    form = MyForm_2()
    if form.validate_on_submit():
        new_movie_title = form.title.data
        response = requests.get(url=search_movies_url, params={"api_key": api_key_movies, "query": new_movie_title}).json()
        return render_template("select.html", movies=response["results"])

    return render_template("add.html", form=form)


# Adds movie to library, redirects to update to get the remaining information
@app.route("/add_movie")
def add_movie():
    api_movie_id = request.args.get("movie_id")

    try:
        response = requests.get(url=f"{search_movie_url}{api_movie_id}?api_key={api_key_movies}").json()
        new_movie_title = response["original_title"]
        new_movie_img_url = search_movie_img_url + response['backdrop_path']

    except:
        return "Sorry, this movie can not be added"

    else:
        new_movie = Movie(title=new_movie_title, year=response["release_date"], description=response["overview"], img_url=new_movie_img_url)
        print(new_movie.year)
        db.session.add(new_movie)
        db.session.commit()
        new_movie_id = Movie.query.filter_by(title=new_movie_title).first()
        return redirect(url_for('update', id=new_movie_id.id))



if __name__ == '__main__':
    app.run(debug=True)
