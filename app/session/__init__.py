from typing import Optional
from flask import session as flask_session


class Session:
    """
    wrapper around flask.session
    """
    def is_authenticated(self) -> bool:
        return "user_id" in flask_session 

    def get_authenticated_user_id(self) -> Optional[int]:
        return flask_session.get("user_id")


session = Session()
