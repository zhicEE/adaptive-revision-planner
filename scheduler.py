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
