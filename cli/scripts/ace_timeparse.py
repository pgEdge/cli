import re
from datetime import timedelta

import ace_config as config


def parse_time_string(time_str):
    """
    Convert a time string like "5 min", "1 hr", "30 s", "2 w" into a timedelta object.

    Args:
    time_str (str): A string representing a time duration.

    Returns:
    timedelta: A timedelta object representing the parsed duration.

    Raises:
    ValueError: If the input string format is invalid.
    """
    # Define a regular expression pattern to match the input format
    pattern = (
        r"^(\d+)\s*(s|sec(s)?|second(s)?|m|min(s)?|minute(s)?|"
        r"h|hr(s)?|hour(s)?|w|wk(s)?|week(s)?)$"
    )

    # Try to match the pattern
    match = re.match(pattern, time_str.strip().lower())

    if not match:
        raise ValueError(f"Invalid time string format: {time_str}")

    # Extract the numeric value and unit
    match_groups = [g for g in match.groups() if g is not None]
    value, unit = match_groups

    if not value.isdigit():
        raise ValueError(f"Invalid time string format: {time_str}")

    value = int(value)
    frequency = None

    # Convert to timedelta based on the unit
    if unit in ["s", "sec", "secs", "seconds"]:
        frequency = timedelta(seconds=value)
    elif unit in ["m", "min", "mins", "minutes"]:
        frequency = timedelta(minutes=value)
    elif unit in ["h", "hr", "hrs", "hours"]:
        frequency = timedelta(hours=value)
    elif unit in ["w", "wk", "wks", "weeks"]:
        frequency = timedelta(weeks=value)
    else:
        raise ValueError(f"Unsupported time unit: {unit}")

    if frequency < config.MIN_RUN_FREQUENCY:
        raise ValueError("Minimum frequency is 5 minutes")

    return frequency
