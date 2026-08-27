from models import ScheduledBlock, ScheduleResult
from datetime import timedelta


def calculate_remaining(estimated_minutes, completed_minutes):
    if estimated_minutes <= 0:
        raise ValueError("Estimated minutes must be positive")

    if completed_minutes < 0 or completed_minutes > estimated_minutes:
        raise ValueError("Completed minutes are invalid")

    return estimated_minutes - completed_minutes


def calculate_unscheduled(remaining_minutes, available_minutes):
    if remaining_minutes < 0:
        raise ValueError("Remaining minutes must not be negative")

    if available_minutes < 0:
        raise ValueError("Available minutes must not be negative")

    return max(remaining_minutes - available_minutes, 0)


def sort_tasks_by_priority(tasks):
    return sorted(tasks, key=lambda task: (task.deadline, -task.importance, task.task_id))


def schedule_tasks(tasks, availability_windows):
    task = tasks[0]
    window = availability_windows[0]

    window_minutes = int(
        (window.end - window.start).total_seconds() / 60
    )

    allocated_minutes = min(
        window_minutes,
        task.remaining_minutes,
        task.max_session_minutes,
    )

    block_end = window.start + timedelta(
        minutes=allocated_minutes
    )

    unscheduled_minutes = (
        task.remaining_minutes - allocated_minutes
    )

    scheduled_block = ScheduledBlock(
        task_id=task.task_id,
        start=window.start,
        end=block_end,
        allocated_minutes=allocated_minutes,
    )

    return ScheduleResult(
        scheduled_blocks=[scheduled_block],
        unscheduled_minutes=unscheduled_minutes,
    )
