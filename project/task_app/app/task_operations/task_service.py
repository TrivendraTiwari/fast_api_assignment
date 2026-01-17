
from sqlalchemy.orm import Session
from ..bg_tasks.email_tasks import send_email_notification
from task_app.app.database_setup import schemas
from task_app.app.database_setup import models
from uuid import UUID
from task_app.app.services_config.config import *

def create_task(db: Session, task_in: schemas.TaskCreate, user_id: str) -> models.Task:
    try:
        with db.begin(): 
            existing_task = db.query(models.Task).filter(
                models.Task.title == task_in.title,
                models.Task.user_id == user_id
            ).first()
            if existing_task:
                raise ValueError(f"Task with title '{task_in.title}' already exists for this user.")

            task = models.Task(
                title=task_in.title,
                description=task_in.description,
                status=task_in.status.value if hasattr(task_in.status, "value") else task_in.status,
                user_id=user_id
            )
            db.add(task)

            db.flush()
            db.refresh(task)  
        send_email_notification.delay(MAIL_SUBJECT, MAIL_BODY, TO_ADDRESS)
        return task

    except ValueError:
        raise  
    except Exception as e:
        print("ERROR in create_task:", e)
        raise



def get_task(db: Session, task_id: UUID, user_id: str) -> models.Task | None:
    return (
        db.query(models.Task)
        .filter(
            models.Task.id == task_id,
            models.Task.user_id == user_id.username
        )
        .first()
    )


def get_tasks(db: Session, page: int = 1, page_size: int = 10, user: str = None):
    q = db.query(models.Task)
    if user:
        q = q.filter(models.Task.user_id == user)

    total = q.count()
    items = (
        q.order_by(models.Task.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return total, items


def update_task(db: Session, task_id: UUID, updates: schemas.TaskUpdate, user_id: str):
    task = (
        db.query(models.Task)
        
        .filter(
            models.Task.id == task_id,
            models.Task.user_id == user_id.username
        )
        .first()
    )
    if not task:
        return None  

    if updates.title is not None:
        task.title = updates.title
    if updates.status is not None:
        task.status = updates.status.value if hasattr(updates.status, "value") else updates.status

    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: models.Task):
    db.delete(task)
    db.commit()
