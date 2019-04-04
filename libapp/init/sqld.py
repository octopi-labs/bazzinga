from flask_sqlalchemy import SQLAlchemy

from libapp.config import sqlconf


def init_app(app):
    """Initialize application with sqlalchemy

    :param app: Reference to application
    :return: database connection
    """
    app.config["SQLALCHEMY_DATABASE_URI"] = sqlconf.DB_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_POOL_SIZE"] = sqlconf.DB_POOL_SIZE
    app.config["SQLALCHEMY_POOL_TIMEOUT"] = sqlconf.DB_POOL_TIMEOUT
    app.config["SQLALCHEMY_POOL_RECYCLE"] = sqlconf.DB_POOL_RECYCLE

    db = SQLAlchemy(app)
    return db
