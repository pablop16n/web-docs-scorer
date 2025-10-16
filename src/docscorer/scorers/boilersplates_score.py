from docscorer.configuration import ScorerConfiguration
from docscorer.scorers.utils import get_threshold, scale_value
import numpy as np

class BoilerScore:
    def __init__(self, config: ScorerConfiguration):
        self.config = config

    def score(self, ref_language: str, word_chars: list) -> float:
        num_segments = len(word_chars)
        # Almost 5 segments
        if num_segments < 5:
            return False
        menu_length = get_threshold(self.config.MENUS_AVERAGE_LENGTH, ref_language)
        arr = np.array(word_chars)
        idx_max = np.argmax(arr)
        before = arr[:idx_max]
        after = arr[idx_max:]
    
        if len(before) < 2 or len(after) < 2:
            return False
    
        # Correlation with a growing or decreasing sequence
        x_before = np.arange(len(before))
        x_after = np.arange(len(after))
    
        # before grows and after decrease
        correl_before = np.corrcoef(x_before, before)[0, 1]
        correl_after = np.corrcoef(x_after, after)[0, 1]
        if correl_before < 0.5 or correl_after > -0.5:
            return False
    
        # symmetry of the curve
        if abs(len(before) - len(after)) / len(word_chars) > 0.5:
            return False
        
        # At this point is a bell curve, now we determinate the number of possible boilerplate segments
        
        average = (sum(word_chars)/len(word_chars) + menu_length)/2 #Average of all segments except for the biggest, and approached to the menu_length value using another average
        boilerplates = []
        
        # before
        for n in range(len(word_chars)):
            if (word_chars[n]+word_chars[n+1])/2 < average:
                boilerplates.append(n)
            else:
                break
        # after
        for n in reversed(range(len(word_chars))):
            if word_chars[n] < average:
                boilerplates.append(n)
            else:
                break
        num_boilerplates = len(boilerplates)
        if num_boilerplates < 5:
            return False
        score = (abs(num_boilerplates/num_segments - 1) + 3) / 4
        return score
        # return (score, boilerplates)
        

        
