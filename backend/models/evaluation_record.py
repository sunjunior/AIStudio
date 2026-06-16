import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class EvaluationRecord(Base):
    __tablename__ = "evaluation_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_id = Column(Integer, ForeignKey("models.id", ondelete="CASCADE"), nullable=False)
    eval_type = Column(String(50), nullable=False)
    dataset = Column(String(512), default="")
    metrics = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="pending")
    log_path = Column(String(512), default="")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    model = relationship("ModelRegistry")
