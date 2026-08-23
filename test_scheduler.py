import unittest

from scheduler import calculate_remaining, calculate_unscheduled


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


if __name__ == "__main__":
    unittest.main()