#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate, MigrateCommand
from datetime import date
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://sdupl:Baller24@localhost:5432/fyyur'

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
    genres = db.Column(db.ARRAY(db.String()))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False, server_default="f", nullable = False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
      return '<Venue {}>'.format(self.name)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

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
    seeking_performance_venues = db.Column(db.Boolean(), default=False, nullable=False  )
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
      return '<Artist {}>'.format(self.name)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'Show'
    
    id = db.Column(db.Integer, primary_key=True)
    Venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable = False)
    Artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable = False)
    show_date = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
      return '<Show {}>'.format(self.artist_id, self.venue.id)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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

  areas = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)
  data = []
  for area in areas:
    areas = Venue.query.filter_by(state=area.state).filter_by(city=area.city).all()
    venue_data = []
    for venue in areas:
      upcoming_shows = len(db.session.query(Show).filter(Show.show_date >= date.today()).all())
      venue_data.append({
        'id':venue.id,
        'name':venue.name,
        'num_upcoming_shows': upcoming_shows
      })
      data.append({
        'city':area.city,
        'state':area.state,
        'venues':venue_data
      })
  return render_template('pages/venues.html', areas=data)

    
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  result = Venue.query.filter(Venue.name.like(f'%{search_term}%'))
  response={
    "count": result.count(),
    "data": result
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.filter_by(id=venue_id)
  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
      # TODO: modify data to be the data object returned from db insertion
      # TODO: insert form data as a new Venue record in the db, instead
      venue = Venue(
          name=request.form.get('name'),
          city=request.form.get('city'),
          address=request.form.get('address'),
          state=request.form.get('state'),
          phone=request.form.get('phone'),
          facebook_link=request.form.get('facebook_link'),
          genres=request.form.get('genres'),
          seeking_talent= True if 'seeking_talent' in request.form else False,
          seeking_description=request.form.get('seeking_description')
      )
      try:    
          db.session.add(venue)
          db.session.commit()
          flash('Venue ' + request.form['name'] + ' was successfully listed!')
      except:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        db.session.rollback()

      finally:
        db.session.close() 
        return render_template('pages/home.html')



@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  result = Artist.query.filter(Artist.name.like(f'%{search_term}%'))
  response={
    "count": result.count(),
    "data": result
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.filter_by(id=artist_id).first()
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "facebook_link": artist.facebook_link,
    "seeking_performance": artist.seeking_performance_venues,
    "image_link": artist.image_link
  } 
  # shows the venue page with the given Venue_id
  # TODO: replace with real venue data from the venues table, using Venue_id
  return render_template('pages/show_artist.html', artist=data)
  

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  if form.validate_on_submit():
    form.populate_obj(artist)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  if form.validate_on_submit():
    form.populate_obj(venue)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
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
  new_artist = Artist(
    name = request.form.get('name'),
    city= request.form.get('city'),
    state=request.form.get('state'),
    phone=request.form.get('phone'),
    image_link=request.form.get('image_link'),
    genres=request.form.get('genres'),
    facebook_link=request.form.get('facebook_link')
  )
  try:
    db.session.add(new_artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('Artist ' + request.form['name'] + ' Unable to complete the request!')
    db.session.rollback()
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.all()
  show_info = []
  for show in shows:
    show = {
      "venue_id": Show.Venue_id,
      "venue_name":db.session.query(Venue.name).filter_by(id=show.Venue_id).first()[0],
      "artist_id": Show.Artist_id,
      "artist_name":db.session.query(Artist.name).filter_by(id=show.Artist_id).first()[0],
      "artist_image_link": db.session.query(Artist.image_link).filter_by(id=show.Artist_id),
      "show_date": format_datetime(str(show.show_date))
    }
    show_info.append(show)
  return render_template('pages/shows.html', shows=show_info)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  new_show = Show(
    Artist_id=get_value("artist_id"),
    Venue_id=get_value("venue_id"),
    show_date=get_value("start_time")
  )
  try:
    db.session.add(new_show)
    db.session.commit()
    flash('Show was successfully listed!')
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  # on successful db insert, flash success
  except:
    flash('An error occurred. Show could not be listed.')
    db.session.rollback()
  # TODO: on unsuccessful db insert, flash an error instead.
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
