"""
Unit tests for app/analytics/task_analytics.py -- pure business logic,
no database needed. Uses lightweight fake objects instead of real Task
model instances since these functions only touch a handful of attributes.
"""
from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest

from app.analytics.task_analytics import (
    calculate_completion_rate,
    calculate_overdue_tasks,
    calculate_high_priority_pending,
    calculate_average_completion_time,
    calculate_estimated_vs_actual,
    calculate_productivity_score,
    get_task_summary,
)
from app.enums.task_enum import TaskStatus, TaskPriority


def fake_task(
    status=TaskStatus.TODO,
    priority=TaskPriority.MEDIUM,
    due_date=None,
    estimated_minutes=30,
    actual_minutes=None,
):
    return SimpleNamespace(
        status=status,
        priority=priority,
        due_date=due_date or (datetime.now() + timedelta(days=1)),
        estimated_minutes=estimated_minutes,
        actual_minutes=actual_minutes,
    )


class TestCompletionRate:
    def test_empty_list_returns_zero(self):
        assert calculate_completion_rate([]) == 0.0

    def test_all_completed_is_100_percent(self):
        tasks = [fake_task(status=TaskStatus.COMPLETED) for _ in range(3)]
        assert calculate_completion_rate(tasks) == 100.0

    def test_partial_completion(self):
        tasks = [
            fake_task(status=TaskStatus.COMPLETED),
            fake_task(status=TaskStatus.TODO),
            fake_task(status=TaskStatus.IN_PROGRESS),
            fake_task(status=TaskStatus.COMPLETED),
        ]
        # 2 of 4 completed = 50%
        assert calculate_completion_rate(tasks) == 50.0

    def test_returns_percentage_not_fraction(self):
        # Regression guard: this value is a 0-100 percentage. A caller
        # (e.g. a frontend) multiplying it by 100 again is a real bug we
        # hit once already -- this test pins the contract.
        tasks = [fake_task(status=TaskStatus.COMPLETED)]
        rate = calculate_completion_rate(tasks)
        assert 0 <= rate <= 100


class TestOverdueTasks:
    def test_past_due_incomplete_task_is_overdue(self):
        tasks = [
            fake_task(
                due_date=datetime.now() - timedelta(days=1),
                status=TaskStatus.TODO,
            )
        ]
        assert len(calculate_overdue_tasks(tasks)) == 1

    def test_past_due_completed_task_is_not_overdue(self):
        tasks = [
            fake_task(
                due_date=datetime.now() - timedelta(days=1),
                status=TaskStatus.COMPLETED,
            )
        ]
        assert len(calculate_overdue_tasks(tasks)) == 0

    def test_future_due_task_is_not_overdue(self):
        tasks = [
            fake_task(
                due_date=datetime.now() + timedelta(days=1),
                status=TaskStatus.TODO,
            )
        ]
        assert len(calculate_overdue_tasks(tasks)) == 0


class TestHighPriorityPending:
    def test_high_priority_incomplete_counts(self):
        tasks = [fake_task(priority=TaskPriority.HIGH, status=TaskStatus.TODO)]
        assert len(calculate_high_priority_pending(tasks)) == 1

    def test_high_priority_completed_does_not_count(self):
        tasks = [
            fake_task(priority=TaskPriority.HIGH, status=TaskStatus.COMPLETED)
        ]
        assert len(calculate_high_priority_pending(tasks)) == 0

    def test_low_priority_does_not_count(self):
        tasks = [fake_task(priority=TaskPriority.LOW, status=TaskStatus.TODO)]
        assert len(calculate_high_priority_pending(tasks)) == 0


class TestAverageCompletionTime:
    def test_no_completed_tasks_returns_zero(self):
        tasks = [fake_task(actual_minutes=None)]
        assert calculate_average_completion_time(tasks) == 0

    def test_averages_only_tasks_with_actual_minutes(self):
        tasks = [
            fake_task(actual_minutes=30),
            fake_task(actual_minutes=60),
            fake_task(actual_minutes=None),  # should be excluded
        ]
        assert calculate_average_completion_time(tasks) == 45.0


class TestEstimatedVsActual:
    def test_sums_estimated_and_actual_separately(self):
        tasks = [
            fake_task(estimated_minutes=30, actual_minutes=45),
            fake_task(estimated_minutes=20, actual_minutes=None),
        ]
        result = calculate_estimated_vs_actual(tasks)
        assert result == {"estimated": 50, "actual": 45}


class TestProductivityScore:
    def test_perfect_completion_no_penalties(self):
        assert calculate_productivity_score(100, 0, 0) == 100

    def test_overdue_tasks_reduce_score(self):
        assert calculate_productivity_score(100, 2, 0) == 90

    def test_high_priority_pending_reduces_score(self):
        assert calculate_productivity_score(100, 0, 2) == 94

    def test_score_never_goes_negative(self):
        assert calculate_productivity_score(10, 10, 10) == 0


class TestGetTaskSummary:
    def test_summary_shape_and_values(self):
        tasks = [
            fake_task(status=TaskStatus.COMPLETED, actual_minutes=30),
            fake_task(
                status=TaskStatus.TODO,
                priority=TaskPriority.HIGH,
                due_date=datetime.now() - timedelta(days=1),
            ),
        ]

        summary = get_task_summary(tasks)

        assert summary["total_tasks"] == 2
        assert summary["completed_tasks"] == 1
        assert summary["pending_tasks"] == 1
        assert summary["overdue_tasks"] == 1
        assert summary["high_priority_pending"] == 1
        assert "estimated_vs_actual" in summary
        assert "productivity_score" in summary
