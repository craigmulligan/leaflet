from datetime import datetime
import re
from typing import Optional, List
from sqlalchemy import ForeignKey, DateTime, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    validates,
)
from pgvector.sqlalchemy import Vector
from itsdangerous import URLSafeTimedSerializer
from .config import SECRET_KEY


class BaseModel(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )


class User(BaseModel):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[Optional[str]]
    is_email_confirmed: Mapped[Optional[bool]]
    prompt: Mapped[Optional[str]]

    email_regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    salt_signin = "signin"

    leaflets: Mapped[List["Leaflet"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

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
    user = relationship(User, back_populates="leaflets")

    recipes: Mapped[List["Recipe"]] = relationship(
        back_populates="leaflet", cascade="all, delete-orphan"
    )


class Recipe(BaseModel):
    __tablename__ = "recipe"
    id: Mapped[int] = mapped_column(primary_key=True)
    leaflet_id: Mapped[int] = mapped_column(ForeignKey("leaflet.id"))
    title: Mapped[str]
    servings: Mapped[int]
    description: Mapped[str]
    estimated_time: Mapped[int]  # time in mins
    image: Mapped[Optional[str]]

    leaflet = relationship(Leaflet)

    ingredients: Mapped[List["RecipeIngredient"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan"
    )
    steps: Mapped[List["RecipeStep"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan"
    )
    shopping_list_items: Mapped[List["ShoppingListItem"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"""{self.title}: {self.description}"""


class RecipeStep(BaseModel):
    __tablename__ = "recipe_step"
    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipe.id"))
    description: Mapped[str]
    index: Mapped[int]

    recipe = relationship(Recipe)


class RecipeIngredient(BaseModel):
    __tablename__ = "recipe_ingredient"
    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipe.id"))
    description: Mapped[str]
    unit: Mapped[str]
    amount: Mapped[float]

    recipe = relationship(Recipe)


class ShoppingListItem(BaseModel):
    __tablename__ = "shopping_list_item"
    id: Mapped[int] = mapped_column(primary_key=True)
    shopping_list_id: Mapped[int] = mapped_column(ForeignKey("recipe.id"))
    description: Mapped[str]
    unit: Mapped[str]
    amount: Mapped[float]

    recipe = relationship(Recipe)


class RecipeEmbedding(BaseModel):
    __tablename__ = "recipe_embedding"
    id: Mapped[int] = mapped_column(primary_key=True)
    # By default, the length of the embedding vector
    # will be 1536 for text-embedding-3-small
    embedding: Mapped[List[float]] = mapped_column(Vector(1536))
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipe.id"))
    recipe = relationship(Recipe)
