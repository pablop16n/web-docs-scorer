from typing import List, Tuple
from docscorer.configuration import ScorerConfiguration
from docscorer.scorers.utils import get_threshold



class ShortSegmentsScorer:
    NO_SEGMENTS_SCORE = 0.0

    def __init__(self, config: ScorerConfiguration):
        self.config = config

    def search_short_segments(self, word_chars: List[int], menu_length: int) -> List[int]:
        initial_menu = 0
        for segment in word_chars:
            if segment <= menu_length:
                initial_menu += segment
            else:
                break
        final_menu = 0
        for segment in reversed(word_chars):
            if segment <= menu_length:
                final_menu += segment
            else:
                break
        return (initial_menu, final_menu)

    def score(self, ref_language: str, word_chars: List[int]) -> float:
        menu_length = get_threshold(self.config.MENUS_AVERAGE_LENGTH, ref_language)
        if not word_chars:
            return self.NO_SEGMENTS_SCORE
        initial_menu, final_menu = self.search_short_segments(word_chars, menu_length)
        short_segments_ratio = (initial_menu + final_menu) / sum(word_chars)
        score = 1 - (short_segments_ratio / 2)
        return score