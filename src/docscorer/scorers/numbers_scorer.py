from docscorer.configuration import ScorerConfiguration
from docscorer.scorers.utils import get_threshold, scale_value, penalize_accumulation


class NumsScorer:
    def __init__(self, config: ScorerConfiguration):
        self.config = config

    def score(self, ref_language: str, num_numbers: int, num_word_chars: int,
              number_chars: list, word_chars: list) -> float:
        if num_word_chars == 0:
            return 0.0

        percent_max = get_threshold(self.config.NUMBERS_PERCENT_MAX, ref_language)
        percent_desired = get_threshold(self.config.NUMBERS_PERCENT_DESIRED, ref_language)

        ratio = round((num_numbers / num_word_chars) * 100, 1)

        
        if ratio >= percent_max:
            return 0.0
        
        accumulation = penalize_accumulation(analyzed_chars=number_chars, word_chars=word_chars,
                                            not_penalized=self.config.ACCUM_NUMBERS_NOT_PENALIZED,
                                            hard_penalized=self.config.ACCUM_NUMBERS_HARD_PENALIZED)

        if ratio <= percent_desired:
            return 1.0 * accumulation
        return scale_value(ratio, percent_desired, percent_max, 1.0, 0.0) * accumulation

    
    
