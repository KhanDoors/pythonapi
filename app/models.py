from .database import Base
from sqlalchemy import TIMESTAMP, Column, Integer, String, DateTime, Boolean, text, true


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String(100), nullable=False)
    content = Column(String(1000), nullable=False)
    published = Column(Boolean, server_default="True", nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))

    def __repr__(self):
        return f"<Post(id={self.id}, title={self.title}, content={self.content}, published={self.published}, created_at={self.created_at})>"
