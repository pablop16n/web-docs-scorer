from docscorer.configuration import ScorerConfiguration
from docscorer.scorers.utils import get_threshold


class RepeatedScorer:
    MAX_SCORE = 1.0

    def __init__(self, config: ScorerConfiguration):
        self.config = config

    def score(self, ref_language: str, document: str) -> float:
        menu_length = get_threshold(self.config.MENUS_AVERAGE_LENGTH, ref_language)

        segments = [line for line in document.split("\n") if len(line) >= menu_length]
        if not segments:
            return self.MAX_SCORE

        num_duplicates = len(segments) - len(set(segments))
        repetition_ratio = num_duplicates / len(segments)
        score = (1 - repetition_ratio)
        return score
