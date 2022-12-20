

from app.api.user import blueprint as user
from app.api.auth import blueprint as auth
from app.api.public import blueprint as public


def register(app):
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(user, url_prefix="/user")

    app.register_blueprint(public)


