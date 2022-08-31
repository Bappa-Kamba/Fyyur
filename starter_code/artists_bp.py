import re
from xml.dom import ValidationErr
from flask import (
    Blueprint,
    flash,
    request,
    redirect,
    url_for,
    render_template
)
import dateutil
from models import *
from forms import *


artists_bp = Blueprint('artists_bp', __name__)


def validate_phone(phone):
    phone_num = '^([0-9]{3})[-][0-9]{3}[-][0-9]{4}$'
    match = re.search(phone_num, phone)
    if not match:
        raise ValidationErr('Error, phone number must be in format'
                            ' xxx-xxx-xxxx')


@artists_bp.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@artists_bp.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form

    form = ArtistForm(request.form)
    error = False
    name = form.name.data
    city = form.city.data
    state = form.state.data
    phone = form.phone.data
    image_link = form.image_link.data
    genres = form.genres.data
    facebook_link = form.facebook_link.data
    website_link = form.website_link.data
    seeking_venue = form.seeking_venue.data
    seeking_description = form.seeking_description.data
    # print(name,' ', city, ' ', state, ' ',
    #  phone, ' ', image_link, ' ',
    #  genres, ' ', facebook_link,
    #   ' ', website_link, ' ', seeking_venue,
    #    ' ', seeking_description
    #  )
    print(state)
    print(genres)
    try:
        validate_phone(phone)
        artist = Artist(
            name=name,
            city=city,
            state=state,
            phone=phone,
            image_link=image_link,
            genres=genres,
            facebook_link=facebook_link,
            website_link=website_link,
            seeking_venue=seeking_venue,
            seeking_description=seeking_description)
        db.session.add(artist)
        db.session.commit()

    except Exception as e:
        err = e
        flash('Error, phone number must be in format (08012345678)')
        print(f"Err => {err}")
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if not error:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    else:
        flash('Something went wrong!')
    return render_template('pages/home.html')


@artists_bp.route('/artist/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):

    # SQLAlchemy ORM to delete a record. Handle cases where the session commit
    # could fail.

    artist = Artist.query.get(artist_id)
    name = artist.name
    error = False
    try:

        db.session.delete(artist)
        db.session.commit()

    except BaseException:
        error = True
        db.session.rollback()
    finally:
        db.session.close()

    if error:
        flash('An error ocuured. Artist ' + name + ' could not be deleted!')

    else:
        flash('Artist ' + name + '  deleted successfully.')

    return redirect(url_for('/artists'))


@artists_bp.route('/artists')
def artists():
    # some snippets here were from a github repo I stumbled upon

    artists = Artist.query.order_by(Artist.id).all()
    data = []
    for artist in artists:
        data.append({
            'id': artist.id,
            'name': artist.name
        })
    return render_template('pages/artists.html', artists=data)


@artists_bp.route('/artists/search', methods=['POST'])
def search_artists():
    #  implement search on artists with partial string search.
    #  Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado",
    # and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    search_term = request.form.get('search_term', '')
    artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
    # venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

    # print(artists)
    response = {
        'count': len(artists),
        'data': []
    }

    for artist in artists:
        num_upcoming_shows = 0

        shows = Show.query.filter_by(artist_id=artist.id).all()

        for show in shows:
            if dateutil.parser.parse(show.start_time) > datetime.now():
                num_upcoming_shows += 1

        response['data'].append({
            'id': artist.id,
            'name': artist.name,
            'num_upcoming_shows': num_upcoming_shows,
        })

    return render_template(
        'pages/search_artists.html',
        results=response,
        search_term=request.form.get(
            'search_term',
            ''))


@artists_bp.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # replace with real artist data from the artist table, using artist_id

    artist = Artist.query.get(artist_id)
    upcoming_shows = []
    past_shows = []

    shows = Show.query.join(Artist).filter_by(
        id=artist_id).order_by(
        Artist.name).all()

    for show in shows:
        venue = Venue.query.get(show.venue_id)
        if dateutil.parser.parse(show.start_time) > datetime.now():
            upcoming_shows.append({
                "venue_id": show.venue_id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": show.start_time
            })

    for show in shows:
        venue = Venue.query.get(show.venue_id)
        if dateutil.parser.parse(show.start_time) < datetime.now():
            past_shows.append({
                "venue_id": show.venue_id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": show.start_time
            })

    data = {
        'id': artist.id,
        'name': artist.name,
        'city': artist.city,
        'genres': artist.genres,
        'state': artist.state,
        'phone': artist.phone,
        'website': artist.website_link,
        'facebook_link': artist.facebook_link,
        'image_link': artist.image_link,
        'seeking_venue': artist.seeking_venue,
        'seeking_description': artist.seeking_description,
        'upcoming_shows': upcoming_shows,
        'past_shows': past_shows,
        'upcoming_shows_count': len((upcoming_shows)),
        'past_shows_count': len((past_shows))
    }
    return render_template('pages/show_artist.html', artist=data)


@artists_bp.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm(request.form)

    artist = Artist.query.get(artist_id)
    artist = {
        'id': artist.id,
        'name': artist.name,
        'genres': artist.genres,
        'city': artist.city,
        'state': artist.state,
        'phone': artist.phone,
        'website': artist.website_link,
        'facebook_link': artist.facebook_link,
        'seeking_venue': artist.seeking_venue,
        'seeking_description': artist.seeking_description,
        'image_link': artist.image_link,

    }
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@artists_bp.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

    form = ArtistForm(request.form)
    error = False
    artist = Artist.query.get(artist_id)
    try:
        artist.name = form.name.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.image_link = form.image_link.data
        artist.genres = form.genres.data
        artist.facebook_link = form.facebook_link.data
        artist.website_link = form.website_link.data
        artist.seeking_venue = form.seeking_venue.data
        artist.seeking_description = form.seeking_description.data
        validate_phone(artist.phone)

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

    return redirect(url_for('show_artist', artist_id=artist_id))
