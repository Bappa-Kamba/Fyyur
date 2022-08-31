import os

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


class DatabaseURI:
    SECRET_KEY = os.urandom(48)

    # Just change the names of your database and crendtials and
    # all to connect to your local system
    DATABASE_NAME = "fyyur"
    username = 'postgres'
    password = 'root'
    url = 'localhost:5432'
    drivername = 'postgresql'
    SQLALCHEMY_DATABASE_URI = "{}://{}:{}@{}/{}".format(
        drivername, username, password, url, DATABASE_NAME)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:root@localhost:5432/fyyur'
# SQLALCHEMY_TRACK_MODIFICATIONS = False
