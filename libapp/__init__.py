from flask import Flask


def create_app():
    """
    Create app and configure the details
    :rtype : object
    """
    from libapp.config import libconf
    app = Flask(__name__, template_folder=libconf.TEMPLATE_DIR,
                static_folder=libconf.STATIC_PATH, static_url_path="")

    return app


def init_app(app):
    """
    Initializes app with needed configurations for add-on entities
        :param app: flask app object
    """
    from .init import loggerd, celeryd, redisd, shortnerd, sqld

    loggerd.init_app(app)
    celeryd = celeryd.init_app(app)
    redisd, pubsubd = redisd.init_app(app)
    shortnerd = shortnerd.init_app(app)
    db = sqld.init_app(app)

    return celeryd, redisd, pubsubd, shortnerd, db


app = create_app()
celeryd, redisd, pubsubd, shortnerd, sqld = init_app(app)

if app:
    from views import *
