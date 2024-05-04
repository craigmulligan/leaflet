import re
from typing import Optional
from sqlalchemy import ForeignKey, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, validates
from itsdangerous import URLSafeTimedSerializer
from .config  import SECRET_KEY

class BaseModel(DeclarativeBase):
    created_at: Mapped[str] = mapped_column(DateTime, default=func.now(), nullable=False)

class User(BaseModel):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[Optional[str]]
    is_email_confirmed: Mapped[Optional[bool]]
    email_regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    salt_signin = "signin"

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


class Leaflet(BaseModel):
    __tablename__ = "leaflet"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))

class UserSettings(BaseModel):
    __tablename__ = "user_account_setting"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    prompt: Mapped[str]

class Recipe(BaseModel):
    __tablename__ = "recipe"
    id: Mapped[int] = mapped_column(primary_key=True)
    leaflet_id: Mapped[int] = mapped_column(ForeignKey("leaflet.id"))
    title: Mapped[str]
    servings: Mapped[int]
    description: Mapped[str]
    estimated_time: Mapped[int] # time in mins 
    image: Mapped[str]

class RecipeItem(BaseModel):
    __tablename__ = "recipe_item"
    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipe.id"))
    description: Mapped[str]
    step: Mapped[int]

class ShoppingList(BaseModel):
    __tablename__ = "shopping_list"
    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipe.id"))

class ShoppingListItem(BaseModel):
    __tablename__ = "shopping_list_item"
    id: Mapped[int] = mapped_column(primary_key=True)
    shopping_list_id: Mapped[int] = mapped_column(ForeignKey("shopping_list.id"))
    description: Mapped[str]
    unit: Mapped[str]
    amount: Mapped[int]
