from flask import (
    Blueprint,
    render_template
)
from models import (
    Venue,
    Artist
)

index_bp = Blueprint('index_bp', __name__)


@index_bp.route('/')
def index():
    venues = Venue.query.order_by((Venue.id)).limit(10).all()
    artists = Artist.query.order_by((Artist.id)).limit(10).all()

    return render_template('pages/home.html', venues=venues, artists=artists)
