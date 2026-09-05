import scheduler
import unittest

from scheduler import calculate_remaining, calculate_unscheduled, sort_tasks_by_priority
from datetime import datetime
from models import Task, AvailabilityWindow


class SchedulerTests(unittest.TestCase):
    def test_returns_remaining_minutes(self):
        self.assertEqual(calculate_remaining(120, 30), 90)

    def test_rejects_completed_minutes_above_estimate(self):
        with self.assertRaises(ValueError):
            calculate_remaining(120, 130)

    def test_rejects_negative_completed_minutes(self):
        with self.assertRaises(ValueError):
            calculate_remaining(120, -10)

    def test_rejects_non_positive_estimated_minutes(self):
        with self.assertRaises(ValueError):
            calculate_remaining(0, 0)

        with self.assertRaises(ValueError):
            calculate_remaining(-10, 0)

    def test_returns_zero_when_task_is_complete(self):
        self.assertEqual(calculate_remaining(60, 60), 0)

    def test_calculates_unscheduled_minutes(self):
        self.assertEqual(calculate_unscheduled(90, 60), 30)

    def test_unscheduled_minutes_never_go_below_zero(self):
        self.assertEqual(calculate_unscheduled(60, 90), 0)

    def test_rejects_negative_remaining_minutes(self):
        with self.assertRaises(ValueError):
            calculate_unscheduled(-10, 60)

    def test_rejects_negative_available_minutes(self):
        with self.assertRaises(ValueError):
            calculate_unscheduled(60, -10)

    def test_sorts_higher_importance_first_when_deadlines_are_equal(self):
        deadline = datetime(2026, 8, 25, 15, 0)

        t1 = Task(
            "T1",
            60,
            0,
            deadline=deadline,
            importance=5,
            min_session_minutes=30,
            max_session_minutes=60,
        )

        t2 = Task(
            "T2",
            60,
            0,
            deadline=deadline,
            importance=3,
            min_session_minutes=30,
            max_session_minutes=60,
        )

        ordered_tasks = sort_tasks_by_priority([t2, t1])
        actual_ids = [task.task_id for task in ordered_tasks]

        self.assertEqual(actual_ids, ["T1", "T2"])

    def test_uses_task_id_as_tie_breaker_when_deadline_and_importance_are_equal(self):
        deadline = datetime(2026, 8, 25, 15, 0)

        t1 = Task(
            "T1",
            60,
            0,
            deadline=deadline,
            importance=3,
            min_session_minutes=30,
            max_session_minutes=60,
        )

        t2 = Task(
            "T2",
            60,
            0,
            deadline=deadline,
            importance=3,
            min_session_minutes=30,
            max_session_minutes=60,
        )

        ordered_tasks = sort_tasks_by_priority([t2, t1])
        actual_ids = [task.task_id for task in ordered_tasks]

        self.assertEqual(actual_ids, ["T1", "T2"])

    def test_sorts_earlier_deadline_before_higher_importance(self):

        t1 = Task(
            "T1",
            60,
            0,
            deadline=datetime(2026, 8, 25, 11, 0),
            importance=2,
            min_session_minutes=30,
            max_session_minutes=60,
        )

        t2 = Task(
            "T2",
            60,
            0,
            deadline=datetime(2026, 8, 25, 15, 0),
            importance=5,
            min_session_minutes=30,
            max_session_minutes=60,
        )

        ordered_tasks = sort_tasks_by_priority([t2, t1])
        actual_ids = [task.task_id for task in ordered_tasks]

        self.assertEqual(actual_ids, ["T1", "T2"])

    def test_schedules_one_task_that_fits_exactly(self):
        t1 = Task(
            "T1",
            60,
            0,
            deadline=datetime(2026, 8, 25, 12, 0),
            importance=3,
            min_session_minutes=30,
            max_session_minutes=60,
        )

        window = AvailabilityWindow(
            start=datetime(2026, 8, 25, 10, 0),
            end=datetime(2026, 8, 25, 11, 0),
        )

        result = scheduler.schedule_tasks(
            tasks=[t1],
            availability_windows=[window],
        )

        self.assertEqual(len(result.scheduled_blocks), 1)

        block = result.scheduled_blocks[0]

        self.assertEqual(block.task_id, "T1")
        self.assertEqual(block.start, datetime(2026, 8, 25, 10, 0))
        self.assertEqual(block.end, datetime(2026, 8, 25, 11, 0))
        self.assertEqual(block.allocated_minutes, 60)
        self.assertEqual(result.unscheduled_minutes, 0)
        self.assertEqual(result.unscheduled_work, [])

    def test_reports_unscheduled_minutes_when_capacity_is_insufficient(self):
        t1 = Task(
            "English",
            120,
            30,
            deadline=datetime(2026, 8, 25, 12, 0),
            importance=3,
            min_session_minutes=30,
            max_session_minutes=60,
        )

        window = AvailabilityWindow(
            start=datetime(2026, 8, 25, 10, 0),
            end=datetime(2026, 8, 25, 11, 0),
        )

        result = scheduler.schedule_tasks(
            tasks=[t1],
            availability_windows=[window]
        )

        self.assertEqual(len(result.scheduled_blocks), 1)

        block = result.scheduled_blocks[0]

        self.assertEqual(block.start, datetime(2026, 8, 25, 10, 0))
        self.assertEqual(block.end, datetime(2026, 8, 25, 11, 0))
        self.assertEqual(block.allocated_minutes, 60)
        self.assertEqual(result.unscheduled_minutes, 30)

        self.assertEqual(len(result.unscheduled_work), 1)

        unscheduled = result.unscheduled_work[0]

        self.assertEqual(unscheduled.task_id, "English")
        self.assertEqual(unscheduled.remaining_minutes, 30)
        self.assertEqual(
            unscheduled.reason_code,
            "INSUFFICIENT_CAPACITY"
        )

    def test_does_not_schedule_window_shorter_than_minimum_session(self):
        t1 = Task(
            "T1",
            60,
            0,
            deadline=datetime(2026, 8, 25, 12, 0),
            importance=3,
            min_session_minutes=30,
            max_session_minutes=60,
        )

        window = AvailabilityWindow(
            start=datetime(2026, 8, 25, 10, 0),
            end=datetime(2026, 8, 25, 10, 20),
        )

        result = scheduler.schedule_tasks(
            tasks=[t1],
            availability_windows=[window]
        )

        self.assertEqual(result.scheduled_blocks, [])
        self.assertEqual(result.unscheduled_minutes, 60)
        self.assertEqual(len(result.unscheduled_work), 1)

        unscheduled = result.unscheduled_work[0]

        self.assertEqual(unscheduled.task_id, "T1")
        self.assertEqual(unscheduled.remaining_minutes, 60)
        self.assertEqual(
            unscheduled.reason_code,
            "SESSION_TOO_SHORT"
        )

    def test_schedules_window_equal_to_minimum_session(self):
        t1 = Task(
            "T1",
            60,
            0,
            deadline=datetime(2026, 8, 25, 12, 0),
            importance=3,
            min_session_minutes=30,
            max_session_minutes=60,
        )

        window = AvailabilityWindow(
            start=datetime(2026, 8, 25, 10, 0),
            end=datetime(2026, 8, 25, 10, 30),
        )

        result = scheduler.schedule_tasks(
            tasks=[t1],
            availability_windows=[window]
        )

        self.assertEqual(len(result.scheduled_blocks), 1)

        block = result.scheduled_blocks[0]

        self.assertEqual(block.start, datetime(2026, 8, 25, 10, 0))
        self.assertEqual(block.end, datetime(2026, 8, 25, 10, 30))
        self.assertEqual(block.allocated_minutes, 30)
        self.assertEqual(result.unscheduled_minutes, 30)

        self.assertEqual(len(result.unscheduled_work), 1)

        unscheduled = result.unscheduled_work[0]

        self.assertEqual(unscheduled.task_id, "T1")
        self.assertEqual(unscheduled.remaining_minutes, 30)
        self.assertEqual(
            unscheduled.reason_code,
            "INSUFFICIENT_CAPACITY"
        )

if __name__ == "__main__":
    unittest.main()
