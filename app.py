#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from email.policy import default
import json
from operator import truediv
from tracemalloc import Trace
from unittest import result
from xmlrpc.client import Boolean
import dateutil.parser
import babel
from flask import Flask, jsonify, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import ForeignKey, true
from forms import *
import sys
from flask_migrate import Migrate
from datetime import datetime
from models import *

 

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
db = SQLAlchemy(app)


migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#




@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  
  venues = Venue.query.all()
  data = []
  locations = set()
  for venue in venues:
    locations.add((venue.city, venue.state))

  for location in locations:
    data.append({
      "city": location[0],
      "state":location[1],
      "venues":[]
    })

    for venue_location in data:
      if venue.state == venue_location['state'] and venue.city==venue_location['city']:
        venue_location['venues'].append({
          "id": venue.id,
          "name":venue.name,
          "num_upcoming_shows": num_of_upcoming_shows(venues)
        })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():

  search_term = request.form.get('search_term','')
  result = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))

  response ={"count":result.count(),"data": result}
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  
  # getting venue by venue_id 
  venue =  Venue.query.get(venue_id)
  # get shows by id
  shows = Show.query.filter_by(venue_id = venue_id)
  # list of past shows 
  past_shows =[]
  # upcoming shows list
  upcoming_shows=[]
  # current data and time
  now = datetime.now()
  upcoming_shows_data = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time>now).all()
  for show in upcoming_shows_data:
    upcoming_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": format_datetime(str(show.start_time))
    })

  past_shows_data = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time < now).all()
  for show in past_shows_data:
     past_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": format_datetime(str(show.start_time))
     })
  
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows":upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shiws_count":len(upcoming_shows)
  }


  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  try:
    # getting data user inputs
    form = VenueForm()
    
    seeking_talent =True
    if "seeking_venue" not in request.form:
      seeking_talent = False
  
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    image_link = request.form['image_link']
    genres = request.form.getlist('genres')
    facebook_link = request.form['facebook_link']
    website_link = request.form['website_link']
    seeking_description = request.form['seeking_description']

    venue = Venue(
      name = name,city = city,state = state,address = address,phone= phone,image_link = image_link,
      genres = genres,facebook_link = facebook_link,website_link= website_link,
      seeking_talent=seeking_talent,seeking_description = seeking_description
    )
  
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    # on unsuccessful, flash unsuccessfull
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    print(sys.exc_info())
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    
    venue = Venue.query.get(venue_id)
    name = venue.name
    db.session.delete(name)
    db.session.commit()
    flash("Vneue successfully deleted")
  except: 
    flash("Venue was not deleted, error occured")
    print(sys.exc_info())
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # getting artist data
  data= Artist.query.all()
 
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():

  search_artist = request.form.get('search_term','')
  result_data = Artist.query.filter(Artist.name.ilike(f'%{search_artist}%'))
  
  response={"count": result_data.count(),"data": result_data}

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
 
  # getting venue by id 
  artist =  Artist.query.get(artist_id)
  # get shows by id
  shows = Show.query.filter_by(artist_id = artist_id)
  # pash shows list
  past_shows =[]
  # upcoming shows list
  upcoming_shows=[]
  # current data anda time
  now = datetime.now()
  upcoming_shows_data = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time > now).all()
  for show in upcoming_shows_data:
    upcoming_shows.append({
      "artist_id": show.venue_id,
      "artist_name": show.venue.name,
      "artist_image_link": show.venue.image_link,
      "start_time":format_datetime(str(show.start_time))
    })
  

  past_shows_data = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time > now).all()
  for show in past_shows_data:
    past_shows.append({
      "artist_id": show.venue_id,
      "artist_name": show.venue.name,
      "artist_image_link": show.venue.image_link,
      "start_time":format_datetime(str(show.start_time))
    })
  

  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state":artist.state,
    "phone": artist.phone,
    "facebook_link": artist.facebook_link,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows":upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shiws_count":len(upcoming_shows)
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist_data=Artist.query.get(artist_id)

  form.name.data= artist_data.name
  form.city.data= artist_data.city
  form.state.data= artist_data.state
  form.phone.data = artist_data.phone
  form.genres.data = artist_data.genres
  form.facebook_link.data = artist_data.facebook_link
  form.image_link.data= artist_data.image_link
  form.website_link.data = artist_data.website_link
  form.seeking_venue.data= artist_data.seeking_venue
  form.seeking_description.data =artist_data.seeking_description
                  
    
  return render_template('forms/edit_artist.html', form=form, artist=artist_data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  
  
  # get venue by id
  artist = Artist.query.get(artist_id)
  try:
    form = ArtistForm()
    # load data from user input
    seeking_venue =True
    if "seeking_venue" not in request.form:
      seeking_venue=False

    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form['genres']
    artist.facebook_link = request.form['facebook_link']
    artist.website_link = request.form['website_link']
    artist.image_link = request.form['image_link']
    artist.seeking_venue = seeking_venue
    artist.seeking_description = request.form['seeking_description']

    db.session.commit()
    flash("Successfully Updated")
  except:
    flash("Error occured")
    db.session.rollback()

  finally:
    db.session.close()
 
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  venue_data = Venue.query.get(venue_id)

  form.name.data= venue_data.name
  form.city.data= venue_data.city
  form.state.data= venue_data.state
  form.phone.data = venue_data.phone
  form.genres.data = venue_data.genres
  form.facebook_link.data = venue_data.facebook_link
  form.image_link.data= venue_data.image_link
  form.website_link.data = venue_data.website_link
  form.seeking_talent.data= venue_data.seeking_talent
  form.seeking_description.data =venue_data.seeking_description

  return render_template('forms/edit_venue.html', form=form, venue=venue_data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  #getting venue by veneu_id  
  venue = Venue.query.get(venue_id)
  try:  
    form = VenueForm()
    
    # loading form data from user input
    seeking_talent =True
    if "seeking_talent" not in request.form:
      seeking_talent = False
    venue.name= request.form['name']
    venue.city= request.form['city']
    venue.state= request.form['state']
    venue.address= request.form['address']
    venue.phone= request.form['phone']
    venue.genres= request.form['genres']
    venue.facebook_link= request.form['facebook_link']
    venue.website_link= request.form['website_link']
    venue.image_link= request.form['image_link']
    venue.seeking_talent= seeking_talent 
    venue.seeking_description= request.form['seeking_description']
    # commit changess, flash message if successful
    db.session.commit()
    flash("The veneu was updated successfully")
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash("Error occured while updat")
  finally:
    db.session.close()

  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    # GETTING USER INPUT FROM THE ARTIST FORM
    form = ArtistForm()
    seeking_venue =True
    if "seeking_venue" not in request.form:
      seeking_venue = False
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website_link = request.form['website_link']
    seeking_description = request.form['seeking_description']
    
    # creating artist object
    artist = Artist(
      name = name,city = city,state = state,phone = phone,genres = genres,image_link=image_link,
      facebook_link = facebook_link,website_link = website_link,seeking_venue = seeking_venue,
      seeking_description = seeking_description
    )
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    # on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
 
  shows_details= Show.query.all()
  data =[]
  for show in shows_details:
    data.append({
      "venue_id": show.venue.id,
      "venue_name":show.venue.name,
      "artist_id":show.artist.id,
      "artist_name":show.artist.name,
      "artist_image_link":show.artist.image_link,
      "start_time":format_datetime(str(show.start_time)) 
    })
 
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    form = ShowForm()
    
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']

    show = Show(artist_id = artist_id,venue_id = venue_id,start_time = start_time)

    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    # on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
