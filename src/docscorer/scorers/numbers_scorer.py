from docscorer.configuration import ScorerConfiguration
from docscorer.scorers.utils import get_threshold, scale_value


class NumsScorer:
    def __init__(self, config: ScorerConfiguration):
        self.config = config

    def score(self, ref_language: str, num_numbers: int, num_word_chars: int) -> float:
        if num_word_chars == 0:
            return 0.0

        percent_max = get_threshold(self.config.NUMBERS_PERCENT_MAX, ref_language)
        percent_bad = get_threshold(self.config.NUMBERS_PERCENT_BAD, ref_language)
        percent_semibad = get_threshold(
            self.config.NUMBERS_PERCENT_SEMIBAD, ref_language
        )
        percent_desired = get_threshold(
            self.config.NUMBERS_PERCENT_DESIRED, ref_language
        )

        ratio = round((num_numbers / num_word_chars) * 100, 1)

        if ratio <= percent_desired:
            return 1.0
        if ratio >= percent_bad:
            ratio = min(ratio, percent_max)
            return scale_value(ratio, percent_max, percent_bad, 0.0, 0.5)
        if ratio >= percent_semibad:
            return scale_value(ratio, percent_bad, percent_semibad, 0.5, 0.7)
        return scale_value(ratio, percent_semibad, percent_desired, 0.7, 1.0)
