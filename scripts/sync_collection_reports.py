#!/usr/bin/env python3
"""Download successful plugin collection reports into a permanent local archive."""

from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import sync_topic_plugins as topic_sync


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARCHIVE_ROOT = ROOT / "local-reports"
FINAL_PREFIX = "plugin-collection-report-"
SOURCE_PREFIX = "plugin-collection-report-source-"
SHA_PATTERN = re.compile(r"[0-9a-f]{40}")
LEGACY_RUN_PATTERN = re.compile(r"^- 运行编号：`([^`]+)`$", re.MULTILINE)
LEGACY_DATE_PATTERN = re.compile(r"^# DSH 插件自动收录报告 — (\d{4}-\d{2}-\d{2})$", re.MULTILINE)
LEGACY_ADDED_PATTERN = re.compile(r"^- 本次新增插件：(\d+)$", re.MULTILINE)
LEGACY_PLUGIN_PATTERN = re.compile(r"^### \[([^]]+)]\((https://github\.com/[^)]+)\)$", re.MULTILINE)


class ArchiveError(RuntimeError):
    """A report could not be safely archived."""


def command(
    args: list[str], *, cwd: Path = ROOT, check: bool = True
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        args,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "command failed"
        raise ArchiveError(f"{args[0]} failed: {detail}")
    return result


def list_artifacts(gh: str, repository: str) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []
    for page in range(1, 11):
        result = command(
            [
                gh,
                "api",
                f"repos/{repository}/actions/artifacts?per_page=100&page={page}",
            ]
        )
        payload = json.loads(result.stdout)
        batch = payload.get("artifacts", [])
        if not isinstance(batch, list):
            raise ArchiveError("GitHub returned an invalid artifact list")
        artifacts.extend(item for item in batch if not item.get("expired"))
        if len(batch) < 100:
            break
    else:
        raise ArchiveError("more than 1,000 artifacts; refusing a partial sync")
    return artifacts


def select_report_artifacts(artifacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected: dict[int, dict[str, Any]] = {}
    for artifact in artifacts:
        name = str(artifact.get("name", ""))
        run_id = int((artifact.get("workflow_run") or {}).get("id", 0))
        if not run_id or not name.startswith(FINAL_PREFIX):
            continue
        is_source = name.startswith(SOURCE_PREFIX)
        current = selected.get(run_id)
        if current is None or (
            str(current.get("name", "")).startswith(SOURCE_PREFIX) and not is_source
        ):
            selected[run_id] = artifact
    return sorted(selected.values(), key=lambda item: str(item.get("created_at", "")))


def load_manifest(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ArchiveError(f"manifest.jsonl line {number} is invalid") from exc
    return records


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def append_manifest(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def publication_commit(repo_root: Path, run_id: str) -> str | None:
    marker = f"<!-- topic-sync:{run_id} -->"
    result = command(
        [
            "git",
            "log",
            "-S",
            marker,
            "-1",
            "--format=%H",
            "origin/main",
            "--",
            "CHANGELOG.md",
        ],
        cwd=repo_root,
    )
    value = result.stdout.strip()
    return value if SHA_PATTERN.fullmatch(value) else None


def publication_pr_metadata(
    gh: str, repository: str, commit_sha: str
) -> tuple[str, str]:
    result = command(
        [
            gh,
            "api",
            f"repos/{repository}/commits/{commit_sha}/pulls",
            "--jq",
            ".[0] | [.html_url, .merged_at] | @tsv",
        ],
        check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return "", ""
    values = result.stdout.strip().split("\t", 1)
    return values[0], values[1] if len(values) > 1 else ""


def finalize_source_report(
    report_dir: Path,
    payload: dict[str, Any],
    *,
    gh: str,
    repository: str,
    repo_root: Path,
) -> dict[str, Any] | None:
    commit_sha = publication_commit(repo_root, str(payload["run_id"]))
    if not commit_sha:
        return None
    pr_url, published_at = publication_pr_metadata(gh, repository, commit_sha)
    if not published_at:
        published_at = command(
            ["git", "show", "-s", "--format=%cI", commit_sha], cwd=repo_root
        ).stdout.strip()
    return topic_sync.finalize_report_bundle(
        report_dir,
        commit_sha=commit_sha,
        published_at=published_at,
        run_url=(
            f"https://github.com/{repository}/actions/runs/{payload['run_id']}"
        ),
        pr_url=pr_url,
        repository=repository,
    )


def validate_report(payload: dict[str, Any], markdown: str, repo_root: Path) -> str:
    if payload.get("schema_version") != 1 or payload.get("report_type") != "plugin_collection":
        raise ArchiveError("unsupported report schema")
    if payload.get("status") != "published":
        raise ArchiveError("report is not finalized as published")
    if int(payload.get("added_count", 0)) < 1:
        raise ArchiveError("published report does not contain added plugins")
    plugins = payload.get("plugins")
    if not isinstance(plugins, list) or len(plugins) != int(payload["added_count"]):
        raise ArchiveError("report plugin count is inconsistent")
    commit_sha = str((payload.get("publication") or {}).get("commit_sha", ""))
    if not SHA_PATTERN.fullmatch(commit_sha):
        raise ArchiveError("report is missing a valid publication commit")
    expected_markdown = topic_sync.report_markdown(payload)
    if markdown != expected_markdown:
        raise ArchiveError("report.md does not match report.json")
    marker = f"<!-- topic-sync:{payload['run_id']} -->"
    changelog = command(
        ["git", "show", f"{commit_sha}:CHANGELOG.md"], cwd=repo_root
    ).stdout
    if marker not in changelog:
        raise ArchiveError("publication commit does not contain the report run marker")
    catalog = json.loads(
        command(
            ["git", "show", f"{commit_sha}:data/plugins.json"], cwd=repo_root
        ).stdout
    )
    published_urls = {item.get("url") for item in catalog.get("plugins", [])}
    missing = [item.get("url") for item in plugins if item.get("url") not in published_urls]
    if missing:
        raise ArchiveError(f"publication commit is missing report plugins: {missing}")
    return commit_sha


def archive_legacy_markdown(
    markdown_path: Path,
    *,
    artifact: dict[str, Any],
    archive_root: Path,
    manifest_records: list[dict[str, Any]],
    repo_root: Path,
    dry_run: bool = False,
) -> str:
    """Archive the Markdown-only report format used before report bundles."""
    markdown = markdown_path.read_text(encoding="utf-8")
    run_match = LEGACY_RUN_PATTERN.search(markdown)
    date_match = LEGACY_DATE_PATTERN.search(markdown)
    added_match = LEGACY_ADDED_PATTERN.search(markdown)
    plugins = LEGACY_PLUGIN_PATTERN.findall(markdown)
    if not run_match or not date_match or not added_match:
        raise ArchiveError("legacy report is missing required identity fields")
    run_id = run_match.group(1)
    if str((artifact.get("workflow_run") or {}).get("id", "")) != run_id:
        raise ArchiveError("legacy report run id does not match its artifact")
    if len(plugins) != int(added_match.group(1)) or not plugins:
        raise ArchiveError("legacy report plugin count is inconsistent")
    commit_sha = publication_commit(repo_root, run_id)
    if not commit_sha:
        return "pending"
    catalog = json.loads(
        command(["git", "show", f"{commit_sha}:data/plugins.json"], cwd=repo_root).stdout
    )
    published_urls = {item.get("url") for item in catalog.get("plugins", [])}
    missing = [url for _, url in plugins if url not in published_urls]
    if missing:
        raise ArchiveError(f"publication commit is missing legacy report plugins: {missing}")
    markdown_bytes = markdown.encode("utf-8")
    markdown_hash = sha256(markdown_bytes)
    existing = next(
        (item for item in manifest_records if item.get("publication_sha") == commit_sha),
        None,
    )
    if existing:
        if existing.get("markdown_sha256") != markdown_hash:
            raise ArchiveError("existing report SHA has different Markdown content")
        return "duplicate"
    review_date = date_match.group(1)
    metadata = {
        "schema_version": 1,
        "report_type": "legacy_markdown_plugin_collection",
        "status": "published",
        "run_id": run_id,
        "review_date": review_date,
        "added_count": len(plugins),
        "plugins": [{"name": name, "url": url} for name, url in plugins],
        "publication": {
            "commit_sha": commit_sha,
            "commit_url": f"https://github.com/HackSing/dsh-plugins/commit/{commit_sha}",
            "run_url": f"https://github.com/HackSing/dsh-plugins/actions/runs/{run_id}",
        },
        "migration_note_zh": "此报告由旧版 Markdown Artifact 迁移，原文未改写。",
    }
    metadata_bytes = (
        json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    safe_run_id = re.sub(r"[^A-Za-z0-9_.-]", "-", run_id)[:80]
    base_name = f"{review_date}-{commit_sha[:12]}-{safe_run_id}"
    target_dir = archive_root / review_date[:4] / review_date[5:7]
    markdown_target = target_dir / f"{base_name}.md"
    json_target = target_dir / f"{base_name}.json"
    if dry_run:
        return "would_archive"
    atomic_write(markdown_target, markdown_bytes)
    atomic_write(json_target, metadata_bytes)
    atomic_write(archive_root / "latest.md", markdown_bytes)
    record = {
        "artifact_id": artifact.get("id"),
        "artifact_name": artifact.get("name"),
        "format": "legacy_markdown",
        "json_path": str(json_target.relative_to(archive_root)),
        "json_sha256": sha256(metadata_bytes),
        "markdown_path": str(markdown_target.relative_to(archive_root)),
        "markdown_sha256": markdown_hash,
        "publication_sha": commit_sha,
        "run_id": run_id,
        "synced_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    append_manifest(archive_root / "manifest.jsonl", record)
    manifest_records.append(record)
    return "archived"


def archive_bundle(
    report_dir: Path,
    *,
    artifact: dict[str, Any],
    archive_root: Path,
    manifest_records: list[dict[str, Any]],
    gh: str,
    repository: str,
    repo_root: Path,
    dry_run: bool = False,
) -> str:
    json_path = report_dir / "report.json"
    markdown_path = report_dir / "report.md"
    if not json_path.exists() or not markdown_path.exists():
        raise ArchiveError("artifact does not contain report.md and report.json")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    if payload.get("status") != "published":
        payload = finalize_source_report(
            report_dir,
            payload,
            gh=gh,
            repository=repository,
            repo_root=repo_root,
        )
        if payload is None:
            return "pending"
    markdown = markdown_path.read_text(encoding="utf-8")
    commit_sha = validate_report(payload, markdown, repo_root)
    run_id = str(payload["run_id"])
    existing = next(
        (item for item in manifest_records if item.get("publication_sha") == commit_sha),
        None,
    )
    markdown_bytes = markdown.encode("utf-8")
    json_bytes = (
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    markdown_hash = sha256(markdown_bytes)
    json_hash = sha256(json_bytes)
    if existing:
        if existing.get("markdown_sha256") != markdown_hash:
            raise ArchiveError("existing report SHA has different Markdown content")
        return "duplicate"
    review_date = str(payload["review_date"])
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", review_date):
        raise ArchiveError("report review_date is invalid")
    safe_run_id = re.sub(r"[^A-Za-z0-9_.-]", "-", run_id)[:80]
    base_name = f"{review_date}-{commit_sha[:12]}-{safe_run_id}"
    target_dir = archive_root / review_date[:4] / review_date[5:7]
    markdown_target = target_dir / f"{base_name}.md"
    json_target = target_dir / f"{base_name}.json"
    if dry_run:
        return "would_archive"
    atomic_write(markdown_target, markdown_bytes)
    atomic_write(json_target, json_bytes)
    atomic_write(archive_root / "latest.md", markdown_bytes)
    record = {
        "artifact_id": artifact.get("id"),
        "artifact_name": artifact.get("name"),
        "json_path": str(json_target.relative_to(archive_root)),
        "json_sha256": json_hash,
        "markdown_path": str(markdown_target.relative_to(archive_root)),
        "markdown_sha256": markdown_hash,
        "publication_sha": commit_sha,
        "run_id": run_id,
        "synced_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    append_manifest(archive_root / "manifest.jsonl", record)
    manifest_records.append(record)
    return "archived"


def sync_reports(
    *,
    gh: str,
    repository: str,
    repo_root: Path,
    archive_root: Path,
    dry_run: bool = False,
) -> dict[str, int]:
    command(["git", "fetch", "--quiet", "origin", "main"], cwd=repo_root)
    artifacts = select_report_artifacts(list_artifacts(gh, repository))
    manifest_records = load_manifest(archive_root / "manifest.jsonl")
    counts = {"archived": 0, "duplicate": 0, "pending": 0, "would_archive": 0}
    failures = []
    for artifact in artifacts:
        run_id = int((artifact.get("workflow_run") or {}).get("id", 0))
        try:
            with tempfile.TemporaryDirectory(prefix="dsh-report-") as directory:
                command(
                    [
                        gh,
                        "run",
                        "download",
                        str(run_id),
                        "--repo",
                        repository,
                        "--name",
                        str(artifact["name"]),
                        "--dir",
                        directory,
                    ],
                    cwd=repo_root,
                )
                report_json = next(Path(directory).rglob("report.json"), None)
                if report_json is not None:
                    outcome = archive_bundle(
                        report_json.parent,
                        artifact=artifact,
                        archive_root=archive_root,
                        manifest_records=manifest_records,
                        gh=gh,
                        repository=repository,
                        repo_root=repo_root,
                        dry_run=dry_run,
                    )
                else:
                    legacy_markdown = next(Path(directory).rglob("*.md"), None)
                    if legacy_markdown is None:
                        raise ArchiveError("downloaded artifact has no supported report")
                    outcome = archive_legacy_markdown(
                        legacy_markdown,
                        artifact=artifact,
                        archive_root=archive_root,
                        manifest_records=manifest_records,
                        repo_root=repo_root,
                        dry_run=dry_run,
                    )
                counts[outcome] += 1
        except (ArchiveError, json.JSONDecodeError, OSError) as exc:
            failures.append(f"{artifact.get('name')}: {exc}")
            failure_record = {
                "artifact_id": artifact.get("id"),
                "artifact_name": artifact.get("name"),
                "error": str(exc),
                "recorded_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                "run_id": run_id,
            }
            atomic_write(
                archive_root / "failed" / f"{artifact.get('id', 'unknown')}.json",
                (
                    json.dumps(failure_record, ensure_ascii=False, indent=2, sort_keys=True)
                    + "\n"
                ).encode("utf-8"),
            )
    print(
        "Report sync completed: "
        + ", ".join(f"{key}={value}" for key, value in counts.items())
    )
    if failures:
        raise ArchiveError("; ".join(failures))
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default="HackSing/dsh-plugins")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--archive-root", type=Path, default=DEFAULT_ARCHIVE_ROOT)
    parser.add_argument("--gh", default=shutil.which("gh") or "gh")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    archive_root = args.archive_root.resolve()
    archive_root.mkdir(parents=True, exist_ok=True)
    try:
        with (archive_root / ".sync.lock").open("a", encoding="utf-8") as lock:
            try:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                print("Report sync skipped: another local sync is already running.")
                return
            sync_reports(
                gh=args.gh,
                repository=args.repo,
                repo_root=args.repo_root.resolve(),
                archive_root=archive_root,
                dry_run=args.dry_run,
            )
    except ArchiveError as exc:
        print(f"Report sync failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
