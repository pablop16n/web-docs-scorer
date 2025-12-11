from typing import Any


def get_threshold(
    table: dict[str, Any], language: str, default_key: str = "standard"
) -> Any:
    """Fetch a language-specific threshold, falling back to `default_key`."""
    try:
        script = language.split("_")[1]
        if language in table:
            return table[language]
        elif script in table:
            return table[script]
        else:
            return table[default_key]
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


def penalize_accumulation(analyzed_chars: list, word_chars: list, not_penalized: 
                          int, hard_penalized: int) -> float:
    problem_chars = 0
    for n in range(len(analyzed_chars)):
        n_word_ch = word_chars[n]
        n_analyzed = analyzed_chars[n]
        if analyzed_chars[n] < 10:
            continue
        if not n_word_ch or n_analyzed/n_word_ch > 0.1:
            candidate_num = n_analyzed - n_word_ch
            problem_chars=candidate_num if candidate_num > problem_chars else problem_chars
    if problem_chars <= not_penalized:
        return 1.0
    elif problem_chars > hard_penalized:
        return 0.0
    return scale_value(problem_chars, not_penalized, hard_penalized, 1.0, 0.0)
        
