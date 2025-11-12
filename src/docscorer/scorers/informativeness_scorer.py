import json
import re
from pathlib import Path
from typing import Any

import joblib
import zstandard

from docscorer.scorers.utils import scale_value


class InformativenessScorer:

    # Thresholds for score ranges
    TOLERANCE_GOOD = 10
    TOLERANCE_BAD = 20
    TOLERANCE_SEMIBAD = 15

    def __init__(self, config_filepath: Path, interpolation_functions_dir: Path):
        self.cctx = zstandard.ZstdCompressor()
        with open(config_filepath, "r", encoding="utf-8") as f:
            config = json.load(f)

        self.GROUPS = {
            script: group
            for group, scripts in config["GROUPS"].items()
            for script in scripts
        }
        self.FUNCTION_FILES = config["FUNCTION_FILES"]
        self.OUTSIDERS_FIX = config["OUTSIDERS_FIX"]
        self.functions = {
            group: joblib.load(interpolation_functions_dir / file)
            for group, file in self.FUNCTION_FILES.items()
        }

    def _get_group(self, script_code: str) -> Any:
        # Group A is the default
        return self.GROUPS.get(script_code, "GROUP_A")

    def _calculate_information_score(
        self, raw_weight: int, compression: float, script_code: str
    ) -> float:
        group = self._get_group(script_code)
        raw_weight = min(raw_weight, self.OUTSIDERS_FIX[group])

        y_pred = float(self.functions[group](raw_weight))
        diff = compression - y_pred

        if abs(diff) <= self.TOLERANCE_GOOD:
            return 1.0
        if abs(diff) >= self.TOLERANCE_BAD:
            return 0.0

        # Below predicted
        if diff < 0:
            if abs(diff) <= self.TOLERANCE_SEMIBAD:
                return scale_value(
                    compression,
                    y_pred - self.TOLERANCE_GOOD,
                    y_pred - self.TOLERANCE_SEMIBAD,
                    1.0,
                    0.7,
                )
            return scale_value(
                compression,
                y_pred - self.TOLERANCE_SEMIBAD,
                y_pred - self.TOLERANCE_BAD,
                0.7,
                0.0,
            )

        # Above predicted
        if diff <= self.TOLERANCE_SEMIBAD:
            return scale_value(
                compression,
                y_pred + self.TOLERANCE_GOOD,
                y_pred + self.TOLERANCE_SEMIBAD,
                1.0,
                0.7,
            )
        return scale_value(
            compression,
            y_pred + self.TOLERANCE_SEMIBAD,
            y_pred + self.TOLERANCE_BAD,
            0.7,
            0.0,
        )

    def score(self, text: str, script_code: str) -> float:
        text = re.sub(r"\d", "1", text.lower())
        compressed_weight = len(self.cctx.compress(text.encode("utf-8")))
        raw_weight = max(1, len(text.encode("utf-8")))
        compression = round((1 - compressed_weight / raw_weight) * 100, 1)
        return self._calculate_information_score(raw_weight, compression, script_code)
