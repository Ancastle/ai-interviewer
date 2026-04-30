from datetime import datetime, timezone
from sqlalchemy import DateTime, String, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class SessionStatus(enum.Enum):
    in_progress = "in_progress"
    completed = "completed"


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    model: Mapped[str] = mapped_column(String(100))
    status: Mapped[SessionStatus] = mapped_column(SAEnum(SessionStatus), default=SessionStatus.in_progress)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    messages: Mapped[list["Message"]] = relationship(back_populates="session", cascade="all, delete-orphan")
    documents: Mapped[list["Document"]] = relationship(back_populates="session", cascade="all, delete-orphan")
