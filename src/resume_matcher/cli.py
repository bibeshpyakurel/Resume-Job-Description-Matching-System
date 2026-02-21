from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .pipeline import rank_resumes_in_folder, score_resume
from .preprocessing import NormalizationMode


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="resume-matcher",
        description="Match resumes against a job description.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    single_parser = subparsers.add_parser("single", help="Score one resume")
    single_parser.add_argument("pdf_path", type=Path, help="Path to a resume PDF")
    single_parser.add_argument("--jd", required=True, help="Job description text")
    single_parser.add_argument(
        "--normalize",
        choices=["none", "stem", "lemma"],
        default="none",
        help="Optional token normalization strategy",
    )
    single_parser.add_argument(
        "--no-synonyms",
        action="store_true",
        help="Disable skill synonym expansion",
    )

    batch_parser = subparsers.add_parser("batch", help="Rank resumes in a folder")
    batch_parser.add_argument("folder_path", type=Path, help="Folder containing PDF resumes")
    batch_parser.add_argument("--jd", required=True, help="Job description text")
    batch_parser.add_argument("--top", type=int, default=10, help="Top N results to print")
    batch_parser.add_argument("--json", action="store_true", help="Emit JSON output")
    batch_parser.add_argument(
        "--normalize",
        choices=["none", "stem", "lemma"],
        default="none",
        help="Optional token normalization strategy",
    )
    batch_parser.add_argument(
        "--no-synonyms",
        action="store_true",
        help="Disable skill synonym expansion",
    )

    return parser


def _print_table(results: list[dict[str, object]]) -> None:
    if not results:
        print("No resumes were processed.")
        return

    print(f"{'#':<3} {'Filename':<28} {'Overlap':>8} {'Cosine':>8} {'Final':>8}")
    print("-" * 64)
    for index, row in enumerate(results, start=1):
        print(
            f"{index:<3} {str(row['filename'])[:28]:<28} "
            f"{float(row['overlap_score']):>7.2f}% "
            f"{float(row['cosine_score']):>7.2f}% "
            f"{float(row['final_score']):>7.2f}%"
        )


def _single_command(
    pdf_path: Path,
    jd_text: str,
    normalization: NormalizationMode,
    expand_synonyms: bool,
) -> int:
    result = score_resume(
        jd_text=jd_text,
        pdf_path=pdf_path,
        normalization=normalization,
        expand_synonyms=expand_synonyms,
    )
    payload = asdict(result)
    _print_table([payload])
    if payload["matched_keywords"]:
        print(f"Matched keywords: {', '.join(payload['matched_keywords'])}")
    if payload["warnings"]:
        print(f"Warnings: {', '.join(payload['warnings'])}")
    print(f"Rationale: {payload['explainability']['rationale']}")
    return 0


def _batch_command(
    folder_path: Path,
    jd_text: str,
    top_n: int,
    as_json: bool,
    normalization: NormalizationMode,
    expand_synonyms: bool,
) -> int:
    results = rank_resumes_in_folder(
        jd_text=jd_text,
        folder_path=folder_path,
        top_n=top_n,
        normalization=normalization,
        expand_synonyms=expand_synonyms,
    )
    payload = [asdict(result) for result in results]

    if as_json:
        print(json.dumps(payload, indent=2))
        return 0

    _print_table(payload)
    warning_count = sum(len(result["warnings"]) for result in payload)
    print(f"Processed: {len(payload)} | Total warnings: {warning_count}")
    return 0


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "single":
        return _single_command(
            pdf_path=args.pdf_path,
            jd_text=args.jd,
            normalization=args.normalize,
            expand_synonyms=not args.no_synonyms,
        )

    if args.command == "batch":
        return _batch_command(
            folder_path=args.folder_path,
            jd_text=args.jd,
            top_n=args.top,
            as_json=args.json,
            normalization=args.normalize,
            expand_synonyms=not args.no_synonyms,
        )

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
