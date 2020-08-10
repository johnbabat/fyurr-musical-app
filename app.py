#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
from datetime import datetime
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, make_response, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

venue_genres = db.Table('venue_genres',
  db.Column('venue_id', db.Integer, db.ForeignKey('venues.id'), primary_key=True),
  db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
)

artist_genres = db.Table('artist_genres',
  db.Column('artist_id', db.Integer, db.ForeignKey('artists.id'), primary_key=True),
  db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
)

class Venue(db.Model):
  __tablename__ = 'venues'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String())
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  address = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  website = db.Column(db.String(120))
  seeking_talent = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String(120))
  genres = db.relationship('Genre', secondary=venue_genres, backref=db.backref('venues', lazy=True))
  shows = db.relationship('Show', backref = 'venues')

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
  __tablename__ = 'artists'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String())
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  genres = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  website = db.Column(db.String(120))
  seeking_venue = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String(120))
  genres = db.relationship('Genre', secondary=artist_genres, backref=db.backref('artists', lazy=True))
  shows = db.relationship('Show', backref = 'artists')

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
  __tablename__ = 'shows'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
  start_time = db.Column(db.String(50), nullable=False)


class Genre(db.Model):
  __tablename__ = 'genres'
  
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String())


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en_US')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  artists = Artist.query.order_by('id').all()[::-1][:10]
  venues = Venue.query.order_by('id').all()[::-1][:10]
  return render_template('pages/home.html', venues=venues, artists=artists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  venues = Venue.query.order_by('id').all()
  data, groups = [], {}

  for venue in venues:
    if (venue.city, venue.state) in groups:
      groups[(venue.city, venue.state)].append(venue)
    else:
      groups[(venue.city, venue.state)] = [venue]
  for group in groups:
    value = {
      "city": group[0],
      "state": group[1],
      "venues": []
    }
    for venue in groups[group]:
      value["venues"].append({
        "id": venue.id,
        "name": venue.name
      })
    data.append(value)

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  keyWord = request.form.get('search_term', '').lower()
  if not keyWord:
    flash('Enter a search keyword')
    return render_template('pages/venues.html')

  response1 = {"count": 0, "data": []}
  venues = Venue.query.all()
  for venue in venues:
    if keyWord in venue.name.lower():
      data = {
        "id": venue.id,
        "name": venue.name,
      }
      response1["data"].append(data)
      response1["count"] +=1

  response2 = {"count": 0, "data": []}
  venues = Venue.query.all()
  for venue in venues:
    if keyWord in f'{venue.city.lower()}, {venue.state.lower()}':
      data = {
        "id": venue.id,
        "name": venue.name,
        "state": venue.state,
        "city": venue.city
      }
      response2["data"].append(data)
      response2["count"] +=1

  return render_template('pages/search_venues.html', results=[response1, response2], search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue = Venue.query.get(venue_id)
  if not venue:
    flash('Venue does not exist')
    return render_template('pages/home.html')
  data ={}
  data["id"] = venue.id
  data["name"] = venue.name
  data["genres"] = [genre.name for genre in venue.genres]
  data["address"] = venue.address
  data["city"] = venue.city
  data["state"] = venue.state
  data["phone"] = venue.phone
  data["website"] = venue.website
  data["facebook_link"] = venue.facebook_link
  data["seeking_talent"] = venue.seeking_talent
  if venue.seeking_talent:
    data["seeking_description"] = venue.seeking_description
  data["image_link"] = venue.image_link
  data["past_shows"] = []
  data["upcoming_shows"] = []
  shows = venue.shows
  prev_shows = []
  next_shows = []
  for show in shows:
    if dateutil.parser.parse(show.start_time) > datetime.now():
      next_shows.append(show)
    else:
      prev_shows.append(show)
  for show in prev_shows:
    cur_show = {}
    artist = Artist.query.get(show.artist_id)
    cur_show["artist_id"] = artist.id
    cur_show["artist_name"] = artist.name
    cur_show["artist_image_link"] = artist.image_link
    cur_show["start_time"] = show.start_time
    data["past_shows"].append(cur_show)
  for show in next_shows:
    cur_show = {}
    artist = Artist.query.get(show.artist_id)
    cur_show["artist_id"] = artist.id
    cur_show["artist_name"] = artist.name
    cur_show["artist_image_link"] = artist.image_link
    cur_show["start_time"] = show.start_time
    data["upcoming_shows"].append(cur_show)
  
  data["past_shows_count"] = len(data["past_shows"])
  data["upcoming_shows_count"] = len(data["upcoming_shows"])

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  form = VenueForm()
  if not form.validate_on_submit():
    flash('One or more form fields are invalid. Please re-fill correctly.')
    return render_template('forms/new_venue.html', form=form)

  try:
    name = request.form.get('name')
    address = request.form.get('address')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    image_link = request.form.get('image_link')
    website = request.form.get('website')
    facebook_link = request.form.get('facebook_link')
    seeking_talent = True if request.form.get('seeking_venue') == 'YES' else False
    seeking_description = request.form.get('seeking_description')
    new_venue = Venue(name=name, address=address, city=city, state=state, phone=phone, image_link=image_link, website=website, facebook_link=facebook_link, seeking_talent=seeking_talent, seeking_description=seeking_description)
    genres = set(request.form.getlist('genres'))
    for genre in genres:
      genre_present = Genre.query.filter_by(name=genre).all()
      if not genre_present:
        g = Genre(name=genre)
        db.session.add(g)
      else:
        g = genre_present[0]
      g.venues.append(new_venue)

    db.session.add(new_venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.close()
  
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    error_code = 200
    flash('Venue +', successfully)
  except:
    db.session.rollback()
    error_code = 404
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html'), error_code

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()
  data = []

  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  keyWord = request.form.get('search_term', '').lower()
  if not keyWord:
    flash('Enter a search keyword')
    return render_template('pages/artists.html')

  response1 = {"count" : 0, "data": []}
  artists = Artist.query.all()
  for artist in artists:
    if keyWord in artist.name.lower():
      data = {
        "id": artist.id,
        "name": artist.name
      }
      response1["data"].append(data)
      response1["count"] +=1

  response2 = {"count" : 0, "data": []}
  artists = Artist.query.all()
  for artist in artists:
    if keyWord in f'{artist.city.lower()}, {artist.state.lower()}':
      data = {
        "id": artist.id,
        "name": artist.name,
        "state": artist.state,
        "city": artist.city
      }
      response2["data"].append(data)
      response2["count"] +=1

  return render_template('pages/search_artists.html', results=[response1, response2], search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  artist = Artist.query.get(artist_id)
  if not artist:
    flash('Artist does not exist')
    return render_template('pages/home.html')
  data ={}
  data["id"] = artist.id
  data["name"] = artist.name
  data["genres"] = [genre.name for genre in artist.genres]
  data["city"] = artist.city
  data["state"] = artist.state
  data["phone"] = artist.phone
  data["website"] = artist.website
  data["facebook_link"] = artist.facebook_link
  data["seeking_venue"] = artist.seeking_venue
  if artist.seeking_venue:
    data["seeking_description"] = artist.seeking_description
  data["image_link"] = artist.image_link
  data["past_shows"] = []
  data["upcoming_shows"] = []
  shows = artist.shows
  prev_shows = []
  next_shows = []
  for show in shows:
    if dateutil.parser.parse(show.start_time) > datetime.now():
      next_shows.append(show)
    else:
      prev_shows.append(show)
  for show in prev_shows:
    cur_show = {}
    venue = Venue.query.get(show.venue_id)
    cur_show["venue_id"] = venue.id
    cur_show["venue_name"] = venue.name
    cur_show["venue_image_link"] = venue.image_link
    cur_show["start_time"] = show.start_time
    data["past_shows"].append(cur_show)
  for show in next_shows:
    cur_show = {}
    venue = Venue.query.get(show.venue_id)
    cur_show["venue_id"] = venue.id
    cur_show["venue_name"] = venue.name
    cur_show["venue_image_link"] = venue.image_link
    cur_show["start_time"] = show.start_time
    data["upcoming_shows"].append(cur_show)
  
  data["past_shows_count"] = len(data["past_shows"])
  data["upcoming_shows_count"] = len(data["upcoming_shows"])

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  
  artist = Artist.query.get(artist_id)
  if not artist:
    flash('Artist does not exist')
    return render_template('pages/home.html')
  form = ArtistForm(obj=artist)
  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  form = ArtistForm()
  if not form.validate_on_submit():
    flash('One or more form fields are invalid. Please re-fill correctly.')
    return render_template('forms/edit_artist.html', form=form)

  artist = Artist.query.get(artist_id)
  try:
    artist.name = request.form.get('name')
    artist.artist = Artist.query.get(artist_id)
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.image_link = request.form.get('image_link')
    artist.website = request.form.get('website')
    artist.facebook_link = request.form.get('facebook_link')
    artist.seeking_venue = True if request.form.get('seeking_venue') == 'YES' else False
    artist.seeking_description = request.form.get('seeking_description')
    genres = request.form.getlist('genres')
    artist.genres = []
    for genre in genres:
      genre_present = Genre.query.filter_by(name=genre).all()
      if not genre_present:
        g = Genre(name=genre)
        db.session.add(g)
      else:
        g = genre_present[0]
      g.artists.append(artist)

    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occured ' + request.form['name'] + ' could not be updated!')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  
  venue = Venue.query.get(venue_id)
  if not venue:
    flash('Venue does not exist')
    return render_template('pages/home.html')
  form = VenueForm(obj=venue)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm()
  if not form.validate_on_submit():
    flash('One or more form fields are invalid. Please re-fill correctly.')
    return render_template('forms/edit_venue.html', form=form)

  venue = Venue.query.get(venue_id)
  try:
    venue.name = request.form.get('name')
    venue.address = request.form.get('address')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.phone = request.form.get('phone')
    venue.image_link = request.form.get('image_link')
    venue.website = request.form.get('website')
    venue.facebook_link = request.form.get('facebook_link')
    venue.seeking_talent = True if request.form.get('seeking_talent') == 'YES' else False
    venue.seeking_description = request.form.get('seeking_description')
    genres = request.form.getlist('genres')
    venue.genres = []
    for genre in genres:
      genre_present = Genre.query.filter_by(name=genre).all()
      if not genre_present:
        g = Genre(name=genre)
        db.session.add(g)
      else:
        g = genre_present[0]
      g.venues.append(venue)

    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occured ' + request.form['name'] + ' could not be updated!')
  finally:
    db.session.close()
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm()
  if not form.validate_on_submit():
    flash('One or more form fields are invalid. Please re-fill correctly.')
    return render_template('forms/new_artist.html', form=form)

  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    image_link = request.form.get('image_link')
    website = request.form.get('website')
    facebook_link = request.form.get('facebook_link')
    seeking_venue = True if request.form.get('seeking_venue') == 'YES' else False
    seeking_description = request.form.get('seeking_description')
    new_artist = Artist(name=name, city=city, state=state, phone=phone, image_link=image_link, website=website, facebook_link=facebook_link, seeking_venue=seeking_venue, seeking_description=seeking_description)
    genres = set(request.form.getlist('genres'))
    for genre in genres:
      genre_present = Genre.query.filter_by(name=genre).all()
      if not genre_present:
        g = Genre(name=genre)
        db.session.add(g)
      else:
        g = genre_present[0]
      g.artists.append(new_artist)

    db.session.add(new_artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  shows = Show.query.order_by('id').all()
  data = {"old_shows":[], "upcoming_shows":[]}

  for show in shows:
    artist = Artist.query.get(show.artist_id)
    venue = Venue.query.get(show.venue_id)
    if datetime.now() > dateutil.parser.parse(show.start_time):
      data["old_shows"].append({
        "venue_id": show.venue_id,
        "venue_name": venue.name,
        "artist_id": show.artist_id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": show.start_time,
      })
    else:
      data["upcoming_shows"].append({
        "venue_id": show.venue_id,
        "venue_name": venue.name,
        "artist_id": show.artist_id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": show.start_time,
      })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create', methods=['GET'])
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm()
  if not form.validate_on_submit():
    flash('One or more form fields are invalid. Please re-fill correctly.')
    return render_template('forms/new_show.html', form=form)

  
  try:
    artist_id = request.form.get('artist_id')
    venue_id = request.form.get('venue_id')
    start_time = request.form.get('start_time')

    artist_exists = Artist.query.get(artist_id)
    if not artist_exists:
      flash('No artist with ID ' + artist_id)
      return render_template('forms/new_show.html', form=form)

    venue_exists = Venue.query.get(venue_id)
    if not venue_exists:
      flash('No venue with ID ' + venue_id)
      return render_template('forms/new_show.html', form=form)

    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  # on successful db insert, flash success
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
