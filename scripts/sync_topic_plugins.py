#!/usr/bin/env python3
"""Discover DSH plugins from GitHub Topics and maintain the bilingual directory.

The scheduled path is intentionally approval-gated: discovery updates a candidate
ledger, while only candidates explicitly marked ``accepted`` are promoted into
the published directory by the render command.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PLUGINS_PATH = ROOT / "data" / "plugins.json"
CANDIDATES_PATH = ROOT / "data" / "topic-candidates.json"
READMES = {"en": ROOT / "README.md", "zh": ROOT / "README.zh.md"}
TOPIC = "dsh-plugin"
SELF_REPOSITORY = "hacksing/dsh-plugins"

CATEGORIES = {
    "interaction": {"en": "Interaction & Experience", "zh": "交互与体验"},
    "tools": {"en": "Tools & Capabilities", "zh": "工具与能力"},
    "automation": {"en": "Automation & Agents", "zh": "自动化与智能体"},
    "development": {"en": "Development & Ecosystem", "zh": "开发与生态集成"},
}
CATEGORY_BY_HEADING = {
    value[language]: key
    for key, value in CATEGORIES.items()
    for language in ("en", "zh")
}
ENTRY = re.compile(r"^- \[([^]]+)]\((https://github\.com/[^)]+)\) — (.+)$")
COUNT_PATTERNS = {
    "en": re.compile(r"Explore \*\*\d+ plugins\*\*"),
    "zh": re.compile(r"当前整理 \*\*\d+ 个插件\*\*"),
}
REVIEW_PATTERNS = {
    "en": re.compile(r"Last directory review: \*\*[^*]+\*\*"),
    "zh": re.compile(r"最近一次目录复核：\*\*[^*]+\*\*"),
}
SNAPSHOT_PATTERNS = {
    "en": re.compile(r"This is the first published directory snapshot: \*\*\d+ plugins\*\*"),
    "zh": re.compile(r"这是目录的首个公开快照：共 \*\*\d+ 个插件\*\*"),
}

DIRECTORY_WORDS = re.compile(
    r"(?:^|[-_\s])(awesome|directory|collection|curated|marketplace|catalog|list)(?:$|[-_\s])",
    re.IGNORECASE,
)
LEARNING_WORDS = re.compile(
    r"(?:^|[-_\s])(tutorial|handbook|course|workshop|guide|from[-_\s]?scratch)(?:$|[-_\s])",
    re.IGNORECASE,
)
PLANNED_WORDS = re.compile(r"\b(planned|coming soon|placeholder|roadmap only)\b", re.IGNORECASE)
PLUGIN_EVIDENCE = re.compile(
    r"\b(dsh[-_ ]plugin|plugin for (?:deepseek harness|dsh)|deepseek harness plugin)\b",
    re.IGNORECASE,
)
CATEGORY_RULES = {
    "interaction": re.compile(
        r"\b(ui|ux|chat|conversation|visual|panel|navigation|share|theme|game|emoji|sticker|desktop pet)\b",
        re.IGNORECASE,
    ),
    "automation": re.compile(
        r"\b(agent|workflow|automation|scheduled|scheduler|research|loop|team|orchestrat|monitor|sentinel)\w*\b",
        re.IGNORECASE,
    ),
    "development": re.compile(
        r"\b(integration|bridge|runtime|sandbox|developer|template|notification|security|audit|diagnostic|trace|telemetry|protocol)\w*\b",
        re.IGNORECASE,
    ),
}


class SyncError(RuntimeError):
    """A deterministic sync failure that should stop publication."""


@dataclass(frozen=True)
class ReadmeEntry:
    category: str
    name: str
    url: str
    description: str


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") == rendered:
        return
    path.write_text(rendered, encoding="utf-8")


def parse_readme(path: Path) -> list[ReadmeEntry]:
    current_category = ""
    entries: list[ReadmeEntry] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            current_category = CATEGORY_BY_HEADING.get(line[3:], "")
            continue
        match = ENTRY.match(line)
        if match and current_category:
            entries.append(
                ReadmeEntry(current_category, match.group(1), match.group(2), match.group(3))
            )
    return entries


def bootstrap() -> None:
    if PLUGINS_PATH.exists():
        raise SyncError(f"{PLUGINS_PATH.relative_to(ROOT)} already exists")
    english = parse_readme(READMES["en"])
    chinese = parse_readme(READMES["zh"])
    if [(x.name, x.url, x.category) for x in english] != [
        (x.name, x.url, x.category) for x in chinese
    ]:
        raise SyncError("bilingual README entries do not align")

    plugins = []
    for en, zh in zip(english, chinese):
        plugins.append(
            {
                "category": en.category,
                "description_en": en.description,
                "description_zh": zh.description,
                "name": en.name,
                "repository_id": None,
                "source": f"github-topic:{TOPIC}",
                "url": en.url,
            }
        )
    write_json(PLUGINS_PATH, {"schema_version": 1, "plugins": plugins})
    print(f"Bootstrapped {len(plugins)} bilingual plugins into data/plugins.json.")


class GitHubClient:
    def __init__(self, token: str = "") -> None:
        self.headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "dsh-plugins-topic-sync",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    def get_json(self, url: str) -> tuple[Any, dict[str, str]]:
        request = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                headers = {key.lower(): value for key, value in response.headers.items()}
                return json.load(response), headers
        except urllib.error.HTTPError as exc:
            raise SyncError(f"GitHub API returned HTTP {exc.code} for {url}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise SyncError(f"GitHub API request failed for {url}: {exc}") from exc

    def search(self, max_pages: int | None = None) -> tuple[list[dict[str, Any]], int]:
        repositories: list[dict[str, Any]] = []
        page = 1
        total = 0
        while True:
            query = urllib.parse.urlencode(
                {
                    "q": f"topic:{TOPIC}",
                    "sort": "updated",
                    "order": "desc",
                    "per_page": 100,
                    "page": page,
                }
            )
            payload, _ = self.get_json(f"https://api.github.com/search/repositories?{query}")
            if payload.get("incomplete_results"):
                raise SyncError("GitHub returned incomplete search results; refusing a partial update")
            total = int(payload.get("total_count", 0))
            items = payload.get("items", [])
            repositories.extend(items)
            if not items or len(items) < 100 or (max_pages and page >= max_pages):
                break
            page += 1
        if max_pages is None and len(repositories) != total:
            raise SyncError(
                f"GitHub reported {total} repositories but pagination returned {len(repositories)}"
            )
        return repositories, total

    def readme(self, full_name: str) -> str | None:
        try:
            payload, _ = self.get_json(f"https://api.github.com/repos/{full_name}/readme")
        except SyncError as exc:
            if "HTTP 404" in str(exc):
                return None
            raise
        content = payload.get("content", "")
        if payload.get("encoding") != "base64" or not content:
            return None
        try:
            return base64.b64decode(content).decode("utf-8", errors="replace")[:30000]
        except (ValueError, TypeError):
            return None


def repository_fingerprint(repo: dict[str, Any]) -> str:
    fields = (
        repo.get("full_name"),
        repo.get("description"),
        repo.get("archived"),
        repo.get("disabled"),
        repo.get("fork"),
        repo.get("is_template"),
        repo.get("pushed_at"),
        (repo.get("license") or {}).get("spdx_id"),
    )
    return "|".join("" if value is None else str(value) for value in fields)


def suggest_category(text: str) -> tuple[str, str]:
    scores = {key: len(pattern.findall(text)) for key, pattern in CATEGORY_RULES.items()}
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "tools", "low"
    ordered = sorted(scores.values(), reverse=True)
    confidence = "high" if ordered[0] >= 2 and ordered[0] > ordered[1] else "medium"
    return best, confidence


def classify(repo: dict[str, Any], readme: str | None, previous: dict[str, Any] | None) -> dict[str, Any]:
    full_name = repo["full_name"]
    description = (repo.get("description") or "").strip()
    evidence_text = "\n".join((full_name, description, readme or ""))
    reasons: list[str] = []
    status = "proposed"

    if previous and previous.get("status") in {"rejected", "watch"}:
        status = previous["status"]
        reasons = previous.get("reasons", ["preserved_manual_decision"])
    elif full_name.lower() == SELF_REPOSITORY:
        status, reasons = "excluded", ["current_directory_repository"]
    elif repo.get("fork"):
        status, reasons = "excluded", ["fork_repository"]
    elif repo.get("is_template"):
        status, reasons = "excluded", ["template_repository"]
    elif repo.get("archived") or repo.get("disabled"):
        status, reasons = "excluded", ["inactive_repository"]
    elif DIRECTORY_WORDS.search(full_name + " " + description):
        status, reasons = "excluded", ["directory_or_collection"]
    elif LEARNING_WORDS.search(full_name + " " + description):
        status, reasons = "excluded", ["tutorial_or_handbook"]
    elif readme is None:
        status, reasons = "excluded", ["missing_readme"]
    else:
        if not description:
            reasons.append("missing_repository_description")
        if not repo.get("license"):
            reasons.append("missing_detected_license")
        if PLANNED_WORDS.search(evidence_text):
            reasons.append("planned_or_placeholder")
        if not PLUGIN_EVIDENCE.search(evidence_text):
            reasons.append("unclear_plugin_evidence")
        if reasons:
            status = "needs_review"
        else:
            reasons = ["topic_and_readme_plugin_evidence"]

    category, confidence = suggest_category(evidence_text)
    return {
        "category_suggestion": category,
        "category_confidence": confidence,
        "description_en": description,
        "description_zh": previous.get("description_zh", "") if previous else "",
        "fingerprint": repository_fingerprint(repo),
        "name": repo["name"],
        "reasons": reasons,
        "repository_id": repo["id"],
        "status": status,
        "url": repo["html_url"],
    }


def discover(*, dry_run: bool, max_pages: int | None, no_readme: bool) -> None:
    catalog = load_json(PLUGINS_PATH, {"plugins": []})
    accepted_by_url = {
        item["url"].rstrip("/").lower(): item for item in catalog["plugins"]
    }
    accepted_by_id = {
        int(item["repository_id"]): item
        for item in catalog["plugins"]
        if item.get("repository_id") is not None
    }
    previous_payload = load_json(CANDIDATES_PATH, {"candidates": []})
    previous_by_id = {
        int(item["repository_id"]): item
        for item in previous_payload.get("candidates", [])
        if item.get("repository_id") is not None
    }
    client = GitHubClient(os.environ.get("GITHUB_TOKEN", ""))
    repositories, total = client.search(max_pages=max_pages)
    candidates = []
    skipped_accepted = 0
    for repo in repositories:
        normalized_url = repo["html_url"].rstrip("/").lower()
        accepted = accepted_by_url.get(normalized_url) or accepted_by_id.get(int(repo["id"]))
        if accepted:
            accepted["repository_id"] = int(repo["id"])
            accepted["url"] = repo["html_url"]
            skipped_accepted += 1
            continue
        previous = previous_by_id.get(int(repo["id"]))
        if previous and previous.get("fingerprint") == repository_fingerprint(repo):
            candidates.append(previous)
            continue
        readme = "" if no_readme else client.readme(repo["full_name"])
        candidates.append(classify(repo, readme, previous))

    candidates.sort(key=lambda item: (item["status"], item["name"].casefold(), item["url"]))
    payload = {
        "candidates": candidates,
        "query": f"topic:{TOPIC}",
        "schema_version": 1,
        "source_total": total,
    }
    counts: dict[str, int] = {}
    for item in candidates:
        counts[item["status"]] = counts.get(item["status"], 0) + 1
    scope = f"first {len(repositories)} results" if max_pages else "all results"
    print(
        f"Topic scan completed ({scope}): source={total}, accepted={skipped_accepted}, "
        + ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))
    )
    if dry_run:
        print("Dry run: no files were changed.")
        return
    write_json(PLUGINS_PATH, catalog)
    write_json(CANDIDATES_PATH, payload)


def promote_accepted(catalog: dict[str, Any], candidates_payload: dict[str, Any]) -> int:
    plugins = catalog["plugins"]
    retained = []
    promoted = 0
    urls = {item["url"].rstrip("/").lower() for item in plugins}
    for candidate in candidates_payload.get("candidates", []):
        if candidate.get("status") != "accepted":
            retained.append(candidate)
            continue
        required = (
            candidate.get("name"),
            candidate.get("url"),
            candidate.get("description_en"),
            candidate.get("description_zh"),
            candidate.get("category_suggestion"),
        )
        if not all(required) or candidate["category_suggestion"] not in CATEGORIES:
            raise SyncError(f"accepted candidate {candidate.get('url')} is missing publishable metadata")
        normalized_url = candidate["url"].rstrip("/").lower()
        if normalized_url in urls:
            continue
        plugins.append(
            {
                "category": candidate["category_suggestion"],
                "description_en": candidate["description_en"],
                "description_zh": candidate["description_zh"],
                "name": candidate["name"],
                "repository_id": candidate["repository_id"],
                "source": f"github-topic:{TOPIC}",
                "url": candidate["url"],
            }
        )
        urls.add(normalized_url)
        promoted += 1
    candidates_payload["candidates"] = retained
    return promoted


def render_readme(
    path: Path,
    language: str,
    plugins: list[dict[str, Any]],
    review_date: dt.date | None,
) -> str:
    text = path.read_text(encoding="utf-8")
    count = len(plugins)
    if language == "en":
        text = COUNT_PATTERNS[language].sub(f"Explore **{count} plugins**", text, count=1)
        text = SNAPSHOT_PATTERNS[language].sub(
            f"This is the first published directory snapshot: **{count} plugins**", text, count=1
        )
        if review_date:
            date_text = review_date.strftime("%B %d, %Y").replace(" 0", " ")
            text = REVIEW_PATTERNS[language].sub(
                f"Last directory review: **{date_text}**", text, count=1
            )
    else:
        text = COUNT_PATTERNS[language].sub(f"当前整理 **{count} 个插件**", text, count=1)
        text = SNAPSHOT_PATTERNS[language].sub(
            f"这是目录的首个公开快照：共 **{count} 个插件**", text, count=1
        )
        if review_date:
            date_text = f"{review_date.year} 年 {review_date.month} 月 {review_date.day} 日"
            text = REVIEW_PATTERNS[language].sub(
                f"最近一次目录复核：**{date_text}**", text, count=1
            )

    for index, (category, headings) in enumerate(CATEGORIES.items()):
        heading = headings[language]
        next_headings = list(CATEGORIES.values())[index + 1 :]
        boundary = "|".join(re.escape(f"## {item[language]}") for item in next_headings)
        boundary = boundary or re.escape("## How to choose a plugin" if language == "en" else "## 如何选择插件")
        pattern = re.compile(rf"(## {re.escape(heading)}\n\n)(.*?)(?=\n(?:{boundary})\n)", re.DOTALL)
        entries = [item for item in plugins if item["category"] == category]
        body = "\n".join(
            f'- [{item["name"]}]({item["url"]}) — {item[f"description_{language}"]}'
            for item in entries
        )
        text, replacements = pattern.subn(
            lambda match: match.group(1) + body + "\n", text, count=1
        )
        if replacements != 1:
            raise SyncError(f"could not replace category {heading} in {path.name}")
    return text


def render() -> None:
    catalog = load_json(PLUGINS_PATH, None)
    if not catalog:
        raise SyncError("data/plugins.json is missing; run bootstrap first")
    candidates = load_json(CANDIDATES_PATH, {"schema_version": 1, "candidates": []})
    promoted = promote_accepted(catalog, candidates)
    expected = {
        language: [
            (
                item["category"],
                item["name"],
                item["url"],
                item[f"description_{language}"],
            )
            for item in catalog["plugins"]
        ]
        for language in READMES
    }
    catalog_changed = any(
        [(x.category, x.name, x.url, x.description) for x in parse_readme(path)]
        != expected[language]
        for language, path in READMES.items()
    )
    review_date = dt.datetime.now(dt.timezone.utc).date() if catalog_changed else None
    for language, path in READMES.items():
        rendered = render_readme(path, language, catalog["plugins"], review_date)
        if path.read_text(encoding="utf-8") != rendered:
            path.write_text(rendered, encoding="utf-8")
    write_json(PLUGINS_PATH, catalog)
    if CANDIDATES_PATH.exists() or candidates.get("candidates"):
        write_json(CANDIDATES_PATH, candidates)
    print(f"Rendered {len(catalog['plugins'])} plugins; promoted {promoted} accepted candidates.")


def check() -> None:
    catalog = load_json(PLUGINS_PATH, None)
    if not catalog or catalog.get("schema_version") != 1:
        raise SyncError("data/plugins.json is missing or has an unsupported schema")
    plugins = catalog.get("plugins", [])
    errors = []
    seen_names: set[str] = set()
    seen_urls: set[str] = set()
    for item in plugins:
        missing = [
            key
            for key in ("name", "url", "category", "description_en", "description_zh", "source")
            if not item.get(key)
        ]
        if missing:
            errors.append(f"{item.get('url', '<unknown>')}: missing {', '.join(missing)}")
        if item.get("category") not in CATEGORIES:
            errors.append(f"{item.get('url')}: invalid category")
        if not re.fullmatch(r"https://github\.com/[^/\s]+/[^/\s]+", str(item.get("url", ""))):
            errors.append(f"{item.get('url')}: invalid GitHub repository URL")
        if any("\n" in str(item.get(key, "")) for key in ("name", "description_en", "description_zh")):
            errors.append(f"{item.get('url')}: published fields must be single-line values")
        name = str(item.get("name", "")).casefold()
        url = str(item.get("url", "")).rstrip("/").lower()
        if name in seen_names:
            errors.append(f"duplicate name: {item.get('name')}")
        if url in seen_urls:
            errors.append(f"duplicate URL: {item.get('url')}")
        seen_names.add(name)
        seen_urls.add(url)

    for language, path in READMES.items():
        actual = parse_readme(path)
        expected = [
            (
                item["category"],
                item["name"],
                item["url"],
                item[f"description_{language}"],
            )
            for item in plugins
        ]
        observed = [(x.category, x.name, x.url, x.description) for x in actual]
        if observed != expected:
            errors.append(f"{path.name} does not match data/plugins.json")
    if errors:
        raise SyncError("catalog check failed:\n- " + "\n- ".join(errors))
    print(f"Catalog check passed: {len(plugins)} bilingual plugins match the data source.")


def summary() -> None:
    payload = load_json(CANDIDATES_PATH, None)
    if not payload:
        raise SyncError("data/topic-candidates.json is missing; run discover first")
    counts: dict[str, int] = {}
    for item in payload.get("candidates", []):
        status = item.get("status", "unknown")
        counts[status] = counts.get(status, 0) + 1
    print("## Automated topic discovery summary")
    print()
    print(f"- Query: `{payload.get('query', f'topic:{TOPIC}')}`")
    print(f"- Topic repositories returned: {payload.get('source_total', 0)}")
    for status, count in sorted(counts.items()):
        print(f"- {status.replace('_', ' ').title()}: {count}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("bootstrap", help="create data/plugins.json from the current READMEs")
    discover_parser = subparsers.add_parser("discover", help="scan GitHub Topic repositories")
    discover_parser.add_argument("--dry-run", action="store_true")
    discover_parser.add_argument("--max-pages", type=int)
    discover_parser.add_argument(
        "--no-readme", action="store_true", help="skip README enrichment for an API smoke test"
    )
    subparsers.add_parser("render", help="promote approved candidates and regenerate READMEs")
    subparsers.add_parser("check", help="validate the structured catalog and READMEs")
    subparsers.add_parser("summary", help="print the saved candidate summary as Markdown")
    args = parser.parse_args()
    try:
        if args.command == "bootstrap":
            bootstrap()
        elif args.command == "discover":
            discover(dry_run=args.dry_run, max_pages=args.max_pages, no_readme=args.no_readme)
        elif args.command == "render":
            render()
        elif args.command == "check":
            check()
        else:
            summary()
    except (SyncError, json.JSONDecodeError) as exc:
        print(f"Topic sync failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
