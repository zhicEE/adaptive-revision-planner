from dataclasses import dataclass
from datetime import datetime


@dataclass
class Task:
    task_id: str
    estimated_minutes: int
    completed_minutes: int
    deadline: datetime
    importance: int
    min_session_minutes: int
    max_session_minutes: int

    def __post_init__(self):
        if self.estimated_minutes <= 0:
            raise ValueError("Estimated minutes must be positive")

        if self.completed_minutes > self.estimated_minutes:
            raise ValueError("Completed minutes cannot exceed estimated minutes")

        if self.completed_minutes < 0:
            raise ValueError("Completed minutes cannot be negative")
        if self.importance < 1 or self.importance > 5:
            raise ValueError("Importance must be between 1 and 5")

    @property
    def remaining_minutes(self):
        return self.estimated_minutes - self.completed_minutes


@dataclass
class AvailabilityWindow:
    start: datetime
    end: datetime

    def __post_init__(self):
        if self.start >= self.end:
            raise ValueError("End time must be after start time")


@dataclass
class ScheduledBlock:
    task_id: str
    start: datetime
    end: datetime
    allocated_minutes: int


@dataclass
class ScheduleResult:
    scheduled_blocks: list[ScheduledBlock]
    unscheduled_minutes: int
