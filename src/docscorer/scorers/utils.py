from typing import Any


def get_threshold(
    table: dict[str, Any], language: str, default_key: str = "standard"
) -> Any:
    """Fetch a language-specific threshold, falling back to `default_key`."""
    try:
        return table.get(language, table[default_key])
    except KeyError:
        raise KeyError(
            f"Neither '{language}' nor default '{default_key}' found in {table}."
        ) from None


def scale_value(
    value: float,
    min_value: float,
    max_value: float,
    min_score: float,
    max_score: float,
) -> float:
    """Scale a value linearly into a score range."""
    if min_value == max_value:
        return 0.0

    ratio = (value - min_value) / (max_value - min_value)
    score = ratio * (max_score - min_score) + min_score
    return score
