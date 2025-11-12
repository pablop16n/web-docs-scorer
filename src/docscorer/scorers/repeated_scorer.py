from docscorer.configuration import ScorerConfiguration
from docscorer.scorers.utils import get_threshold
from collections import Counter

class RepeatedScorer:
    MAX_SCORE = 1.0

    def __init__(self, config: ScorerConfiguration):
        self.config = config

    def score(self, document: str) -> float:
        segments = document.split("\n")
        segments = [seg for seg in segments if len(seg) > 4]
        if not segments:
            return self.MAX_SCORE
        occurr_per_seg = Counter(segments)
        repeated = sum(ocur for ocur in occurr_per_seg.values() if ocur > 1)
        repetition_ratio = repeated / len(segments)
        score = (1 - repetition_ratio)
        return score if score >= 0 else 0.0
