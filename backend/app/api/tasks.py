from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.core.dependencies import (
    get_current_user
)

from app.models.user import User

from app.schemas.task_schema import (
    TaskCreate,
    TaskResponse,
    TaskAnalyticsResponse,
)

from app.services.task_service import (
    create_task,
    get_all_tasks,
    get_task_by_id,
    update_task,
    delete_task,
    complete_task,
    get_today_tasks,
    get_pending_tasks,
    get_completed_tasks,
    get_task_analytics
)

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


# ======================================================
# Get All Tasks
# ======================================================

@router.get(
    "/",
    response_model=list[TaskResponse]
)
def fetch_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return get_all_tasks(db, current_user.id)


# ======================================================
# Create Task
# ======================================================

@router.post(
    "/",
    response_model=TaskResponse
)
def add_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    task_data = task.model_dump()
    # Always trust the logged-in user, not whatever the client sends
    task_data["user_id"] = current_user.id

    return create_task(
        db,
        task_data
    )


# ======================================================
# Today's Tasks
# ======================================================

@router.get(
    "/today",
    response_model=list[TaskResponse]
)
def today_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return get_today_tasks(db, current_user.id)


# ======================================================
# Pending Tasks
# ======================================================

@router.get(
    "/pending",
    response_model=list[TaskResponse]
)
def pending_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return get_pending_tasks(db, current_user.id)


# ======================================================
# Completed Tasks
# ======================================================

@router.get(
    "/completed",
    response_model=list[TaskResponse]
)
def completed_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return get_completed_tasks(db, current_user.id)


# ======================================================
# Update Task
# ======================================================

@router.put(
    "/{task_id}",
    response_model=TaskResponse
)
def edit_task(
    task_id: int,
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    updated_task = update_task(
        db,
        current_user.id,
        task_id,
        task.model_dump()
    )

    if updated_task is None:

        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return updated_task


# ======================================================
# Complete Task
# ======================================================

@router.patch(
    "/{task_id}/complete",
    response_model=TaskResponse
)
def finish_task(
    task_id: int,
    actual_minutes: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    task = complete_task(
        db,
        current_user.id,
        task_id,
        actual_minutes
    )

    if task is None:

        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task


# ======================================================
# Delete Task
# ======================================================

@router.delete("/{task_id}")
def remove_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    deleted = delete_task(
        db,
        current_user.id,
        task_id
    )

    if not deleted:

        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return {
        "message": "Task deleted successfully."
    }

# ======================================================
# Task Analytics
# ======================================================

@router.get(
    "/analytics",
    response_model=TaskAnalyticsResponse
)
def task_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return get_task_analytics(db, current_user.id)
# ======================================================
# Get Task By ID
# KEEP THIS ROUTE LAST
# ======================================================

@router.get(
    "/{task_id}",
    response_model=TaskResponse
)
def fetch_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    task = get_task_by_id(
        db,
        current_user.id,
        task_id
    )

    if task is None:

        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task