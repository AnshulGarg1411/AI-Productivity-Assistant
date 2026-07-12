import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import TaskRow from "../TaskRow";

const baseTask = {
  id: 1,
  title: "Write report",
  description: "Quarterly summary",
  priority: "HIGH",
  category: "WORK",
  status: "TODO",
  due_date: new Date(Date.now() + 1000 * 60 * 60 * 24).toISOString(), // tomorrow
  estimated_minutes: 30,
};

describe("TaskRow", () => {
  it("renders the title, priority, and category badges", () => {
    render(
      <TaskRow task={baseTask} onComplete={vi.fn()} onEdit={vi.fn()} onDelete={vi.fn()} />
    );

    expect(screen.getByText("Write report")).toBeInTheDocument();
    expect(screen.getByText("HIGH")).toBeInTheDocument();
    expect(screen.getByText("WORK")).toBeInTheDocument();
  });

  it("shows an Overdue badge when due date has passed and task is incomplete", () => {
    const overdueTask = {
      ...baseTask,
      due_date: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(), // yesterday
      status: "TODO",
    };

    render(
      <TaskRow task={overdueTask} onComplete={vi.fn()} onEdit={vi.fn()} onDelete={vi.fn()} />
    );

    expect(screen.getByText("Overdue")).toBeInTheDocument();
  });

  it("does NOT show an Overdue badge for a completed task, even if past due", () => {
    const completedPastDue = {
      ...baseTask,
      due_date: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
      status: "COMPLETED",
    };

    render(
      <TaskRow task={completedPastDue} onComplete={vi.fn()} onEdit={vi.fn()} onDelete={vi.fn()} />
    );

    expect(screen.queryByText("Overdue")).not.toBeInTheDocument();
  });

  it("does NOT show an Overdue badge for a future due date", () => {
    render(
      <TaskRow task={baseTask} onComplete={vi.fn()} onEdit={vi.fn()} onDelete={vi.fn()} />
    );

    expect(screen.queryByText("Overdue")).not.toBeInTheDocument();
  });

  it("calls onComplete when the completion circle is clicked on an incomplete task", () => {
    const onComplete = vi.fn();
    render(
      <TaskRow task={baseTask} onComplete={onComplete} onEdit={vi.fn()} onDelete={vi.fn()} />
    );

    fireEvent.click(screen.getByTitle("Mark as complete"));

    expect(onComplete).toHaveBeenCalledWith(baseTask);
  });

  it("does not call onComplete again for an already-completed task", () => {
    const onComplete = vi.fn();
    const completedTask = { ...baseTask, status: "COMPLETED" };

    render(
      <TaskRow task={completedTask} onComplete={onComplete} onEdit={vi.fn()} onDelete={vi.fn()} />
    );

    fireEvent.click(screen.getByTitle("Completed"));

    expect(onComplete).not.toHaveBeenCalled();
  });

  it("renders the title with a strikethrough style once completed", () => {
    const completedTask = { ...baseTask, status: "COMPLETED" };
    render(
      <TaskRow task={completedTask} onComplete={vi.fn()} onEdit={vi.fn()} onDelete={vi.fn()} />
    );

    expect(screen.getByText("Write report")).toHaveClass("line-through");
  });

  it("calls onEdit and onDelete with the task when their buttons are clicked", () => {
    const onEdit = vi.fn();
    const onDelete = vi.fn();

    const { container } = render(
      <TaskRow task={baseTask} onComplete={vi.fn()} onEdit={onEdit} onDelete={onDelete} />
    );

    const buttons = container.querySelectorAll("button");
    // Order in TaskRow: [complete circle, edit, delete]
    fireEvent.click(buttons[1]);
    fireEvent.click(buttons[2]);

    expect(onEdit).toHaveBeenCalledWith(baseTask);
    expect(onDelete).toHaveBeenCalledWith(baseTask);
  });
});
