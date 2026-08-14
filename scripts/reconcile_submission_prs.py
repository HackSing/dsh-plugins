#!/usr/bin/env python3
"""Reconcile plugin submission pull requests with the trusted catalog workflow."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PLUGINS_PATH = ROOT / "data" / "plugins.json"
CANDIDATES_PATH = ROOT / "data" / "topic-candidates.json"
REPORTS_PATH = ROOT / "reports" / "sync"
SELF_REPOSITORY = "hacksing/dsh-plugins"
REVIEWING_LABEL = "submission:reviewing"
ACCEPTED_LABEL = "submission:accepted"
AUTOMATION_LABEL = "automation-managed"
RETRYABLE_MODEL_REASONS = {
    "model_analysis_deferred",
    "model_analysis_failed",
    "model_provider_unconfigured",
}
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

    def request_json(
        self, url: str, *, method: str = "GET", payload: Any = None
    ) -> Any:
        data = None
        headers = dict(self.headers)
        if payload is not None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(url, headers=headers, data=data, method=method)
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                if response.status == 204:
                    return None
                return json.load(response)
        except urllib.error.HTTPError as exc:
            raise IntakeError(f"GitHub API returned HTTP {exc.code} for {url}") from exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise IntakeError(f"GitHub API request failed for {url}: {exc}") from exc

    def get_json(self, url: str) -> Any:
        return self.request_json(url)

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

    def list_pull_request_comments(self, number: int) -> list[dict[str, Any]]:
        return self.get_json(
            f"https://api.github.com/repos/{self.repository}/issues/{number}/comments?per_page=100"
        )

    def list_automation_report_issues(self) -> list[dict[str, Any]]:
        return self.get_json(
            f"https://api.github.com/repos/{self.repository}/issues"
            "?state=all&labels=automation-report&per_page=100"
        )

    def ensure_label(self, name: str, color: str, description: str) -> None:
        url = f"https://api.github.com/repos/{self.repository}/labels"
        try:
            self.request_json(
                url,
                method="POST",
                payload={"name": name, "color": color, "description": description},
            )
        except IntakeError as exc:
            if "HTTP 422" not in str(exc):
                raise
            encoded = urllib.parse.quote(name, safe="")
            self.request_json(
                f"{url}/{encoded}",
                method="PATCH",
                payload={"new_name": name, "color": color, "description": description},
            )

    def add_labels(self, number: int, labels: list[str]) -> None:
        self.request_json(
            f"https://api.github.com/repos/{self.repository}/issues/{number}/labels",
            method="POST",
            payload={"labels": labels},
        )

    def remove_label(self, number: int, label: str) -> None:
        encoded = urllib.parse.quote(label, safe="")
        try:
            self.request_json(
                f"https://api.github.com/repos/{self.repository}/issues/{number}/labels/{encoded}",
                method="DELETE",
            )
        except IntakeError as exc:
            if "HTTP 404" not in str(exc):
                raise

    def post_comment(self, number: int, body: str) -> None:
        self.request_json(
            f"https://api.github.com/repos/{self.repository}/issues/{number}/comments",
            method="POST",
            payload={"body": body},
        )

    def close_pull_request(self, number: int) -> None:
        self.request_json(
            f"https://api.github.com/repos/{self.repository}/pulls/{number}",
            method="PATCH",
            payload={"state": "closed"},
        )

    def dispatch_workflow(self, workflow: str, inputs: dict[str, str]) -> None:
        encoded = urllib.parse.quote(workflow, safe="")
        self.request_json(
            f"https://api.github.com/repos/{self.repository}/actions/workflows/{encoded}/dispatches",
            method="POST",
            payload={"ref": "main", "inputs": inputs},
        )


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


def build_report(client: GitHubClient, only_pr: int | None = None) -> dict[str, Any]:
    catalog = load_json(PLUGINS_PATH, {"plugins": []})
    candidates = load_json(CANDIDATES_PATH, {"candidates": []})
    submissions = []
    skipped_automation = 0
    for pull_request in client.list_open_pull_requests():
        if only_pr is not None and int(pull_request["number"]) != only_pr:
            continue
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
            "labels": [
                str(label.get("name"))
                for label in pull_request.get("labels", [])
                if label.get("name")
            ],
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
        "# 插件收录 PR 自动处理",
        "",
        f"- 开放 PR：{report['open_prs_scanned']}",
        f"- 跳过自动化 PR：{report['skipped_automation_prs']}",
        (
            "- 当前模式：已收录闭环与未收录定向复核"
            if report.get("mode") == "active"
            else "- 当前模式：只处理已收录申请"
            if report.get("mode") == "published_only"
            else "- 当前模式：只读，不评论、不关闭、不发布"
        ),
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


def git_output(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def find_publication_evidence(repository_url: str) -> dict[str, str]:
    normalized = normalize_repository_url(repository_url) or repository_url
    matched_report = None
    if REPORTS_PATH.exists():
        for path in sorted(REPORTS_PATH.glob("*.md")):
            if f"]({normalized})" in path.read_text(encoding="utf-8"):
                matched_report = path
                break
    if matched_report:
        relative = str(matched_report.relative_to(ROOT))
        commit = git_output("log", "-1", "--format=%H", "--", relative)
        return {
            "commit": commit,
            "report_path": relative,
            "report_stem": matched_report.stem,
        }
    return {"commit": git_output("rev-parse", "HEAD")}


def accepted_comment(
    item: dict[str, Any], evidence: dict[str, str], report_issue_url: str | None
) -> str:
    repository_id = item.get("repository_id") or repository_key(item["repository_url"])
    commit = evidence["commit"]
    report_link = report_issue_url
    if not report_link and evidence.get("report_path"):
        report_link = (
            f"https://github.com/HackSing/dsh-plugins/blob/{commit}/{evidence['report_path']}"
        )
    lines = [
        "✅ 已通过自动目录收录",
        "",
        "该插件已经在远端正式目录中确认，无需合并本 PR 的贡献者分支。",
        "",
        f"- 插件：[{item.get('plugin_name') or repository_key(item['repository_url'])}]({item['repository_url']})",
        f"- 分类：`{item.get('category') or 'unknown'}`",
        "- 正式目录：https://github.com/HackSing/dsh-plugins/blob/main/README.zh.md",
        f"- 收录提交：https://github.com/HackSing/dsh-plugins/commit/{commit}",
    ]
    if report_link:
        lines.append(f"- 自动收录报告：{report_link}")
    lines.extend(
        [
            "",
            "本 PR 作为收录申请自动关闭；后续信息修正可通过新的 Issue 或 PR 提交。",
            "",
            f"<!-- dsh-submission:v1 status=accepted repository={repository_id} commit={commit} -->",
        ]
    )
    return "\n".join(lines)


def reviewing_comment(item: dict[str, Any]) -> str:
    repository = item["repository_url"]
    return "\n".join(
        [
            "🔎 已进入自动复核",
            "",
            f"系统将从主仓库的可信工作流定向复核 [{repository}]({repository})。",
            "复核只读取公开元数据、目录结构和 README，不会检出、安装或执行贡献者分支及插件代码。",
            "",
            "高置信度通过后会自动更新正式目录、双语 README、CHANGELOG 和收录报告，再回到本 PR 回复结果并关闭。系统异常会重试，不会被当作审核拒绝。",
            "",
            f"<!-- dsh-submission:v1 status=reviewing repository={repository_key(repository)} -->",
        ]
    )


def close_already_published(
    report: dict[str, Any], client: GitHubClient
) -> list[dict[str, Any]]:
    accepted = [
        item for item in report["submissions"] if item["intake_status"] == "already_published"
    ]
    if not accepted:
        return []
    client.ensure_label(
        ACCEPTED_LABEL, "0E8A16", "Plugin submission accepted by automation"
    )
    client.ensure_label(
        AUTOMATION_LABEL, "1D76DB", "Pull request lifecycle managed by automation"
    )
    report_issues = client.list_automation_report_issues()
    actions = []
    for item in accepted:
        evidence = find_publication_evidence(item["repository_url"])
        issue_url = None
        report_stem = evidence.get("report_stem")
        if report_stem:
            matching = [
                issue
                for issue in report_issues
                if report_stem in str(issue.get("title", ""))
            ]
            if matching:
                issue_url = matching[0].get("html_url")
        marker = "<!-- dsh-submission:v1 status=accepted "
        comments = client.list_pull_request_comments(int(item["pr_number"]))
        if not any(marker in str(comment.get("body", "")) for comment in comments):
            client.post_comment(
                int(item["pr_number"]), accepted_comment(item, evidence, issue_url)
            )
        client.add_labels(int(item["pr_number"]), [ACCEPTED_LABEL, AUTOMATION_LABEL])
        client.remove_label(int(item["pr_number"]), REVIEWING_LABEL)
        client.close_pull_request(int(item["pr_number"]))
        actions.append(
            {
                "action": "closed_as_published",
                "pr_number": item["pr_number"],
                "repository_url": item["repository_url"],
            }
        )
    return actions


def is_reviewable_submission(item: dict[str, Any]) -> bool:
    if item.get("draft") or REVIEWING_LABEL in item.get("labels", []):
        return False
    status = item.get("intake_status")
    if status == "new_submission":
        return True
    if status != "candidate_needs_review":
        return False
    return bool(RETRYABLE_MODEL_REASONS.intersection(item.get("candidate_reasons", [])))


def queue_targeted_reviews(
    report: dict[str, Any], client: GitHubClient, limit: int
) -> list[dict[str, Any]]:
    if limit < 1:
        raise IntakeError("review limit must be greater than zero")
    targets = [item for item in report["submissions"] if is_reviewable_submission(item)][
        :limit
    ]
    if not targets:
        return []
    client.ensure_label(
        REVIEWING_LABEL, "FBCA04", "Plugin submission is in automated review"
    )
    client.ensure_label(
        AUTOMATION_LABEL, "1D76DB", "Pull request lifecycle managed by automation"
    )
    actions = []
    for item in targets:
        number = int(item["pr_number"])
        client.dispatch_workflow(
            "sync-topic-plugins.yml",
            {
                "mode": "submission",
                "target_repository": item["repository_url"],
                "source_pr": str(number),
                "max_promotions": "0",
            },
        )
        client.add_labels(number, [REVIEWING_LABEL, AUTOMATION_LABEL])
        marker = "<!-- dsh-submission:v1 status=reviewing "
        comments = client.list_pull_request_comments(number)
        if not any(marker in str(comment.get("body", "")) for comment in comments):
            client.post_comment(number, reviewing_comment(item))
        actions.append(
            {
                "action": "queued_targeted_review",
                "pr_number": number,
                "repository_url": item["repository_url"],
            }
        )
    return actions


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
    parser.add_argument(
        "--apply-published",
        action="store_true",
        help="reply to and close only submissions already present in the formal catalog",
    )
    parser.add_argument(
        "--queue-reviews",
        action="store_true",
        help="dispatch trusted targeted review workflows for eligible submissions",
    )
    parser.add_argument("--review-limit", type=int, default=5)
    parser.add_argument("--only-pr", type=int)
    args = parser.parse_args()
    client = GitHubClient(args.repository, os.environ.get("GITHUB_TOKEN", ""))
    report = build_report(client, only_pr=args.only_pr)
    actions = []
    if args.apply_published:
        actions.extend(close_already_published(report, client))
        report["mode"] = "published_only"
    if args.queue_reviews:
        actions.extend(queue_targeted_reviews(report, client, args.review_limit))
        report["mode"] = "active"
    if args.apply_published or args.queue_reviews:
        report["actions"] = actions
    write_outputs(report, args.output)


if __name__ == "__main__":
    main()
