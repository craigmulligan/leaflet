import re
from typing import Optional
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, validates
from itsdangerous import URLSafeTimedSerializer
from .config  import SECRET_KEY

class BaseModel(DeclarativeBase):
    pass

class User(BaseModel):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[Optional[str]]
    is_email_confirmed: Mapped[Optional[bool]]
    email_regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    salt_signin = "signin"

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, email={self.email!r}, is_email_confirmed={self.is_email_confirmed!r})"

    def __init__(self, email):
        self.email = email 

    @staticmethod
    def _get_serializer(salt: str) -> URLSafeTimedSerializer:
        """Gets a URLSafeSerializer"""
        return URLSafeTimedSerializer(SECRET_KEY, salt=salt)

    @staticmethod
    def verify_signin_token(token: str):
        """
        Verify token - used for magic links
        with 30 min expiry.
        """
        return User._get_serializer(User.salt_signin).loads(token, max_age=30 * 60)

    def get_signin_token(self):
        """Used for sessions"""
        return self._get_serializer(User.salt_signin).dumps(self.id)

    @validates("email")
    def validate_email(self, _, address):
        if not re.fullmatch(self.email_regex, address):
            raise ValueError("Invalid Email")

        return address
