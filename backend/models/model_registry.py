import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class ModelRegistry(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    source = Column(String(50), nullable=False)
    source_path = Column(String(512), default="")
    model_type = Column(String(50), nullable=False)
    base_model_id = Column(Integer, ForeignKey("models.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(50), nullable=False, default="ready")
    local_path = Column(String(512), default="")
    description = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    base_model = relationship("ModelRegistry", remote_side=[id], backref="adapters")
