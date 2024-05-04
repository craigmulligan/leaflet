from typing import Optional
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[Optional[str]]
    is_email_confirmed: Mapped[Optional[bool]]

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, email={self.email!r}, is_email_confirmed={self.is_email_confirmed!r})"
