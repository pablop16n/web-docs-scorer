import logging
import sys
from pathlib import Path

from docopt import docopt

from docscorer.configuration import ScorerConfiguration
from docscorer.docscorer import DocumentScorer

usage = (
    "Web Document Scoring Tool\n\n"
    "Usage:\n"
    "  cli.py --input=<input_path> [--output=<output_path>] "
    "[--benchmark_config=<path>] [--info_score_config=<path>] "
    "[--lang_families_config=<path>] "
    "[--text_in_output] [--only_final_score]\n"
    "  cli.py (-h | --help)\n"
    "  cli.py --version\n\n"
    "Options:\n"
    "  --input=<input_path>               Path to input directory with .jsonl files\n"
    "  --output=<output_path>             Path to save output .csv files [default: <input_path>/document_scores]\n"  # noqa: E501
    "  --benchmark_config=<path>          Path to benchmark CSV\n"
    "  --info_score_config=<path>         Path to informativeness config dir\n"
    "  --lang_families_config=<path>      Path to lang families CSV\n"
    "  --char_patterns_config=<path>      Path to char patterns config JSON\n"
    "  --text_in_output                   Include original text in output\n"
    "  --only_final_score                 Only include final score in output\n"
    "  -h --help                         Show this screen\n"
    "  --version                         Show version\n"
)


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )


def main() -> None:
    setup_logging()
    args = docopt(usage, version="DocumentScorer v1.0")

    input_path = Path(args["--input"])
    if not input_path.exists():
        logging.error(f"Input path does not exist: {input_path}")
        sys.exit(1)

    output_path = Path(args.get("--output") or input_path / "document_scores")
    output_path.mkdir(parents=True, exist_ok=True)

    try:
        config = ScorerConfiguration(args)
    except FileNotFoundError as e:
        logging.error(str(e))
        sys.exit(1)

    scorer = DocumentScorer(config)
    scorer.score_directory(input_path, output_path)
    logging.info("Scoring completed successfully.")


if __name__ == "__main__":
    main()
