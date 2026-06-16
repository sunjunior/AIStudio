import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class PublishedService(Base):
    __tablename__ = "published_services"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_id = Column(Integer, ForeignKey("models.id", ondelete="CASCADE"), nullable=False)
    service_type = Column(String(50), nullable=False)
    endpoint = Column(String(512), nullable=True)
    export_path = Column(String(512), nullable=True)
    config = Column(Text, default="{}")
    status = Column(String(50), nullable=False, default="stopped")
    pid = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    stopped_at = Column(DateTime, nullable=True)

    model = relationship("ModelRegistry")
