from flask_sqlalchemy import SQLAlchemy
import app

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    talent_hunt = db.Column(db.Boolean, default=False)
    seeking_desc = db.Column(db.String(120))
    Artist = db.relationship('Show', back_populates='Venue')

    # DONE: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    venue_hunt = db.Column(db.Boolean, default=False)
    available_booking = db.Column(db.Boolean, default=False)
    seeking_desc = db.Column(db.String(500))
    Venue = db.relationship('Show', back_populates='Artist')
    

    # DONE: implement any missing fields, as a database migration using Flask-Migrate

# DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer,db.ForeignKey("Venue.id"))
    artist_id = db.Column(db.Integer,db.ForeignKey("Artist.id"))
    start_time = db.Column(db.DateTime)
    Venue = db.relationship('Venue', back_populates="Artist")
    Artist = db.relationship('Artist', back_populates="Venue")