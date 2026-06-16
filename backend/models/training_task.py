import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class TrainingTask(Base):
    __tablename__ = "training_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_id = Column(Integer, ForeignKey("models.id", ondelete="CASCADE"), nullable=False)
    method = Column(String(50), nullable=False)
    config = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    pid = Column(Integer, nullable=True)
    log_path = Column(String(512), default="")
    output_model_id = Column(Integer, ForeignKey("models.id", ondelete="SET NULL"), nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    model = relationship("ModelRegistry", foreign_keys=[model_id])
    output_model = relationship("ModelRegistry", foreign_keys=[output_model_id])
