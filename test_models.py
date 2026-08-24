import unittest
from datetime import datetime

from models import Task


class TaskTests(unittest.TestCase):
    def test_stores_task_data(self):
        deadline = datetime(2026, 8, 25, 15, 0)

        task = Task(
            task_id="English",
            estimated_minutes=90,
            completed_minutes=25,
            deadline=deadline,
            importance=5,
        )

        self.assertEqual(task.task_id, "English")
        self.assertEqual(task.estimated_minutes, 90)
        self.assertEqual(task.completed_minutes, 25)
        self.assertEqual(task.deadline, deadline)
        self.assertEqual(task.importance, 5)

    def test_calculates_remaining_minutes(self):
        task = Task(
            "English",
            90,
            25,
            deadline=datetime(2026, 8, 25, 15, 0),
            importance=3,
        )

        self.assertEqual(task.remaining_minutes, 65)

    def test_rejects_completed_minutes_above_estimate(self):
        with self.assertRaises(ValueError):
            Task(
                "English",
                90,
                100,
                deadline=datetime(2026, 8, 25, 15, 0),
                importance=3,
            )

    def test_rejects_negative_completed_minutes(self):
        with self.assertRaises(ValueError):
            Task(
                "English",
                90,
                -5,
                deadline=datetime(2026, 8, 25, 15, 0),
                importance=3,
            )

    def test_rejects_zero_estimated_minutes(self):
        with self.assertRaises(ValueError):
            Task(
                "English",
                0,
                0,
                deadline=datetime(2026, 8, 25, 15, 0),
                importance=3,
            )

    def test_allows_zero_completed_minutes(self):
        task = Task(
            "English",
            90,
            0,
            deadline=datetime(2026, 8, 25, 15, 0),
            importance=3,
        )

        self.assertEqual(task.completed_minutes, 0)
        self.assertEqual(task.remaining_minutes, 90)

    def test_rejects_importance_below_one(self):
        with self.assertRaises(ValueError):
            Task(
                "English",
                90,
                25,
                deadline=datetime(2026, 8, 25, 15, 0),
                importance=0,
            )

    def test_rejects_importance_above_five(self):
        with self.assertRaises(ValueError):
            Task(
                "English",
                90,
                25,
                deadline=datetime(2026, 8, 25, 15, 0),
                importance=6,
            )


if __name__ == "__main__":
    unittest.main()
