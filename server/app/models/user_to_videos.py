from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from app.core.database import Base
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.video import Video

class UserToVideos(Base):
    __tablename__ = "user_to_videos"

    id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    video_id: Mapped[str] = mapped_column(ForeignKey("videos.video_id"), nullable=False)
    user_id:Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relations
    user:Mapped["User"]=relationship(back_populates="saved_videos")
    video: Mapped["Video"] = relationship(back_populates="saved_by_users")