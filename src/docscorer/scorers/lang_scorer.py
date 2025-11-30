import sys

from typing import List, Optional

from docscorer.configuration import ScorerConfiguration
from docscorer.scorers.utils import get_threshold


class LangScorer:
    def __init__(self, config: ScorerConfiguration):
        self.config = config

    def score(
        self,
        ref_language: str,
        lang_segments: List[str],
        word_chars: List[int],
        id: str,
    ) -> float:
        if len(lang_segments) != len(
            word_chars
        ):
            return 0  # Errors from unmatched scores
        menu_length = get_threshold(self.config.MENUS_AVERAGE_LENGTH, ref_language)
        correct_lang_chars = 0
        wrong_lang_chars = 0
        available_chars = False
        for n in range(len(lang_segments)):
            if word_chars[n] <= menu_length:
                available_chars = True
                continue
            elif lang_segments[n] == ref_language:
                correct_lang_chars += word_chars[n]
            else:
                wrong_lang_chars += word_chars[n]
        if correct_lang_chars == 0:
            if not available_chars:
                # print(
                #     f"Doc_name: '{id}' - No available segments have been found on "
                #     "the target language\n"
                #     f"- Language: '{ref_language}' - Segment_languages: "
                #     f"{set(lang_segments)}", file=sys.stderr
                # )
                return 0.0

            else:
                if all([x == ref_language for x in lang_segments]):
                    return 1.0
                # print(
                #     f"Doc_name: '{id}' - "
                #     "Only too short segments have been found on the target language"
                #  , file=sys.stderr   	
                # )
                return 0.0
        results = correct_lang_chars / (correct_lang_chars + wrong_lang_chars)
        return min(results, 1.0)
