from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Comment(Base):
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index = True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index = True)
    text: Mapped[str] = mapped_column(Text, nullable = False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("comments.id", ondelete="SET NULL"), nullable = True)    
    post: Mapped["Post"] = relationship("Post", back_populates="comments")
    author: Mapped["User"] = relationship("User", back_populates="comments")
    parent: Mapped[Optional["Comment"]] = relationship("Comment", back_populates="replies", remote_side="Comment.id")
    
    replies: Mapped[list["Comment"]] = relationship("Comment", back_populates="parent") 
    