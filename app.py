#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import dateutil.parser
#import datetime
from datetime import datetime
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import config
import sys
from model import Venue, Artist, Show, db
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
#db = SQLAlchemy(app)
# connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Setup for migrations 
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

def list_genres(genre):
  """Get the genres from the database and convert them to list

  Args:
      genre (str): genres in str

  Returns:
      list: list of genres
  """
  str_genres = genre.lstrip("{").rstrip("}").split(',')
  list_genre = []
  for i in str_genres:
    list_genre.append(i.replace('"', ""))

  return list_genre
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():  
  query_venues = Venue.query.order_by(Venue.id.desc()).limit(10).all()
  query_artist = Artist.query.order_by(Artist.id.desc()).limit(10).all()
  
  venue_data = []
  v = {}

  for i in query_venues:
    v['id'] = i.id
    v['name'] = i.name
    venue_data.append(v)
    v={}
    
  artist_data = []
  a = {}

  for i in query_artist:
    a['id'] = i.id
    a['name'] = i.name
    artist_data.append(a)
    a={}
    
  return render_template('pages/home.html', venues = venue_data, artists = artist_data)

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # Done: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  new_data = []
  d = {} # to hold distinct city and state
  pd = {} # To hold the place details in each distinct city and state
  venue = Venue.query.distinct('city', 'state').all()
  for v in venue:
    d['city'] = v.city
    d['state'] = v.state
    d['venues'] = []
    pd={}
    place = Venue.query.filter_by(city=v.city, state=v.state).all()
    for p in place:
      pd['id'] = p.id
      pd['name'] = p.name
      pd['num_upcoming_shows'] = 0
      d['venues'].append(pd)
      pd = {}
    new_data.append(d)
    d = {}

  return render_template('pages/venues.html', areas=new_data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  search_word = request.form['search_term']
  
  search_result = Venue.query.filter(Venue.name.like('%' + search_word + '%')).all()
  
  data = []
  data_details = {}
  
  for i in search_result:
    data_details['id'] = i.id
    data_details['name'] = i.name
    count = Show.query.filter_by(venue_id = i.id).filter(Show.start_time.between(datetime.now(), Show.start_time)).count()
    data_details['num_upcoming_shows'] = count
    data.append(data_details)
    data_details = {}
  
  new_response = {
    'count': len(search_result),
    'data':data
  }
  
  return render_template('pages/search_venues.html', results=new_response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id
  
  venue = Venue.query.filter_by(id=venue_id).all()  
  new_data = {}
  new_data['id'] = venue[0].id
  new_data['name'] = venue[0].name
  
  #prepare genre list
  new_data['genres'] = list_genres(venue[0].genres)  
  
  new_data['address'] = venue[0].address
  new_data['city'] = venue[0].city
  new_data['state'] = venue[0].state
  new_data['phone'] = venue[0].phone
  new_data['website'] = venue[0].website_link
  new_data['facebook_link'] = venue[0].facebook_link
  new_data['seeking_talent'] = venue[0].talent_hunt
  new_data['image_link'] = venue[0].image_link
  
  # Prepare for past shows
  list_past_show = []
  dict_past_show = {}
  past_shows = Show.query.filter_by(venue_id = venue[0].id).filter(Show.start_time.between(Show.start_time, datetime.now())).all()
  for i in past_shows:
    artist_info = Artist.query.filter_by(id = i.artist_id).all()
    dict_past_show['artist_id'] = artist_info[0].id
    dict_past_show['artist_name'] = artist_info[0].name
    dict_past_show['artist_image_link'] = artist_info[0].image_link
    dict_past_show['start_time'] = str(i.start_time)
    list_past_show.append(dict_past_show)
    dict_past_show = {}    
  new_data['past_shows'] = list_past_show
  
  # Prepare for upcoming show
  upcoming_shows = Show.query.filter_by(venue_id = venue[0].id).filter(Show.start_time.between(datetime.now(), Show.start_time)).all()
  list_upcoming_show = []
  dict_upcoming_show = {}
  for i in upcoming_shows:
    artist_info = Artist.query.filter_by(id = i.artist_id).all()
    dict_upcoming_show['artist_id'] = artist_info[0].id
    dict_upcoming_show['artist_name'] = artist_info[0].name
    dict_upcoming_show['artist_image_link'] = artist_info[0].image_link
    dict_upcoming_show['start_time'] = str(i.start_time)
    list_upcoming_show.append(dict_upcoming_show)
    dict_upcoming_show = {}
  new_data['upcoming_shows'] = list_upcoming_show
  
  
  new_data['past_shows_count'] = len(list_past_show)
  new_data['upcoming_shows_count'] = len(list_upcoming_show)
    
  return render_template('pages/show_venue.html', venue=new_data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  # DONE: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion
  venue_form = VenueForm()
  
  
  if venue_form.validate():
  
    try:
        name = venue_form.name.data
        city = venue_form.city.data
        state = venue_form.state.data
        address = venue_form.address.data
        phone = venue_form.phone.data
        genres = venue_form.genres.data
        facebook_link = venue_form.facebook_link.data
        image_link = venue_form.image_link.data
        website_link = venue_form.website_link.data
        talent_hunt = venue_form.seeking_talent.data
        seeking_desc = venue_form.seeking_description.data
        
        venue = Venue(
          name = name,
          city = city,
          state = state,
          address = address,
          phone = phone,
          genres = genres,
          facebook_link = facebook_link,
          image_link = image_link,
          website_link = website_link,
          talent_hunt = talent_hunt,
          seeking_desc = seeking_desc   
        )
        db.session.add(venue)
        db.session.commit()
    except:
          db.session.rollback()
          error = True        
          print(sys.exc_info())
    finally:
          db.session.close()
    if error:    
      # DONE: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Venue ' + venue_form.name.data + ' could not be listed.')
    else:
      # on successful db insert, flash success
      flash('Venue ' + venue_form.name.data + ' was successfully listed!')
    return redirect(url_for('index'))
  else:
     for fieldName, errorMessages in venue_form.errors.items():
        for err in errorMessages:
          flash(f"Check the {fieldName}: {err}")
  # DONE see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('forms/new_venue.html', form=venue_form)

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # DONE: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False  
  try:
    Show.query.filter_by(venue_id = venue_id).delete()
    Venue.query.filter_by(id = venue_id).delete()
    
    db.session.commit()
    
  except:
    error = True
    print(sys.exc_info())
    db.session.rollback()
  finally:    
    db.session.close()
  
  if error:
    flash('An error occurred. Venue could not be deleted.')
  else:
    flash('Venue was successfully deleted!')
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('venues'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # DONE: replace with real data returned from querying the database
  new_data = []
  a = {}
  artist = Artist.query.all()

  for i in artist:
    a['id'] = i.id
    a['name'] = i.name
    new_data.append(a)
    a={}
  return render_template('pages/artists.html', artists=new_data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  search_word = str.title(request.form['search_term'])
  
  search_result = Artist.query.filter(Artist.name.like('%' + search_word + '%')).all()
  
  data = []
  data_details = {}
  
  for i in search_result:
    count = Show.query.filter_by(artist_id = i.id).filter(Show.start_time.between(datetime.now(), Show.start_time)).count()
    data_details['id'] = i.id
    data_details['name'] = i.name
    data_details['num_upcoming_shows'] = count
    data.append(data_details)
    data_details = {}
  
  new_response = {
    'count': len(search_result),
    'data':data
  }
    
  return render_template('pages/search_artists.html', results=new_response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # Done: replace with real artist data from the artist table, using artist_id
  
  artist = Artist.query.filter_by(id=artist_id).all()  
  new_data = {}
  new_data['id'] = artist[0].id
  new_data['name'] = artist[0].name
  
  #prepare genre list
  new_data['genres'] = list_genres(artist[0].genres)  

  new_data['city'] = artist[0].city
  new_data['state'] = artist[0].state
  new_data['phone'] = artist[0].phone
  new_data['website'] = artist[0].website_link
  new_data['facebook_link'] = artist[0].facebook_link
  new_data['seeking_venue'] = artist[0].venue_hunt
  new_data['available_booking'] = artist[0].available_booking
  new_data['image_link'] = artist[0].image_link
  
  # Prepare for past shows
  list_past_show = []
  dict_past_show = {}
  past_shows = Show.query.filter_by(venue_id = artist[0].id).filter(Show.start_time.between(Show.start_time, datetime.now())).all()
  for i in past_shows:
    
    artist_info = Venue.query.filter_by(id = i.venue_id).all()
    dict_past_show['venue_id'] = artist_info[0].id
    dict_past_show['venue_name'] = artist_info[0].name
    dict_past_show['venue_image_link'] = artist_info[0].image_link
    dict_past_show['start_time'] = str(i.start_time)
    list_past_show.append(dict_past_show)
    dict_past_show = {}    
  new_data['past_shows'] = list_past_show
  
  # Prepare for upcoming show
  upcoming_shows = Show.query.filter_by(venue_id = artist[0].id).filter(Show.start_time.between(datetime.now(), Show.start_time)).all()
  list_upcoming_show = []
  dict_upcoming_show = {}
  for i in upcoming_shows:
    artist_info = Venue.query.filter_by(id = i.venue_id).all()
    dict_upcoming_show['venue_id'] = artist_info[0].id
    dict_upcoming_show['venue_name'] = artist_info[0].name
    dict_upcoming_show['venue_image_link'] = artist_info[0].image_link
    dict_upcoming_show['start_time'] = str(i.start_time)
    list_upcoming_show.append(dict_upcoming_show)
    dict_upcoming_show = {}
  new_data['upcoming_shows'] = list_upcoming_show
  
  
  new_data['past_shows_count'] = len(list_past_show)
  new_data['upcoming_shows_count'] = len(list_upcoming_show)
  
  
  return render_template('pages/show_artist.html', artist=new_data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist_query = Artist.query.filter_by(id=artist_id).all()
  artist={
    "id": artist_query[0].id,
    "name": artist_query[0].name,
    "genres": list_genres(artist_query[0].genres),
    "city": artist_query[0].city,
    "state": artist_query[0].state,
    "phone": artist_query[0].phone,
    "website": artist_query[0].website_link,
    "facebook_link": artist_query[0].facebook_link,
    "seeking_venue": artist_query[0].venue_hunt,
    "available_booking":artist_query[0].available_booking,
    "seeking_description": artist_query[0].seeking_desc,
    "image_link": artist_query[0].image_link,
  }
  # DONE: populate form with fields from artist with ID <artist_id>
  form.name.data = artist.get('name')
  form.genres.data = artist.get('genres')  
  form.city.data = artist.get('city')
  form.state.data = artist.get('state')
  form.phone.data = artist.get('phone')
  form.website_link.data = artist.get('website')
  form.facebook_link.data = artist.get('facebook_link')
  form.seeking_venue.data = artist.get('seeking_venue')
  form.available_booking.data = artist.get('available_booking')
  form.seeking_description.data = artist.get('seeking_description')
  form.image_link.data = artist.get('image_link')
  
  
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # DONE: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm()
  error = False
  
  try:
    update_artist = Artist.query.get(artist_id)
    update_artist.name = form.name.data
    update_artist.genres = form.genres.data
    update_artist.city = form.city.data
    update_artist.state = form.state.data
    update_artist.phone = form.phone.data
    update_artist.website_link = form.website_link.data
    update_artist.facebook_link = form.facebook_link.data
    update_artist.seeking_venue = form.seeking_venue.data
    update_artist.available_booking = form.available_booking.data
    update_artist.seeking_description = form.seeking_description.data
    update_artist.image_link = form.image_link.data
    
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if error:
    # DONE: on unsuccessful db update, flash an error instead.
    flash('An error occurred. Artist ' + form.name.data + ' could not be updated.')
  else:
    # on successful db update, flash success
    flash('Artist ' + form.name.data + ' was successfully updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue_query = Venue.query.filter_by(id=venue_id).all()
  
  venue={
    "id": venue_query[0].id,
    "name": venue_query[0].name,
    "genres": list_genres(venue_query[0].genres),
    "address": venue_query[0].address,
    "city": venue_query[0].city,
    "state": venue_query[0].state,
    "phone": venue_query[0].phone,
    "website": venue_query[0].website_link,
    "facebook_link": venue_query[0].facebook_link,
    "seeking_talent": venue_query[0].talent_hunt,
    "seeking_description": venue_query[0].seeking_desc,
    "image_link": venue_query[0].image_link
  }
  # DONE: populate form with values from venue with ID <venue_id>
  form.name.data = venue.get('name')
  form.genres.data = venue.get('genres')
  form.address.data = venue.get('address')
  form.city.data = venue.get('city')
  form.state.data = venue.get('state')
  form.phone.data = venue.get('phone')
  form.website_link.data = venue.get('website')
  form.facebook_link.data = venue.get('facebook_link')
  form.seeking_talent.data = venue.get('seeking_talent')
  form.seeking_description.data = venue.get('seeking_description')
  form.image_link.data = venue.get('image_link')
  
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # DONE: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm()
  error = False
  
  try:
    update_venue = Venue.query.get(venue_id)
    
    update_venue.name = form.name.data
    update_venue.genres = form.genres.data
    update_venue.city = form.city.data
    update_venue.state = form.state.data
    update_venue.phone = form.phone.data
    update_venue.website_link = form.website_link.data
    update_venue.facebook_link = form.facebook_link.data
    update_venue.talent_hunt = form.seeking_talent.data
    update_venue.seeking_desc = form.seeking_description.data
    update_venue.image_link = form.image_link.data
    
    db.session.commit()
  except:
    db.session.rollback()
    error = True    
  finally:
    db.session.close()
  if error:
    # DONE: on unsuccessful db update, flash an error instead.
    flash('An error occurred. Venue ' + form.name.data + ' could not be updated.')
  else:
    # on successful db update, flash success
    flash('Venue ' + form.name.data + ' was successfully updated!')
  
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # DONE: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion
  error = False

  artist_form = ArtistForm()
  
  if artist_form.validate():
    try:
      name = artist_form.name.data
      city = artist_form.city.data
      state = artist_form.state.data
      phone = artist_form.phone.data
      genres = artist_form.genres.data
      facebook_link = artist_form.facebook_link.data
      image_link = artist_form.image_link.data
      website_link = artist_form.website_link.data
      venue_hunt = artist_form.seeking_venue.data
      available_booking = artist_form.available_booking.data
      seeking_desc = artist_form.seeking_description.data

      artist = Artist(
        name = name,
        city = city,
        state =state,
        phone = phone,
        genres = genres,
        image_link = image_link,
        facebook_link = facebook_link,
        website_link = website_link,
        venue_hunt = venue_hunt,
        available_booking = available_booking,
        seeking_desc = seeking_desc

      )
      db.session.add(artist)
      db.session.commit()
    except:
      db.session.rollback()
      error = True        
      print(sys.exc_info())
    finally:
      db.session.close()
    if error:
      # DONE: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Artist ' + artist_form.name.data + ' could not be listed.')
    else:
      # on successful db insert, flash success
      flash('Artist ' + artist_form.name.data + ' was successfully listed!')

    return redirect(url_for('index'))
  else:
     for fieldName, errorMessages in venue_form.errors.items():
        for err in errorMessages:
          flash(f"Check the {fieldName}: {err}")
  # DONE see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('forms/new_venue.html', form=artist_form)

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # DONE: replace with real venues data.
  
  show = Show.query.all()
  new_data = []
  data_obj = {}
  for i in show:
    venue = Venue.query.filter_by(id=i.venue_id).all()
    artist = Artist.query.filter_by(id=i.artist_id).all()
    data_obj["venue_id"] = venue[0].id
    data_obj["venue_name"] = venue[0].name
    data_obj["artist_id"] = artist[0].id
    data_obj["artist_image_link"] = artist[0].image_link
    data_obj["artist_name"] = artist[0].name
    data_obj["start_time"] = str(i.start_time)
    new_data.append(data_obj)
    data_obj = {}
  
  
  return render_template('pages/shows.html', shows=new_data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # DONE: insert form data as a new Show record in the db, instead
  show_form = ShowForm()
  error = False
  
  query_venues = Venue.query.order_by(Venue.id.desc()).limit(10).all()
  query_artist = Artist.query.order_by(Artist.id.desc()).limit(10).all()
  
  
  if show_form.validate():
    try:
      venue_id = show_form.venue_id.data
      artist_id = show_form.artist_id.data
      start_time = show_form.start_time.data
      
      show = Show(venue_id = venue_id,
                  artist_id = artist_id,
                  start_time = start_time)
      
      db.session.add(show)
      db.session.commit()      
    except:
      db.session.rollback()
      error = True        
      print(sys.exc_info())
    finally:
      db.session.close()
    if error:
      # DONE: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Show could not be listed.')
    else:
      # on successful db insert, flash success
      flash('Show was successfully listed!')    
    
    
    # DONE: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return redirect(url_for('index'))
  else:
    for fieldName, errorMessages in show_form.errors.items():
        for err in errorMessages:
          flash(f"Check the {fieldName}: {err}")
  return render_template('forms/new_show.html', form=show_form)

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
