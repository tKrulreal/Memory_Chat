import re


def parse_duration_days(value: str | None) -> int | None:
    """Convert compact setting durations such as 1w or 3m to days."""
    if not value or value.lower() == "unlimited":
        return None

    match = re.fullmatch(r"\s*(\d+)\s*([dwmy])\s*", value.lower())
    if not match:
        return None

    amount = int(match.group(1))
    days_per_unit = {"d": 1, "w": 7, "m": 30, "y": 365}
    return amount * days_per_unit[match.group(2)]
