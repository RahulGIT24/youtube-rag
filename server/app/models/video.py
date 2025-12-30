from sqlalchemy.orm import Mapped, mapped_column,relationship
from sqlalchemy import String,Boolean
from app.core.database import Base
from datetime import datetime
from typing import List,TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user_to_videos import UserToVideos

class Video(Base):
    __tablename__ = "videos"

    video_id: Mapped[str] = mapped_column(primary_key=True)
    video_url: Mapped[str] = mapped_column(String(50),unique=True)
    ready:Mapped[bool]=mapped_column(Boolean,default=False)
    processing: Mapped[bool] = mapped_column(Boolean, default=False)
    enqueued:Mapped[bool]=mapped_column(Boolean,default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    saved_by_users: Mapped[List["UserToVideos"]] = relationship(
        back_populates="video"
    )