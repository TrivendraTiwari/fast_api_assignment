# app/models.py
import enum
import uuid
from sqlalchemy import Column, String, Enum, DateTime,Integer,Index,Text,UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

import enum
import uuid
from sqlalchemy import Column, String, Enum, DateTime,Boolean, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
    
class TaskStatus(enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"    
    rejected = "rejected"
    

class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String, nullable=True)
    status = Column(
        Enum(TaskStatus, name="task_status", native_enum=False),
        nullable=False,
        server_default=TaskStatus.pending.value
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    __table_args__ = (
        Index("idx_tasks_created_at", "created_at"),
        Index("idx_tasks_status", "status"),
    )
