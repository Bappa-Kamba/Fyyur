from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import *
from flask import Flask
from flask_moment import Moment

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config.DatabaseURI')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer,  primary_key=True)
    start_time = db.Column(db.String())
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venues.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artists.id'), nullable=False)
# shows = db.Table('shows',
#     db.Column('id', db.Integer, primary_key=True),
#     db.Column('start_time', db.String()),
#     db.Column('venue_id', db.Integer, db.ForeignKey('venue.id'),
#     primary_key=True),
#     db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'),
#     primary_key=True)
# )


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(120))
    artists = db.relationship(
        'Artist', secondary='shows', backref=db.backref('venue', lazy=True))

    #  implement any missing fields, as a database migration using
    #  Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(120))
