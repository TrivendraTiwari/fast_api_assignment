from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_utils.cbv import cbv
from sqlalchemy.orm import Session
from sqlalchemy import text
from uuid import UUID
from fastapi import HTTPException, status
from task_app.app.database_setup.db_session import get_db
from task_app.app.services_config.redis_config import get_cache, set_cache, rate_limiter
from task_app.app.services_config.rbac_keycloack import require_role
from task_app.app.task_operations.task_service import create_task,get_task,get_tasks,update_task,delete_task
from task_app.app.database_setup import schemas
from sqlalchemy.exc import SQLAlchemyError
router = APIRouter(tags=["Tasks"])


@cbv(router)
class TaskAPI:
    """
    Task-related APIs (Class Based View)
    """

    db: Session = Depends(get_db)

    @router.post(
        "/tasks",
        response_model=schemas.TaskOut,
        status_code=status.HTTP_201_CREATED
    )
    def create_task(
        self,
        task_in: schemas.TaskCreate,
        user=Depends(require_role("admin", "user")),
        _=Depends(rate_limiter)
    ):  
        try:
            return create_task(
                self.db,
                task_in,
                user.username
            )

        except ValueError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create task"
            )

    @router.get(
    "/tasks",
    response_model=schemas.PaginatedTasks,
    status_code=status.HTTP_200_OK
)
    def list_tasks(
        self,
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100),
        user=Depends(require_role("admin", "user")),
        _=Depends(rate_limiter)
    ):
        cache_key = f"user:{user.username}:tasks:{page}:{page_size}"
        try:
            cached_data = get_cache(cache_key)
            if cached_data:
                print(cached_data,'cached_data')

                return cached_data

            total, items = get_tasks(
                self.db,
                page=page,
                page_size=page_size,
                user=user.username
            )

            response = schemas.PaginatedTasks(
                total=total,
                page=page,
                page_size=page_size,
                items=items
            )

            response_dict = response.model_dump()

            for item in response_dict.get("items", []):
                if isinstance(item.get("id"), UUID):
                    item["id"] = str(item["id"])

            set_cache(cache_key, response_dict, ttl=60)

            return response

        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch tasks"
            )

    @router.get(
    "/tasks/{id}",
    response_model=schemas.TaskOut,
    status_code=status.HTTP_200_OK
)
    def get_task(
        self,
        id: UUID,
        user=Depends(require_role("admin", "user")),
        _=Depends(rate_limiter)
    ):
        try:
            task = get_task(
                self.db,
                id,
                user
            )
            print(task,'task')
            if task is None:
                print('yes')
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found"
                )
            return task
        except HTTPException:
            raise
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database service unavailable"
            )

        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch task"
            )

    @router.patch(
    "/tasks/{id}",
    response_model=schemas.TaskOut,
    status_code=status.HTTP_200_OK
)
    def update_task(
        self,
        id: UUID,
        updates: schemas.TaskUpdate,
        user=Depends(require_role("admin", "user")),
        _=Depends(rate_limiter)
    ):
        try:
            task = get_task(
                self.db,
                id,
                user
            )

            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found"
                )

            return update_task(
                self.db,
                id,
                updates,
                user
            )
        except HTTPException:
            raise
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database service unavailable"
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update task"
            )

    @router.delete(
    "/tasks/{id}",
    status_code=status.HTTP_204_NO_CONTENT
)
    def delete_task(
        self,
        id: UUID,
        user=Depends(require_role("admin")),
        _=Depends(rate_limiter)
    ):
        try:
            task = get_task(
                self.db,
                id,
                user
            )

            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found"
                )

            delete_task(self.db, task)
            return None
        except HTTPException:
            raise

        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database service unavailable"
            )

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete task"
            )
