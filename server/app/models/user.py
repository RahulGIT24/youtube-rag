from sqlalchemy.orm import Mapped, mapped_column,relationship
from sqlalchemy import String,Boolean,DateTime
from datetime import datetime
from typing import List,TYPE_CHECKING
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user_to_videos import UserToVideos

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(100))
    is_verified:Mapped[bool] = mapped_column(Boolean,default=False)
    verification_token:Mapped[str]= mapped_column(String(100),nullable=True)
    verification_token_sent_at:Mapped[datetime | None]=mapped_column(DateTime(timezone=True),nullable=True,default=None)
    forgot_password_token:Mapped[str]= mapped_column(String(100),nullable=True)
    refresh_token:Mapped[str]= mapped_column(String(100),nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relations
    saved_videos: Mapped[List["UserToVideos"]] = relationship(back_populates="user",cascade="all, delete-orphan")