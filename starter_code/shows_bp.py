from flask import (
    Blueprint,
    flash,
    render_template,
    request
)
from models import *
from forms import *

shows_bp = Blueprint('shows_bp', __name__)


@app.route('/shows')
def shows():

    shows = Show.query.all()
    data = []
    for show in shows:
        artist = Artist.query.get(show.artist_id)
        venue = Venue.query.get(show.venue_id)
        data.append({
            'venue_id': show.venue_id,
            'venue_name': venue.name,
            'artist_id': show.artist_id,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            'start_time': show.start_time
        })
    return render_template('pages/shows.html', shows=data)


@shows_bp.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@shows_bp.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    form = ShowForm(request.form)
    venue_id = form.venue_id.data
    artist_id = form.artist_id.data
    show_time = form.start_time.data

    try:
        show = Show(
            start_time=show_time,
            venue_id=venue_id,
            artist_id=artist_id
        )
        db.session.add(show)
        db.session.commit()

    except Exception as e:
        err = e
        print(f"Err => {err}")
        error = True
        db.session.rollback()
    if error:
        flash('Show was not listed!')
    else:
        flash('Show was successfully listed')
    return render_template('pages/home.html')
