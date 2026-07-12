from datetime import datetime

from app.enums.task_enum import (
    TaskPriority,
    TaskStatus,
)


# ======================================================
# Completion Rate
# ======================================================

def calculate_completion_rate(tasks):

    if not tasks:
        return 0.0

    completed = sum(
        1
        for task in tasks
        if task.status == TaskStatus.COMPLETED
    )

    return round(
        (completed / len(tasks)) * 100,
        2
    )


# ======================================================
# Overdue Tasks
# ======================================================

def calculate_overdue_tasks(tasks):

    now = datetime.now()

    overdue = []

    for task in tasks:

        if (
            task.due_date < now
            and task.status != TaskStatus.COMPLETED
        ):
            overdue.append(task)

    return overdue


# ======================================================
# High Priority Pending Tasks
# ======================================================

def calculate_high_priority_pending(tasks):

    result = []

    for task in tasks:

        if (
            task.priority == TaskPriority.HIGH
            and task.status != TaskStatus.COMPLETED
        ):
            result.append(task)

    return result


# ======================================================
# Average Completion Time
# ======================================================

def calculate_average_completion_time(tasks):

    completed_times = [
        task.actual_minutes
        for task in tasks
        if task.actual_minutes is not None
    ]

    if not completed_times:
        return 0

    return round(
        sum(completed_times) / len(completed_times),
        2
    )


# ======================================================
# Estimated vs Actual
# ======================================================

def calculate_estimated_vs_actual(tasks):

    estimated = sum(
        task.estimated_minutes
        for task in tasks
    )

    actual = sum(
        task.actual_minutes
        for task in tasks
        if task.actual_minutes is not None
    )

    return {
        "estimated": estimated,
        "actual": actual
    }


# ======================================================
# Productivity Score
# ======================================================

def calculate_productivity_score(
    completion_rate,
    overdue_count,
    high_priority_pending_count
):

    score = completion_rate

    score -= overdue_count * 5

    score -= high_priority_pending_count * 3

    return max(
        0,
        round(score, 2)
    )


# ======================================================
# Complete Task Analytics
# ======================================================

def get_task_summary(tasks):

    completion_rate = calculate_completion_rate(tasks)

    overdue_tasks = calculate_overdue_tasks(tasks)

    high_priority = calculate_high_priority_pending(tasks)

    average_completion = calculate_average_completion_time(tasks)

    estimated_actual = calculate_estimated_vs_actual(tasks)

    completed_tasks = sum(
        1
        for task in tasks
        if task.status == TaskStatus.COMPLETED
    )

    pending_tasks = len(tasks) - completed_tasks

    productivity_score = calculate_productivity_score(
        completion_rate,
        len(overdue_tasks),
        len(high_priority)
    )

    return {

        "total_tasks": len(tasks),

        "completed_tasks": completed_tasks,

        "pending_tasks": pending_tasks,

        "completion_rate": completion_rate,

        "overdue_tasks": len(overdue_tasks),

        "high_priority_pending": len(high_priority),

        "average_completion_time": average_completion,

        "estimated_vs_actual": estimated_actual,

        "productivity_score": productivity_score

    }