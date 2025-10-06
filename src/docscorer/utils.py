import re
from typing import List


def join_utf_blocks(u_list: List[str], inverse: bool = False) -> re.Pattern[str]:
    inversion = "^" if inverse else ""
    prefixes = ["u", "U000"]
    pattern = f"[{inversion}"
    for x in u_list:
        prefix = prefixes[0] if len(x) == 9 else prefixes[1]
        cases = f'\\{prefix}{x.split("-")[0]}-\\{prefix}{x.split("-")[1]}'
        pattern = f"{pattern}{cases}"
    return re.compile(f"{pattern}]")


def custom_mean(neg_values: List[float]) -> float:
    # Negative values
    minor1 = min(neg_values)
    neg_values.remove(minor1)
    minor2 = min(neg_values)
    neg_values.remove(minor2)
    return minor1 * minor2 * (sum(neg_values) / len(neg_values))


def average(numbers: List[float]) -> float:
    return round(sum(numbers) / len(numbers), 3)
