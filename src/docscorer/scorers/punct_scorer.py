from docscorer.configuration import ScorerConfiguration
from docscorer.scorers.utils import get_threshold, scale_value


class PunctScorer:
    def __init__(self, config: ScorerConfiguration):
        self.config = config

    def penalize_lack_punct_segm(self, punct_chars: list, word_chars: list, num_word_chars: int, not_penalized: float, percent_bad: float) -> float:
        bad_segm = 0
        for n in range(len(punct_chars)):
            n_word_seg = word_chars[n]
            n_punct_seg = punct_chars[n]
            if not n_word_seg or n_word_seg <= not_penalized:
                continue
            ratio = round((n_punct_seg / n_word_seg) * 100, 1)
            if ratio < percent_bad:
                bad_segm += n_word_seg
        proportion_bad = bad_segm/num_word_chars
        if proportion_bad < 0.05:
            return 1
        elif proportion_bad > 0.4:
            return 0
        elif proportion_bad > 0.05 and proportion_bad < 0.2:
            return scale_value(proportion_bad, 0.2, 0.05, 0.6, 1.0)
        else:
            return scale_value(proportion_bad, 0.4, 0.2, 0, 0.6)

    def score(
        self, ref_language: str, num_punctuation_chars: int, num_word_chars: int, punct_chars: list, 
        word_chars: list) -> float:
        if not num_word_chars or len(punct_chars) != len(word_chars):
            return 0.0

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
        
        score = 0.0
        if ratio >= percent_bad[0] or ratio <= percent_bad[1]:
            return 0.0
        elif percent_desired_min <= ratio <= percent_desired_max:
            score = 1.0
        elif ratio <= percent_semibad:
            score = scale_value(ratio, percent_bad[1], percent_semibad, 0.0, 0.5) 
        elif ratio <= percent_desired_min:
            score = scale_value(
                ratio, percent_semibad, percent_desired_min, 0.5, 1.0
            )
        elif ratio >= percent_desired_max:
            score = scale_value(
                ratio, percent_desired_max, percent_bad[0], 1.0, 0.0
            )
        if score < 0.3:
            return score
        
        menu_length = get_threshold(self.config.MENUS_AVERAGE_LENGTH, ref_language)
        penalize_lack_punct_segm = self.penalize_lack_punct_segm(punct_chars=punct_chars, word_chars=word_chars, num_word_chars=num_word_chars, not_penalized=menu_length*3, percent_bad=percent_semibad)
        return min(score, penalize_lack_punct_segm)
