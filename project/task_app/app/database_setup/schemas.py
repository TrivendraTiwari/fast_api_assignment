from pydantic import BaseModel, Field, constr
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum

class StatusEnum(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"    
    rejected = "rejected"    

class TaskCreate(BaseModel):
    title: constr(min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[StatusEnum] = StatusEnum.pending

class TaskUpdate(BaseModel):
    title: Optional[constr(min_length=1, max_length=255)] = None
    status: Optional[StatusEnum] = None

class TaskOut(BaseModel):
    id: UUID
    title: str
    description: str | None = None
    status: StatusEnum
    

    class Config:
        from_attributes = True  
        
class PaginatedTasks(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[TaskOut]

    class Config:
        from_attributes = True
        