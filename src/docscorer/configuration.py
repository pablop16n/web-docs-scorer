import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

import pandas as pd

from docscorer.utils import average, join_utf_blocks


class ScorerConfiguration:
    # Constants
    REF_LANGUAGE_KEY = "spa_latn"
    MENU_LENGTH = 30
    PUNCT_BAD = (25.0, 0.3)
    PUNCT_SEMIBAD = 0.5
    PUNCT_DESIRED_MAX = 2.5
    PUNCT_DESIRED_MIN = 0.9
    SINGULAR_CHARS_MAX = 10.0
    SINGULAR_CHARS_BAD = 6.0
    SINGULAR_CHARS_SEMIBAD = 2.0
    SINGULAR_CHARS_DESIRED = 1.0
    NUMBERS_MAX = 30.0
    NUMBERS_DESIRED = 1.0
    LONG_TEXT_MIN_VALUE = 250
    LONG_TEXT_MAX_VALUE = 1000
    DESIRED_LONG_TEXTS = 10
    EQUIVALENT_SCRIPTS = {"hant": "hans"}
    ACCUM_NUMBERS_NOT_PENALIZED = 50
    ACCUM_NUMBERS_HARD_PENALIZED = 1000
    ACCUM_SINGULAR_NOT_PENALIZED = 30
    ACCUM_SINGULAR_HARD_PENALIZED = 250

    def __init__(self, args: Optional[Dict[str, Any]] = None):
        self.args = args or {}
        self._base_dir = Path(__file__).resolve().parent
        self._load_config_files()

        self.text_in_output = self.args.get("--text_in_output", False)
        self.only_final_score = self.args.get("--only_final_score", False)

        # Load benchmark and language family data
        self.df_lang_adaption = pd.read_csv(self.benchmark_config)
        self.df_families = pd.read_csv(self.lang_families_config)

        self.LANGUAGES = self.df_lang_adaption.language_3_chars.to_list()
        self._set_character_patterns()
        self._prepare_modeled_scores()
        self._adapt_missing_languages()
        self._compute_scoring_metrics()

    def _load_config_files(self) -> None:
        def get_path(
            default: Union[str, Path],
            arg_key: str,
        ) -> Path:
            if (
                self.args is not None
                and arg_key in self.args
                and self.args[arg_key] is not None
            ):
                path = self._base_dir / Path(self.args[arg_key])
            else:
                path = self._base_dir / Path(default)
            if not path.exists():
                raise FileNotFoundError(f"Required config file not found: {path}")
            return path

        self.benchmark_config = get_path(
            "configurations/language_adaption/medians_language.csv",
            "--benchmark_config",
        )
        self.info_score_config = get_path(
            "configurations/informativeness_config.json",
            "--info_score_config",
        )
        self.interpolation_functions_dir = get_path(
            "configurations/interpolation_functions/",
            "--interpolation_functions_dir",
        )
        self.lang_families_config = get_path(
            "configurations/language_adaption/lang_families_script.csv",
            "--lang_families_config",
        )
        self.char_patterns_config = get_path(
            "configurations/char_patterns.json",
            "--char_patterns_config",
        )

    def _prepare_modeled_scores(self) -> None:
        self.modeled_numbers = {
            f"{line.language_3_chars}_{line.script}": round(line.numbers_score, 2)
            for _, line in self.df_lang_adaption.iterrows()
        }
        self.modeled_punctuation = {
            f"{line.language_3_chars}_{line.script}": round(line.punctuation_score, 2)
            for _, line in self.df_lang_adaption.iterrows()
        }
        self.modeled_singular_chars = {
            f"{line.language_3_chars}_{line.script}": round(
                line.singular_chars_score, 2
            )
            for _, line in self.df_lang_adaption.iterrows()
        }
        self.SCRIPTS = self.df_lang_adaption.script.unique() #covered scripts
        for script in self.df_lang_adaption.script.unique():
            df_selected = self.df_lang_adaption[self.df_lang_adaption.script == script]
            self.modeled_numbers[script] = round(df_selected.numbers_score.mean(), 2)
            self.modeled_punctuation[script] = round(df_selected.punctuation_score.mean(), 2)
            self.modeled_singular_chars[script] = round(df_selected.singular_chars_score.mean(), 2)
        

    def _adapt_missing_languages(self) -> None:
        df_lang_no_data = self.df_families[
            ~self.df_families.language_3_chars.isin(self.LANGUAGES)
        ]
        df_lang_data = self.df_families[
            self.df_families.language_3_chars.isin(self.LANGUAGES)
        ]
        df_lang_adapted = pd.merge(
            df_lang_data,
            self.df_lang_adaption,
            on=["language_3_chars", "script"],
            how="inner",
        )

        for _, line in df_lang_no_data.iterrows():
            familiars = df_lang_adapted[
                (df_lang_adapted.genus == line.genus)
                & (df_lang_adapted.script == line.script)
            ]
            if familiars.empty:
                familiars = df_lang_adapted[
                    (df_lang_adapted.family == line.family)
                    & (df_lang_adapted.script == line.script)
                ]
            if not familiars.empty:
                key = f"{line.language_3_chars}_{line.script}"
                self.modeled_numbers[key] = round(
                    average(familiars.numbers_score.to_list()), 2
                )
                self.modeled_punctuation[key] = round(
                    average(familiars.punctuation_score.to_list()), 2
                )
                self.modeled_singular_chars[key] = round(
                    average(familiars.singular_chars_score.to_list()), 2
                )

    def _compute_percent_dict(
        self,
        modeled_dict: Dict[str, int],
        ref_value: float,
        factor: float,
        cap_100: bool = False,
    ) -> Dict[str, float]:
        result = {}
        for lang, val in modeled_dict.items():
            pct = round(val * factor / ref_value, 1)
            if cap_100 and pct > 100:
                pct = 100.0
            result[lang] = pct
        result["standard"] = average(list(result.values()))
        return result

    def _compute_percent_dict_tuple(
        self, modeled_dict: Dict[str, int], ref_tuple: Tuple[float, float]
    ) -> Dict[str, Tuple[float, float]]:
        result = {}
        for lang, val in modeled_dict.items():
            result[lang] = (
                round(
                    val
                    * ref_tuple[0]
                    / self.modeled_punctuation[self.REF_LANGUAGE_KEY],
                    1,
                ),
                round(
                    val
                    * ref_tuple[1]
                    / self.modeled_punctuation[self.REF_LANGUAGE_KEY],
                    1,
                ),
            )
        result["standard"] = (
            average([x[0] for x in result.values()]),
            average([x[1] for x in result.values()]),
        )
        return result

    def _compute_scoring_metrics(self) -> None:
        ref_punct = self.modeled_punctuation[self.REF_LANGUAGE_KEY]
        ref_numbers = self.modeled_numbers[self.REF_LANGUAGE_KEY]
        ref_singular = self.modeled_singular_chars[self.REF_LANGUAGE_KEY]

        # Punctuation scores
        self.PUNCTUATION_PERCENT_BAD = self._compute_percent_dict_tuple(
            self.modeled_punctuation, self.PUNCT_BAD
        )
        self.PUNCTUATION_PERCENT_SEMIBAD = self._compute_percent_dict(
            self.modeled_punctuation, ref_punct, self.PUNCT_SEMIBAD
        )
        self.PUNCTUATION_PERCENT_DESIRED_MAX = self._compute_percent_dict(
            self.modeled_punctuation, ref_punct, self.PUNCT_DESIRED_MAX
        )
        self.PUNCTUATION_PERCENT_DESIRED_MIN = self._compute_percent_dict(
            self.modeled_punctuation, ref_punct, self.PUNCT_DESIRED_MIN
        )

        # Singular chars scores
        self.SINGULAR_CHARS_PERCENT_MAX = self._compute_percent_dict(
            self.modeled_singular_chars,
            ref_singular,
            self.SINGULAR_CHARS_MAX,
            cap_100=True,
        )
        self.SINGULAR_CHARS_PERCENT_BAD = self._compute_percent_dict(
            self.modeled_singular_chars, ref_singular, self.SINGULAR_CHARS_BAD
        )
        self.SINGULAR_CHARS_PERCENT_SEMIBAD = self._compute_percent_dict(
            self.modeled_singular_chars, ref_singular, self.SINGULAR_CHARS_SEMIBAD
        )
        self.SINGULAR_CHARS_PERCENT_DESIRED = self._compute_percent_dict(
            self.modeled_singular_chars, ref_singular, self.SINGULAR_CHARS_DESIRED
        )

        # Numbers scores
        self.NUMBERS_PERCENT_MAX = self._compute_percent_dict(
            self.modeled_numbers, ref_numbers, self.NUMBERS_MAX, cap_100=True
        )
        self.NUMBERS_PERCENT_DESIRED = self._compute_percent_dict(
            self.modeled_numbers, ref_numbers, self.NUMBERS_DESIRED
        )

        # Menu adaptation
        self.MENUS_AVERAGE_LENGTH = {
            lang: round(ref_punct * self.MENU_LENGTH / val) 
            for lang, val in self.modeled_punctuation.items()
        }
        self.MENUS_AVERAGE_LENGTH["standard"] = average(
            list(self.MENUS_AVERAGE_LENGTH.values())
        )

        # Long text scoring
        self.LONG_TEXT_MAX = {
            lang: round(ref_punct * self.LONG_TEXT_MAX_VALUE / val)
            for lang, val in self.modeled_punctuation.items()
        }
        self.LONG_TEXT_MAX["standard"] = average(list(self.LONG_TEXT_MAX.values()))

        self.LONG_TEXT_MIN = {
            lang: round(ref_punct * self.LONG_TEXT_MIN_VALUE / val)
            for lang, val in self.modeled_punctuation.items()
        }
        self.LONG_TEXT_MIN["standard"] = average(list(self.LONG_TEXT_MIN.values()))

    def _set_character_patterns(self) -> None:
        with open(self.char_patterns_config, "r", encoding="utf-8") as f:
            char_patterns = json.load(f)
        try:
            self.numbers_pattern = join_utf_blocks(char_patterns["NUMBERS"])
            self.singular_chars_pattern = join_utf_blocks(
                char_patterns["SINGULAR_CHARS"]
            )
            self.punctuation_pattern = join_utf_blocks(
                char_patterns["PUNCTUATION_CHARS"]
            )
            self.word_pattern = join_utf_blocks(
                char_patterns["SINGULAR_CHARS"]
                + char_patterns["PUNCTUATION_CHARS"]
                + char_patterns["NUMBERS"]
                + char_patterns["SPACES"],
                inverse=True,
            )
        except KeyError as exception:
            logging.exception(
                f"Key {exception} not found in {self.char_patterns_config}"
            )
