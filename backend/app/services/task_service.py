from datetime import datetime

from sqlalchemy.orm import Session

from app.models.task import Task

from app.enums.task_enum import TaskStatus

from app.analytics.task_analytics import (
    get_task_summary
)


# =====================================================
# CREATE
# =====================================================

def create_task(
    db: Session,
    task_data: dict
):

    task = Task(
        **task_data
    )

    db.add(task)

    db.commit()

    db.refresh(task)

    return task


# =====================================================
# GET BY ID
# =====================================================

def get_task_by_id(
    db: Session,
    user_id: int,
    task_id: int
):

    return (

        db.query(Task)

        .filter(
            Task.user_id == user_id
        )

        .filter(
            Task.id == task_id
        )

        .first()

    )


# =====================================================
# GET ALL
# =====================================================

def get_all_tasks(
    db: Session,
    user_id: int
):

    return (

        db.query(Task)

        .filter(
            Task.user_id == user_id
        )

        .order_by(
            Task.due_date
        )

        .all()

    )


# =====================================================
# UPDATE
# =====================================================

def update_task(
    db: Session,
    user_id: int,
    task_id: int,
    task_data: dict
):

    task = get_task_by_id(
        db,
        user_id,
        task_id
    )

    if task is None:

        return None

    for key, value in task_data.items():

        setattr(
            task,
            key,
            value
        )

    db.commit()

    db.refresh(task)

    return task


# =====================================================
# DELETE
# =====================================================

def delete_task(
    db: Session,
    user_id: int,
    task_id: int
):

    task = get_task_by_id(
        db,
        user_id,
        task_id
    )

    if task is None:

        return False

    db.delete(task)

    db.commit()

    return True


# =====================================================
# COMPLETE TASK
# =====================================================

def complete_task(
    db: Session,
    user_id: int,
    task_id: int,
    actual_minutes: int
):

    task = get_task_by_id(
        db,
        user_id,
        task_id
    )

    if task is None:

        return None

    task.status = TaskStatus.COMPLETED

    task.actual_minutes = actual_minutes

    task.completed_at = datetime.utcnow()

    db.commit()

    db.refresh(task)

    return task


# =====================================================
# TODAY
# =====================================================

def get_today_tasks(
    db: Session,
    user_id: int
):

    today = datetime.now().date()

    tasks = (

        db.query(Task)

        .filter(
            Task.user_id == user_id
        )

        .all()

    )

    return [

        task

        for task in tasks

        if task.due_date.date() == today

    ]


# =====================================================
# PENDING
# =====================================================

def get_pending_tasks(
    db: Session,
    user_id: int
):

    return (

        db.query(Task)

        .filter(
            Task.user_id == user_id
        )

        .filter(
            Task.status != TaskStatus.COMPLETED
        )

        .order_by(
            Task.due_date
        )

        .all()

    )


# =====================================================
# COMPLETED
# =====================================================

def get_completed_tasks(
    db: Session,
    user_id: int
):

    return (

        db.query(Task)

        .filter(
            Task.user_id == user_id
        )

        .filter(
            Task.status == TaskStatus.COMPLETED
        )

        .order_by(
            Task.completed_at.desc()
        )

        .all()

    )


# =====================================================
# OVERDUE
# =====================================================

def get_overdue_tasks(
    db: Session,
    user_id: int
):

    return (

        db.query(Task)

        .filter(
            Task.user_id == user_id
        )

        .filter(
            Task.status != TaskStatus.COMPLETED
        )

        .filter(
            Task.due_date < datetime.utcnow()
        )

        .order_by(
            Task.due_date
        )

        .all()

    )


# =====================================================
# HIGH PRIORITY
# =====================================================

def get_high_priority_tasks(
    db: Session,
    user_id: int
):

    return (

        db.query(Task)

        .filter(
            Task.user_id == user_id
        )

        .filter(
            Task.status != TaskStatus.COMPLETED
        )

        .order_by(
            Task.priority.desc()
        )

        .all()

    )


# =====================================================
# ANALYTICS
# =====================================================

def get_task_analytics(
    db: Session,
    user_id: int
):

    tasks = (

        db.query(Task)

        .filter(
            Task.user_id == user_id
        )

        .order_by(
            Task.due_date
        )

        .all()

    )

    return get_task_summary(
        tasks
    )

# =====================================================
# TODAY'S TASKS
# =====================================================

def get_today_tasks_card(
    db: Session,
    user_id: int
):

    today = datetime.now().date()

    tasks = (

        db.query(Task)

        .filter(
            Task.user_id == user_id
        )

        .all()

    )

    return [

        task

        for task in tasks

        if task.due_date.date() == today

    ]

# =====================================================
# UPCOMING DEADLINES
# =====================================================

def get_upcoming_deadlines(
    db: Session,
    user_id: int,
    limit: int = 5
):

    return (

        db.query(Task)

        .filter(
            Task.user_id == user_id
        )

        .filter(
            Task.status != TaskStatus.COMPLETED
        )

        .order_by(
            Task.due_date
        )

        .limit(limit)

        .all()

    )