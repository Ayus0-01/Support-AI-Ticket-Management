from __future__ import annotations

import argparse
import json
from pathlib import Path

from .retrieval_eval import (
    run as run_retrieval,
)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Run the M2 retrieval evaluation."
        )
    )

    parser.add_argument(
        "--retrieval-golden",
        default=(
            "evaluation_data/"
            "retrieval_golden.json"
        ),
    )

    parser.add_argument(
        "--output-dir",
        default=(
            "evaluation_data/"
            "reports"
        ),
    )

    args = parser.parse_args()

    output_dir = Path(
        args.output_dir
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    retrieval_report = (
        run_retrieval(
            golden_path=(
                args.retrieval_golden
            ),
            output_path=(
                output_dir
                / "retrieval_report.json"
            ),
        )
    )

    print(
        json.dumps(
            {
                "retrieval": (
                    retrieval_report[
                        "summary"
                    ]
                )
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()