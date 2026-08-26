#!/usr/bin/env python3
"""Validate student homework submissions for prompt-audit policy compliance."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    submission_prompt_counts: dict[str, int] = field(default_factory=dict)
    submission_budget_prompt_counts: dict[str, int] = field(default_factory=dict)
    submission_commit_counts: dict[str, int] = field(default_factory=dict)

    def add_error(self, message: str) -> None:
        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a student submission against instructor policy."
    )
    parser.add_argument(
        "--student-root",
        required=True,
        help="Path to the student's repository root.",
    )
    parser.add_argument(
        "--homework",
        required=True,
        help="Homework id, for example: hw01",
    )
    parser.add_argument(
        "--reference-root",
        default=".",
        help="Path to instructor canonical repository root (default: current directory).",
    )
    parser.add_argument(
        "--policy-file",
        default="policy/homework_limits.json",
        help="Relative path under reference root to policy JSON.",
    )
    parser.add_argument(
        "--locked-paths-file",
        default="policy/locked_paths.txt",
        help="Relative path under reference root to locked paths file.",
    )
    parser.add_argument(
        "--required-initial-prompt-file",
        default="prompts/REQUIRED_INITIAL_PROMPT.md",
        help="Relative path under reference root to required initial prompt file.",
    )
    parser.add_argument(
        "--allow-extra-locked-files",
        action="store_true",
        help="Allow extra files inside locked directories on student side.",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Missing JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc


def load_locked_paths(path: Path) -> list[str]:
    if not path.exists():
        raise ValueError(f"Missing locked paths file: {path}")
    paths: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        paths.append(line)
    return paths


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalize_text(text: str) -> str:
    return text.replace("\r\n", "\n").strip()


def compare_file_contents(ref_file: Path, student_file: Path) -> bool:
    return ref_file.read_bytes() == student_file.read_bytes()


def compare_locked_paths(
    result: ValidationResult,
    reference_root: Path,
    student_root: Path,
    locked_paths: list[str],
    allow_extra_locked_files: bool,
) -> None:
    for rel in locked_paths:
        ref_path = reference_root / rel
        student_path = student_root / rel

        if not ref_path.exists():
            result.add_error(f"Locked path does not exist in reference repo: {rel}")
            continue

        if ref_path.is_file():
            if not student_path.exists():
                result.add_error(f"Missing locked file in student repo: {rel}")
                continue
            if not student_path.is_file():
                result.add_error(f"Locked file is not a file in student repo: {rel}")
                continue
            if not compare_file_contents(ref_path, student_path):
                result.add_error(f"Locked file changed: {rel}")
            continue

        if not student_path.exists():
            result.add_error(f"Missing locked directory in student repo: {rel}")
            continue
        if not student_path.is_dir():
            result.add_error(f"Locked directory is not a directory in student repo: {rel}")
            continue

        ref_files = {
            p.relative_to(ref_path).as_posix(): p
            for p in ref_path.rglob("*")
            if p.is_file()
        }
        student_files = {
            p.relative_to(student_path).as_posix(): p
            for p in student_path.rglob("*")
            if p.is_file()
        }

        for rel_file, ref_file in ref_files.items():
            student_file = student_files.get(rel_file)
            locked_label = f"{rel}{rel_file}" if rel.endswith("/") else f"{rel}/{rel_file}"
            if student_file is None:
                result.add_error(f"Missing file in locked directory: {locked_label}")
                continue
            if not compare_file_contents(ref_file, student_file):
                result.add_error(f"Changed file in locked directory: {locked_label}")

        if allow_extra_locked_files:
            continue

        extra = sorted(set(student_files) - set(ref_files))
        for rel_file in extra:
            locked_label = f"{rel}{rel_file}" if rel.endswith("/") else f"{rel}/{rel_file}"
            result.add_error(f"Extra file added in locked directory: {locked_label}")


def load_prompt_log(path: Path, result: ValidationResult) -> list[dict[str, Any]]:
    try:
        raw_lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        result.add_error(f"Missing prompt log: {path}")
        return []

    # PROMPT_LOG.md format: blocks headed "### Prompt <n> — <timestamp>", body = the prompt.
    records: list[dict[str, Any]] = []
    text = "\n".join(raw_lines)
    for m in re.finditer(
        r"^###\s+Prompt\s+(\d+)\s*(?:[—\-–]\s*(.*?))?$(.*?)(?=^###\s+Prompt\s+\d+|\Z)",
        text, re.M | re.S,
    ):
        records.append({
            "prompt_id": int(m.group(1)),
            "timestamp_local": (m.group(2) or "").strip(),
            "prompt": (m.group(3) or "").strip(),
        })
    if not records and text.strip():
        result.add_error(
            f"{path}: no '### Prompt <n>' entries found. See AI_POLICY.md for the format."
        )
    return records


def validate_prompt_log_schema(
    result: ValidationResult,
    records: list[dict[str, Any]],
    submission_label: str,
) -> None:
    if not records:
        result.add_error(f"{submission_label}: PROMPT_LOG.md is empty.")
        return

    for idx, record in enumerate(records, start=1):
        prompt_id = record.get("prompt_id")
        timestamp = record.get("timestamp_local")
        prompt_text = record.get("prompt")

        if prompt_id != idx:
            result.add_error(
                f"{submission_label}: prompt_id must be sequential starting at 1. "
                f"Expected {idx}, got {prompt_id}."
            )

        if not isinstance(timestamp, str) or not timestamp.strip():
            result.add_error(
                f"{submission_label}: record {idx} missing non-empty 'timestamp_local'."
            )

        if not isinstance(prompt_text, str) or not prompt_text.strip():
            result.add_error(
                f"{submission_label}: record {idx} missing non-empty 'prompt'."
            )


def validate_submission_folder(
    result: ValidationResult,
    submission_dir: Path,
    required_files: list[str],
    required_initial_prompt_text: str,
    max_prompts: int,
    count_initial_prompt_toward_limit: bool,
) -> None:
    submission_label = submission_dir.as_posix()

    for rel in required_files:
        required_path = submission_dir / rel
        if not required_path.exists():
            result.add_error(f"{submission_label}: missing required file {rel}.")

    initial_prompt_path = submission_dir / "INITIAL_PROMPT.md"
    prompt_log_path = submission_dir / "PROMPT_LOG.md"

    records = load_prompt_log(prompt_log_path, result)
    validate_prompt_log_schema(result, records, submission_label)
    if not records:
        return

    total_prompt_count = len(records)
    result.submission_prompt_counts[submission_label] = total_prompt_count
    # The initial prompt is assignment-specific and saved separately as INITIAL_PROMPT.md,
    # so it is not expected to appear as entry 1 of the log.
    budget_prompt_count = total_prompt_count
    result.submission_budget_prompt_counts[submission_label] = budget_prompt_count

    if budget_prompt_count > max_prompts:
        # Budgets are targets, not limits (policy: budgets_are_soft). Report, do not fail.
        result.add_warning(
            f"{submission_label}: {budget_prompt_count} prompts against a budget of {max_prompts}. "
            "Permitted — check the student noted where they got stuck."
        )


def run_git_log_for_path(
    student_root: Path,
    repo_relative_path: str,
) -> tuple[int, str, str]:
    process = subprocess.run(
        ["git", "log", "--format=%H%x1f%s", "--", repo_relative_path],
        cwd=student_root,
        text=True,
        capture_output=True,
    )
    return process.returncode, process.stdout, process.stderr


def extract_prompt_id_from_commit_subject(subject: str, homework_id: str) -> int | None:
    pattern = re.compile(
        rf"\b{re.escape(homework_id.lower())}\b\s+prompt\s+(\d+)\b",
        re.IGNORECASE,
    )
    match = pattern.search(subject)
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def validate_commit_per_prompt(
    result: ValidationResult,
    student_root: Path,
    submission_dir: Path,
    total_prompt_count: int,
    homework_id: str,
) -> None:
    submission_label = submission_dir.as_posix()
    git_dir = student_root / ".git"
    if not git_dir.exists():
        result.add_error(
            f"{submission_label}: commit-per-prompt policy enabled but .git history is unavailable."
        )
        return

    try:
        repo_relative_submission = submission_dir.relative_to(student_root).as_posix()
    except ValueError:
        result.add_error(
            f"{submission_label}: cannot compute submission path relative to student repo root."
        )
        return

    returncode, stdout, stderr = run_git_log_for_path(student_root, repo_relative_submission)
    if returncode != 0:
        result.add_error(
            f"{submission_label}: failed to read git history for submission path ({stderr.strip()})."
        )
        return

    lines = [line for line in stdout.splitlines() if line.strip()]
    result.submission_commit_counts[submission_label] = len(lines)
    if not lines:
        result.add_error(
            f"{submission_label}: no commits found for submission path; commit-per-prompt requirement not met."
        )
        return

    prompt_id_counts: dict[int, int] = {}
    for line in lines:
        if "\x1f" not in line:
            continue
        _commit_hash, subject = line.split("\x1f", 1)
        prompt_id = extract_prompt_id_from_commit_subject(subject, homework_id)
        if prompt_id is None:
            continue
        prompt_id_counts[prompt_id] = prompt_id_counts.get(prompt_id, 0) + 1

    for prompt_id in range(1, total_prompt_count + 1):
        if prompt_id not in prompt_id_counts:
            result.add_error(
                f"{submission_label}: missing commit message for prompt_id {prompt_id} "
                f"using format '{homework_id} prompt <id>: ...'."
            )

    for prompt_id, count in sorted(prompt_id_counts.items()):
        if prompt_id > total_prompt_count:
            result.add_warning(
                f"{submission_label}: commit message references prompt_id {prompt_id} "
                f"beyond logged prompt count {total_prompt_count}."
            )
        if count > 1:
            result.add_warning(
                f"{submission_label}: multiple commits found for prompt_id {prompt_id} ({count})."
            )

    commits_with_prompt_id = sum(prompt_id_counts.values())
    if commits_with_prompt_id < total_prompt_count:
        result.add_error(
            f"{submission_label}: only {commits_with_prompt_id} commit(s) with prompt ids found "
            f"for {total_prompt_count} logged prompts."
        )


def collect_homework_submission_dirs(student_root: Path, homework_id: str) -> list[Path]:
    submissions_root = student_root / "submissions"
    if not submissions_root.exists() or not submissions_root.is_dir():
        return []
    prefix = f"{homework_id.lower()}_"
    return sorted(
        [
            path
            for path in submissions_root.iterdir()
            if path.is_dir() and path.name.lower().startswith(prefix)
        ]
    )


def get_homework_config(policy: dict[str, Any], homework_id: str) -> dict[str, Any]:
    return policy.get("homeworks", {}).get(homework_id, {})


def get_homework_prompt_limit(policy: dict[str, Any], homework_id: str) -> int:
    default_limit = policy.get("default_max_prompts", 20)
    homework_cfg = get_homework_config(policy, homework_id)
    return int(homework_cfg.get("max_prompts", default_limit))


def get_count_initial_prompt_toward_limit(
    policy: dict[str, Any], homework_id: str
) -> bool:
    default_value = bool(policy.get("count_initial_prompt_toward_limit", True))
    homework_cfg = get_homework_config(policy, homework_id)
    return bool(homework_cfg.get("count_initial_prompt_toward_limit", default_value))


def main() -> int:
    args = parse_args()

    result = ValidationResult()
    student_root = Path(args.student_root).resolve()
    reference_root = Path(args.reference_root).resolve()

    if not student_root.exists():
        print(f"ERROR: student root does not exist: {student_root}")
        return 2
    if not reference_root.exists():
        print(f"ERROR: reference root does not exist: {reference_root}")
        return 2

    policy_path = reference_root / args.policy_file
    locked_paths_path = reference_root / args.locked_paths_file
    required_initial_prompt_path = reference_root / args.required_initial_prompt_file

    try:
        policy = load_json(policy_path)
        locked_paths = load_locked_paths(locked_paths_path)
        required_initial_prompt_text = normalize_text(
            read_text(required_initial_prompt_path)
        )
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 2

    compare_locked_paths(
        result=result,
        reference_root=reference_root,
        student_root=student_root,
        locked_paths=locked_paths,
        allow_extra_locked_files=args.allow_extra_locked_files,
    )

    required_files = policy.get(
        "required_submission_files",
        ["REPORT.md", "INITIAL_PROMPT.md", "PROMPT_LOG.md"],
    )
    homework_id = args.homework
    max_prompts = get_homework_prompt_limit(policy, homework_id)
    count_initial_prompt_toward_limit = get_count_initial_prompt_toward_limit(
        policy, homework_id
    )
    require_commit_per_prompt = bool(policy.get("require_commit_per_prompt", False))

    submission_dirs = collect_homework_submission_dirs(student_root, homework_id)
    if not submission_dirs:
        result.add_error(
            f"No submission folder found matching submissions/{homework_id}_<student_or_team_name>/"
        )
    else:
        for submission_dir in submission_dirs:
            validate_submission_folder(
                result=result,
                submission_dir=submission_dir,
                required_files=required_files,
                required_initial_prompt_text=required_initial_prompt_text,
                max_prompts=max_prompts,
                count_initial_prompt_toward_limit=count_initial_prompt_toward_limit,
            )
            total_prompt_count = result.submission_prompt_counts.get(
                submission_dir.as_posix()
            )
            if require_commit_per_prompt and total_prompt_count is not None:
                validate_commit_per_prompt(
                    result=result,
                    student_root=student_root,
                    submission_dir=submission_dir,
                    total_prompt_count=total_prompt_count,
                    homework_id=homework_id,
                )

    if result.warnings:
        print("WARNINGS:")
        for warning in result.warnings:
            print(f"- {warning}")

    if result.errors:
        print("VALIDATION FAILED")
        for error in result.errors:
            print(f"- {error}")
        return 1

    print("VALIDATION PASSED")
    inclusion_text = (
        "including_initial"
        if count_initial_prompt_toward_limit
        else "excluding_initial"
    )
    for submission_label, total_prompt_count in sorted(
        result.submission_prompt_counts.items()
    ):
        budget_prompt_count = result.submission_budget_prompt_counts.get(
            submission_label, total_prompt_count
        )
        print(
            f"- {submission_label}: total_prompt_count={total_prompt_count}, "
            f"budget_prompt_count={budget_prompt_count}, limit={max_prompts} ({inclusion_text})"
        )
    if require_commit_per_prompt:
        for submission_label, commit_count in sorted(result.submission_commit_counts.items()):
            print(f"- {submission_label}: commit_count={commit_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
