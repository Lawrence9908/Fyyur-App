
from operator import le
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import ForeignKey

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
    image_link = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String()))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String)
    seeking_talent = db.Column(db.Boolean , default = False)
    seeking_description = db.Column(db.String)
    venue_show = db.relationship("Show", backref="venue",lazy=True)

    def __repr__(self):
       return f'<Venue {self.id}  {self.name}>'

 

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String)
    seeking_venue = db.Column(db.Boolean, default =False)
    seeking_description = db.Column(db.String)
    arist_show= db.relationship("Show", backref="artist",lazy=True)
    
    def __repr__(self):
       return f'<Venue {self.id}  {self.name}>'

 
class Show(db.Model):
  __tablename_='Show'
  show_id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, ForeignKey("Artist.id"))
  venue_id = db.Column(db.Integer, ForeignKey("Venue.id"))
  start_time = db.Column(db.DateTime, nullable= False, default = datetime.utcnow)

  def __repr__(self):
      return f"<Show {self.id}, Artist {self.artist_id}, Venue {self.venue_id}>"



def num_of_upcoming_shows(venues):
    for venue in venues:
        num_upcoming_shows=0
        shows= Show.query.filter_by(venue_id = venue.id).all()
        now = datetime.now()

    for show in shows:
      if show.start_time > now:
        num_upcoming_shows +=1