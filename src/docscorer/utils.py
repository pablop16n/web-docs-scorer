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
    return sum(numbers) / len(numbers)

def remove_delimitators(punct_chars: list, word_chars: list, number_chars: list) -> list:
    if len(punct_chars) != len(word_chars) or len(punct_chars) != len(number_chars):
        return punct_chars
    punct_without_delimitators = []
    for n in range(len(punct_chars)):
        if not number_chars[n] and not word_chars[n] and punct_chars[n] > 5:
            #is a delimitator
            punct_without_delimitators.append(0)
        else:
            punct_without_delimitators.append(punct_chars[n])
    return punct_without_delimitators
