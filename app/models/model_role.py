from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.db_database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")
    users = relationship("User", secondary="user_roles", back_populates="roles", viewonly=True)
