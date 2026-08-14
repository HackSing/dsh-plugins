#!/usr/bin/env python3
"""Read-only intake scanner for plugin submission pull requests."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PLUGINS_PATH = ROOT / "data" / "plugins.json"
CANDIDATES_PATH = ROOT / "data" / "topic-candidates.json"
SELF_REPOSITORY = "hacksing/dsh-plugins"
GITHUB_REPOSITORY_URL = re.compile(
    r"https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?=\.git(?:\s|$)|[\s)\]}>，。；、]|$)",
    re.IGNORECASE,
)
EXPLICIT_REPOSITORY_URL = re.compile(
    r"(?:plugin\s+repository|repository|repo|插件仓库|仓库)\s*[:：]\s*"
    r"(https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?)",
    re.IGNORECASE,
)


class IntakeError(RuntimeError):
    """A deterministic intake failure."""


class GitHubClient:
    def __init__(self, repository: str, token: str = "") -> None:
        self.repository = repository
        self.headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "dsh-plugins-submission-intake",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    def get_json(self, url: str) -> Any:
        request = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            raise IntakeError(f"GitHub API returned HTTP {exc.code} for {url}") from exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise IntakeError(f"GitHub API request failed for {url}: {exc}") from exc

    def list_open_pull_requests(self) -> list[dict[str, Any]]:
        pulls: list[dict[str, Any]] = []
        for page in range(1, 11):
            query = urllib.parse.urlencode(
                {"state": "open", "per_page": 100, "page": page, "sort": "created"}
            )
            batch = self.get_json(
                f"https://api.github.com/repos/{self.repository}/pulls?{query}"
            )
            if not isinstance(batch, list):
                raise IntakeError("GitHub pull request response was not a list")
            pulls.extend(batch)
            if len(batch) < 100:
                return pulls
        raise IntakeError("more than 1,000 open pull requests; refusing a partial scan")

    def list_pull_request_files(self, number: int) -> list[dict[str, Any]]:
        files: list[dict[str, Any]] = []
        for page in range(1, 4):
            query = urllib.parse.urlencode({"per_page": 100, "page": page})
            batch = self.get_json(
                f"https://api.github.com/repos/{self.repository}/pulls/{number}/files?{query}"
            )
            if not isinstance(batch, list):
                raise IntakeError("GitHub pull request files response was not a list")
            files.extend(batch)
            if len(batch) < 100:
                return files
        raise IntakeError(f"pull request #{number} changes more than 300 files")


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_repository_url(value: str) -> str | None:
    match = GITHUB_REPOSITORY_URL.search(str(value or "").strip())
    if not match:
        return None
    owner = match.group(1)
    name = match.group(2)
    if name.casefold().endswith(".git"):
        name = name[:-4]
    return f"https://github.com/{owner}/{name}"


def repository_key(value: str) -> str:
    normalized = normalize_repository_url(value)
    if not normalized:
        return ""
    return normalized.removeprefix("https://github.com/").casefold()


def extract_repository_urls(
    pull_request: dict[str, Any], files: list[dict[str, Any]]
) -> tuple[str, list[str]]:
    body = str(pull_request.get("body") or "")
    explicit = []
    for match in EXPLICIT_REPOSITORY_URL.finditer(body):
        normalized = normalize_repository_url(match.group(1))
        if normalized and repository_key(normalized) != SELF_REPOSITORY:
            explicit.append(normalized)
    explicit = list(dict.fromkeys(explicit))
    if len(explicit) == 1:
        return "explicit", explicit
    if len(explicit) > 1:
        return "ambiguous", explicit

    text = "\n".join(
        [
            str(pull_request.get("title") or ""),
            body,
            *[str(item.get("patch") or "") for item in files],
        ]
    )
    discovered = []
    for match in GITHUB_REPOSITORY_URL.finditer(text):
        normalized = normalize_repository_url(match.group(0))
        if normalized and repository_key(normalized) != SELF_REPOSITORY:
            discovered.append(normalized)
    discovered = list(dict.fromkeys(discovered))
    if len(discovered) == 1:
        return "inferred", discovered
    if len(discovered) > 1:
        return "ambiguous", discovered
    return "missing", []


def classify_repository(
    url: str,
    catalog: dict[str, Any],
    candidate_payload: dict[str, Any],
) -> dict[str, Any]:
    key = repository_key(url)
    for plugin in catalog.get("plugins", []):
        if repository_key(str(plugin.get("url", ""))) == key:
            return {
                "intake_status": "already_published",
                "plugin_name": plugin.get("name"),
                "category": plugin.get("category"),
                "repository_id": plugin.get("repository_id"),
            }
    matches = [
        candidate
        for candidate in candidate_payload.get("candidates", [])
        if repository_key(str(candidate.get("url", ""))) == key
    ]
    if matches:
        candidate = matches[0]
        return {
            "intake_status": f"candidate_{candidate.get('status', 'unknown')}",
            "candidate_status": candidate.get("status", "unknown"),
            "candidate_reasons": candidate.get("reasons", []),
            "category_suggestion": candidate.get("category_suggestion"),
            "repository_id": candidate.get("repository_id"),
        }
    return {"intake_status": "new_submission"}


def is_automation_pull_request(pull_request: dict[str, Any]) -> bool:
    head = pull_request.get("head") or {}
    user = pull_request.get("user") or {}
    return (
        str(head.get("ref", "")) == "automation/topic-sync"
        or str(user.get("type", "")).casefold() == "bot"
        or str(user.get("login", "")).casefold().endswith("[bot]")
    )


def build_report(client: GitHubClient) -> dict[str, Any]:
    catalog = load_json(PLUGINS_PATH, {"plugins": []})
    candidates = load_json(CANDIDATES_PATH, {"candidates": []})
    submissions = []
    skipped_automation = 0
    for pull_request in client.list_open_pull_requests():
        if is_automation_pull_request(pull_request):
            skipped_automation += 1
            continue
        number = int(pull_request["number"])
        files = client.list_pull_request_files(number)
        extraction, urls = extract_repository_urls(pull_request, files)
        record: dict[str, Any] = {
            "author": (pull_request.get("user") or {}).get("login"),
            "draft": bool(pull_request.get("draft")),
            "extraction": extraction,
            "pr_number": number,
            "pr_title": pull_request.get("title"),
            "pr_url": pull_request.get("html_url"),
            "repository_urls": urls,
        }
        if extraction == "missing":
            record["intake_status"] = "not_identified"
        elif extraction == "ambiguous":
            record["intake_status"] = "ambiguous_repository"
        else:
            record["repository_url"] = urls[0]
            record.update(classify_repository(urls[0], catalog, candidates))
        submissions.append(record)

    counts: dict[str, int] = {}
    for item in submissions:
        status = str(item["intake_status"])
        counts[status] = counts.get(status, 0) + 1
    return {
        "counts": counts,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "mode": "read_only",
        "open_prs_scanned": len(submissions),
        "repository": client.repository,
        "schema_version": 1,
        "skipped_automation_prs": skipped_automation,
        "submissions": submissions,
    }


def markdown_summary(report: dict[str, Any]) -> str:
    lines = [
        "# 插件收录 PR 只读扫描",
        "",
        f"- 开放 PR：{report['open_prs_scanned']}",
        f"- 跳过自动化 PR：{report['skipped_automation_prs']}",
        "- 当前模式：只读，不评论、不关闭、不发布",
        "",
        "| PR | 插件仓库 | 识别结果 | 下一批动作 |",
        "| --- | --- | --- | --- |",
    ]
    actions = {
        "already_published": "第二批：回复并关闭",
        "new_submission": "第三批：定向复核",
        "not_identified": "第四批：请求补充信息",
        "ambiguous_repository": "第四批：请求明确唯一仓库",
    }
    for item in report["submissions"]:
        status = str(item["intake_status"])
        action = actions.get(status, "第三批：根据候选状态处理")
        pr = f"[#{item['pr_number']}]({item.get('pr_url') or ''})"
        repository = item.get("repository_url") or "、".join(item.get("repository_urls", [])) or "未识别"
        repository = repository.replace("|", "\\|")
        lines.append(f"| {pr} | {repository} | `{status}` | {action} |")
    return "\n".join(lines) + "\n"


def write_outputs(report: dict[str, Any], output: Path) -> None:
    output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    summary = markdown_summary(report)
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with Path(summary_path).open("a", encoding="utf-8") as handle:
            handle.write(summary)
    print(summary, end="")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repository", default=os.environ.get("GITHUB_REPOSITORY", "HackSing/dsh-plugins")
    )
    parser.add_argument("--output", type=Path, default=Path("pr-intake.json"))
    args = parser.parse_args()
    client = GitHubClient(args.repository, os.environ.get("GITHUB_TOKEN", ""))
    report = build_report(client)
    write_outputs(report, args.output)


if __name__ == "__main__":
    main()
