from docscorer.configuration import ScorerConfiguration
from docscorer.scorers.utils import get_threshold, scale_value


class PunctScorer:
    MAX_SCORE = 1.0
    MIN_SCORE = 0.0

    def __init__(self, config: ScorerConfiguration):
        self.config = config

    def score(
        self, ref_language: str, num_punctuation_chars: int, num_word_chars: int
    ) -> float:
        if num_word_chars == 0:
            return 0.0

        percent_max = get_threshold(self.config.PUNCTUATION_PERCENT_MAX, ref_language)
        percent_bad = get_threshold(self.config.PUNCTUATION_PERCENT_BAD, ref_language)
        percent_semibad = get_threshold(
            self.config.PUNCTUATION_PERCENT_SEMIBAD, ref_language
        )
        percent_desired_max = get_threshold(
            self.config.PUNCTUATION_PERCENT_DESIRED_MAX, ref_language
        )
        percent_desired_min = get_threshold(
            self.config.PUNCTUATION_PERCENT_DESIRED_MIN, ref_language
        )

        ratio = round((num_punctuation_chars / num_word_chars) * 100, 1)

        if percent_desired_min <= ratio <= percent_desired_max:
            return self.MAX_SCORE
        elif ratio >= percent_bad[0]:
            ratio = min(ratio, percent_max)
            return scale_value(ratio, percent_max, percent_bad[0], self.MIN_SCORE, 0.5)
        elif ratio >= percent_semibad[0]:
            return scale_value(ratio, percent_bad[0], percent_semibad[0], 0.5, 0.7)
        elif ratio > percent_desired_max:
            return scale_value(
                ratio, percent_semibad[0], percent_desired_max, 0.7, self.MAX_SCORE
            )
        elif ratio >= percent_semibad[1]:
            return scale_value(
                ratio, percent_semibad[1], percent_desired_min, 0.5, self.MAX_SCORE
            )
        else:
            return scale_value(ratio, 0.0, percent_semibad[1], self.MIN_SCORE, 0.5)
