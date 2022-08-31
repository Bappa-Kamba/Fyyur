from datetime import datetime
import re
from xml.dom import ValidationErr
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for
)
from models import *
import dateutil.parser
from forms import *

venues_bp = Blueprint('venues_bp', __name__)


def validate_phone(phone):
    phone_num = '^([0-9]{3})[-][0-9]{3}[-][0-9]{4}$'
    match = re.search(phone_num, phone)
    if not match:
        raise ValidationErr('Error, phone number must be in format'
                            ' xxx-xxx-xxxx')


@venues_bp.route('/venues')
def venues():
    # some snippets here were from a github repo I stumbled upon
    venues = Venue.query.group_by(Venue.id).order_by(Venue.state).all()
    venue_set = set()
    data = []

    for venue in venues:
        #  num_upcoming_shows = 0
        venue_set.add((venue.city, venue.state))

    for venue in venue_set:
        data.append({
            'city': venue[0],
            'state': venue[1],
            'venues': []
        })
    for venue in venues:
        num_upcoming_shows = 0

        shows = Show.query.filter_by(venue_id=venue.id).all()
        for show in shows:
            if dateutil.parser.parse(show.start_time) > datetime.now():
                num_upcoming_shows += 1

        for value in data:
            if venue.city == value['city'] and venue.state == value['state']:
                value['venues'].append({
                    'id': venue.id,
                    'name': venue.name,
                    'num_upcoming_shows': num_upcoming_shows
                })
    return render_template('pages/venues.html', areas=data)


@venues_bp.route('/venues/search', methods=['POST'])
def search_venues():
    # implement search on venues with partial string search.
    # Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and
    # "Park Square Live Music & Coffee"
    # some snippets here were from a github repo I stumbled upon

    search_term = request.form.get('search_term', '')
    venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

    # print(venues)
    response = {
        'count': len(venues),
        'data': []
    }

    for venue in venues:
        num_upcoming_shows = 0

        shows = Show.query.filter_by(venue_id=venue.id).all()

        for show in shows:
            if dateutil.parser.parse(show.start_time) > datetime.now():
                num_upcoming_shows += 1

        response['data'].append({
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': num_upcoming_shows,
        })
    return render_template(
        'pages/search_venues.html',
        results=response,
        search_term=request.form.get(
            'search_term',
            ''))


@venues_bp.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # replace with real venue data from the venues table, using venue_id

    venue = Venue.query.get(venue_id)
    upcoming_show = []
    past_show = []

    shows = Show.query.join(Venue).filter_by(
        id=venue_id).order_by(
        Venue.name).all()

    for show in shows:
        artist = Artist.query.get(show.venue_id)
        if dateutil.parser.parse(show.start_time) > datetime.now():
            upcoming_show.append({
                "artist_id": show.artist_id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": show.start_time
            })

    for show in shows:
        artist = Artist.query.get(show.venue_id)
        if dateutil.parser.parse(show.start_time) < datetime.now():
            past_show.append({
                "artist_id": show.artist_id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": show.start_time
            })

    data = {
        'id': venue.id,
        'name': venue.name,
        'city': venue.city,
        'genres': venue.genres,
        'address': venue.address,
        'state': venue.state,
        'phone': venue.phone,
        'website': venue.website_link,
        'facebook_link': venue.facebook_link,
        'image_link': venue.image_link,
        'seeking_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_description,
        'upcoming_shows': upcoming_show,
        'past_shows': past_show,
        'upcoming_shows_count': len((upcoming_show)),
        'past_shows_count': len((past_show))
    }
    return render_template('pages/show_venue.html', venue=data)


@venues_bp.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@venues_bp.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form)
    error = False
    name = form.name.data
    city = form.city.data
    state = form.state.data
    address = form.address.data
    phone = form.phone.data
    image_link = form.image_link.data
    venue_genres = form.genres.data
    facebook_link = form.facebook_link.data
    website_link = form.website_link.data
    seeking_talent = form.seeking_talent.data
    seeking_description = form.seeking_description.data
    # print(name,' ', city, ' ', state, ' ',
    #  phone, ' ', image_link, ' ',
    #  genres, ' ', facebook_link,
    #   ' ', website_link, ' ', seeking_venue,
    #    ' ', seeking_description
    #  )

    try:
        validate_phone(phone)
        venue = Venue(
            name=name,
            city=city,
            state=state,
            phone=phone,
            address=address,
            image_link=image_link,
            genres=venue_genres,
            facebook_link=facebook_link,
            website_link=website_link,
            seeking_talent=seeking_talent,
            seeking_description=seeking_description)
        db.session.add(venue)
        db.session.commit()

    except Exception as e:
        flash('Error, phone number must be in format (xxx-xxx-xxxx)')
        err = e
        print(f"Err => {err}")
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if not error:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    else:
        flash(
            'Something went wrong! Venue ' +
            request.form['name'] +
            ' could not be listed.')
    return render_template('pages/home.html')


@venues_bp.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit
    # could fail.

    venue = Venue.query.get(venue_id)
    name = venue.name
    error = False
    try:

        db.session.delete(venue)
        db.session.commit()

    except BaseException:
        error = True
        db.session.rollback()
    finally:
        db.session.close()

    if error:
        flash('An error ocuured. Venue ' + name + ' could not be deleted!')

    else:
        flash('Venue ' + name + '  deleted successfully.')

    return redirect(url_for('index'))


@venues_bp.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    venue = Venue.query.get(venue_id)

    venue = {
        'id': venue.id,
        'name': venue.name,
        'genres': venue.genres,
        'address': venue.address,
        'city': venue.city,
        'state': venue.state,
        'phone': venue.phone,
        'website_link': venue.website_link,
        'facebook_link': venue.facebook_link,
        'seeking_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_description,
        'image_link': venue.image_link

    }
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@venues_bp.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm(request.form)
    error = False
    venue = Venue.query.get(venue_id)
    try:
        venue.name = form.name.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.phone = form.phone.data
        venue.image_link = form.image_link.data
        venue.genres = form.genres.data
        venue.address = form.address.data
        venue.facebook_link = form.facebook_link.data
        venue.website_link = form.website_link.data
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data
        validate_phone(venue.phone)

        db.session.commit()
    except Exception as e:
        flash('Error, phone number must be in format (08012345678)')
        err = e
        print(f"Err => {err}")
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        flash(
            'Venue ' +
            request.form['name'] +
            ' was not successfully updated!')
    else:
        flash('Venue ' + request.form['name'] + ' was successfully updated!')

    return redirect(url_for('show_venue', venue_id=venue_id))
