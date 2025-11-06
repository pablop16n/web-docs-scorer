import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import math
import pandas as pd

from docscorer.configuration import ScorerConfiguration
from docscorer.scorers.singular_chars_scorer import SingularCharsScorer
from docscorer.scorers.informativeness_scorer import InformativenessScorer
from docscorer.scorers.lang_scorer import LangScorer
from docscorer.scorers.long_texts_scorer import LongTextScorer
from docscorer.scorers.numbers_scorer import NumsScorer
from docscorer.scorers.punct_scorer import PunctScorer
from docscorer.scorers.repeated_scorer import RepeatedScorer
from docscorer.scorers.url_scorer import URLScorer
from docscorer.scorers.short_segments_score import ShortSegmentsScore
from docscorer.utils import custom_mean, remove_delimitators


@dataclass
class ScoreResult:
    """Holds all individual scores for a document."""

    language: float
    punctuation: float
    singular_chars: float
    numbers: float
    repeated: float
    url: float
    informativeness: float
    long_segments: Tuple[float, float]  # [short_score, long_score]
    short_segments: float


class DocumentScorer:
    def __init__(self, config: Optional[ScorerConfiguration] = None):
        self.config = config if config else ScorerConfiguration()
        self.benchmark_config = self.config.benchmark_config
        self.lang_families_config = self.config.lang_families_config
        self.info_scorer = InformativenessScorer(
            self.config.info_score_config, self.config.interpolation_functions_dir
        )
        self.punct_scorer = PunctScorer(self.config)
        self.url_scorer = URLScorer(self.config)
        self.numbers_scorer = NumsScorer(self.config)
        self.singular_chars_scorer = SingularCharsScorer(self.config)
        self.lang_scorer = LangScorer(self.config)
        self.long_text_scorer = LongTextScorer(self.config)
        self.repeated_scorer = RepeatedScorer(self.config)
        self.short_segments_scorer = ShortSegmentsScore(self.config)

    def _extract_features(self, document_text: str) -> dict[str, list[int]]:
        """Extract counts of words, punctuation, sing. chars, and numbers per line."""
        features = [
            (
                len(self.config.word_pattern.findall(segment)),
                len(self.config.punctuation_pattern.findall(segment)),
                len(self.config.singular_chars_pattern.findall(segment)),
                len(self.config.numbers_pattern.findall(segment)),
            )
            for segment in document_text.split("\n")
        ]
        return {
            "word_chars": [f[0] for f in features],
            "punctuation_chars": [f[1] for f in features],
            "singular_chars": [f[2] for f in features],
            "numbers": [f[3] for f in features],
        }

    def _compute_scores(
        self,
        ref_lang: str,
        lang_segments: list[str],
        document_text: str,
        ref_script: str,
        doc_id: str,
        features: dict[str, list[int]],
    ) -> ScoreResult:
        """Compute all scorer outputs and return structured results."""
        num_word_chars = sum(features["word_chars"])
        num_punctuation_chars = sum(remove_delimitators(punct_chars=features["punctuation_chars"],
                                                        word_chars=features["word_chars"],
                                                        number_chars=features["numbers"]))
        num_singular_chars = sum(features["singular_chars"])
        num_numbers = sum(features["numbers"])

        return ScoreResult(
            language=self.lang_scorer.score(
                ref_lang, lang_segments, features["word_chars"], doc_id
            ),
            punctuation=self.punct_scorer.score(
                ref_language=ref_lang, num_punctuation_chars = num_punctuation_chars, num_word_chars = num_word_chars,
                punct_chars=features["punctuation_chars"], word_chars=features["word_chars"]
            ),
            singular_chars=self.singular_chars_scorer.score( ref_lang, num_singular_chars, 
                                                            num_word_chars, features["singular_chars"], 
                                                            features["word_chars"] 
            ),
            numbers=self.numbers_scorer.score(ref_lang, num_numbers, num_word_chars, 
                                              features["numbers"], features["word_chars"]
            ),
            repeated=self.repeated_scorer.score(ref_lang, document_text),
            url=self.url_scorer.score(ref_lang, document_text, features["word_chars"]),
            long_segments=self.long_text_scorer.score(
                ref_lang, lang_segments, features["word_chars"]
            ),
            informativeness=self.info_scorer.score(document_text, ref_script),
            short_segments=self.short_segments_scorer.score(ref_lang, features["word_chars"]),
        )

    def _aggregate_scores(self, scores: ScoreResult, alpha = 2.9) -> float:
        """Aggregate individual scores into a single overall score."""
        def exponent(subscore, subscores, alpha, beta=3):
            a = subscore**-alpha    
            b = sum([x**-alpha for x in subscores])
            return a/b*beta
        
        penalty_scores = [
                scores.url,
                scores.punctuation,
                scores.singular_chars,
                scores.numbers,
                scores.repeated,
                scores.informativeness,
                scores.short_segments,

            ]
        if any(x < 0.1 for x in penalty_scores):
            return 0.0
        P = math.prod([x**exponent(x, penalty_scores, alpha) for x in penalty_scores])
        
        base_score = (
            scores.language * 0.8
            + scores.long_segments[0]/10
            + scores.long_segments[1]/10
        ) * P
        return base_score

    def _format_output(
        self,
        overall_score: float,
        scores: ScoreResult,
        document_text: str,
        raw_score: bool,
    ) -> float | List[float | str]:
        """Format the output depending on configuration."""
        if raw_score:
            return overall_score

        final_score: list[float | str] = [
            overall_score,
            round(scores.language, 2),
            round(scores.url, 2),
            round(scores.punctuation, 2),
            round(scores.singular_chars, 2),
            round(scores.numbers, 2),
            round(scores.repeated, 2),
            round(scores.long_segments[0], 2),
            round(scores.long_segments[1], 2),
            round(scores.informativeness, 2),
            round(scores.short_segments, 2),
        ]

        if self.config.text_in_output:
            final_score.append(document_text.replace("\n", "\\n"))

        return final_score

    def score_document(
        self,
        ref_lang: str,
        ref_script: str,
        lang_segments: List[str],
        document_text: str,
        doc_id: str,
        raw_score: bool,
    ) -> float | List[float | str]:
        """Score a single document and return either raw (if raw_score is True) or detailed scores (if raw_score is False or by default).
        Detailed scores are ordered by the following list:
            - [0-WDS_score, 1-language_score, 2-url_score, 3-punctuation_score, 4-singular_chars_score, 5-numbers_score, 6-repeated_score, 7-n_long_segments_score, 8-great_segment_score, 9-informativeness_score]"""
        ref_lang = f"{ref_lang.lower()}_{ref_script.lower()}"
        lang_segments = [lang.lower() for lang in lang_segments]
        ref_script = ref_script.lower()
        features = self._extract_features(document_text)
        scores = self._compute_scores(
            ref_lang = ref_lang,
            lang_segments = lang_segments,
            document_text = document_text,
            ref_script = ref_script,
            doc_id = doc_id,
            features = features,
        )
        overall_score = self._aggregate_scores(scores)
        return self._format_output(overall_score, scores, document_text, raw_score)