from docscorer.configuration import ScorerConfiguration
from docscorer.scorers.utils import get_threshold, scale_value
import numpy as np

class ShortSegmentsScore:
    def __init__(self, config: ScorerConfiguration):
        self.config = config

    def score(self, ref_language: str, word_chars: list) -> float:
        # Almost 5 segments
        if len(word_chars) < 5:
            return 1.0
        long_text_length = get_threshold(self.config.LONG_TEXT_MIN, ref_language)
        word_chars = [long_text_length if x>long_text_length else x for x in word_chars] #long texts are capped to long_text_length because we need to on the fluctuation of short segments
        word_chars = np.array(word_chars)
        cv = np.std(word_chars) / np.mean(word_chars) # coefficient of variation
        score = 1 / (1 + cv.item())
        if score > 0.6:
            #low fluctuation in segments are not penalized
            return 1.0
        return scale_value(score, 0.0, 0.6, 0.5, 1.0) #is scaled between 0.5 and 1.0 to minimize the impact of this scorer

        
