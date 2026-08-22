#!/usr/bin/env python3
"""Validate the bilingual DSH plugin directory and optionally check links."""

from __future__ import annotations

import argparse
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = {
    "README.md": [
        "Interaction & Experience",
        "Tools & Capabilities",
        "Knowledge & Memory",
        "Content & Creation",
        "Integrations & Connectors",
        "Automation & Agents",
        "Development & Ecosystem",
    ],
    "README.zh.md": [
        "交互与体验",
        "工具与能力",
        "知识与记忆",
        "内容与创作",
        "集成与连接",
        "自动化与智能体",
        "开发与生态集成",
    ],
}
ENTRY = re.compile(r"^- \[([^]]+)]\((https://github\.com/[^)]+)\) — (.+)$")
DECLARED = re.compile(r"\*\*(\d+) (?:plugins|个插件)\*\*")


@dataclass(frozen=True)
class Plugin:
    category: str
    name: str
    url: str


def parse(path: Path, categories: list[str]) -> list[Plugin]:
    entries: list[Plugin] = []
    current = ""
    allowed = set(categories)
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            current = line[3:]
            continue
        match = ENTRY.match(line)
        if match and current in allowed:
            entries.append(Plugin(current, match.group(1), match.group(2)))
    return entries


def validate() -> list[Plugin]:
    parsed: dict[str, list[Plugin]] = {}
    errors: list[str] = []
    for filename, categories in CATEGORIES.items():
        path = ROOT / filename
        text = path.read_text(encoding="utf-8")
        entries = parse(path, categories)
        parsed[filename] = entries
        declared = DECLARED.search(text)
        if not declared or int(declared.group(1)) != len(entries):
            errors.append(f"{filename}: declared count does not match {len(entries)} entries")
        names = [item.name for item in entries]
        urls = [item.url for item in entries]
        if len(names) != len(set(names)):
            errors.append(f"{filename}: duplicate plugin name")
        if len(urls) != len(set(urls)):
            errors.append(f"{filename}: duplicate plugin URL")

    en = parsed["README.md"]
    zh = parsed["README.zh.md"]
    if [(item.name, item.url) for item in en] != [(item.name, item.url) for item in zh]:
        errors.append("README.md and README.zh.md do not have matching ordered names and URLs")

    if errors:
        print("Directory validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)

    category_count = len(CATEGORIES["README.md"])
    print(
        f"Directory validation passed: {len(en)} bilingual plugin entries "
        f"across {category_count} categories."
    )
    return en


def check_links(entries: list[Plugin]) -> None:
    token = os.environ.get("GITHUB_TOKEN", "")
    broken: list[str] = []
    warnings: list[str] = []
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "dsh-plugins-link-check"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    for item in entries:
        request = urllib.request.Request(item.url, headers=headers, method="HEAD")
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                if response.status >= 400:
                    warnings.append(f"{item.name}: HTTP {response.status} — {item.url}")
        except urllib.error.HTTPError as exc:
            message = f"{item.name}: HTTP {exc.code} — {item.url}"
            if exc.code in (404, 410):
                broken.append(message)
            else:
                warnings.append(message)
        except (urllib.error.URLError, TimeoutError) as exc:
            warnings.append(f"{item.name}: transient check error — {exc}")

    for warning in warnings:
        print(f"WARNING: {warning}")
    if broken:
        print("Broken plugin links:", file=sys.stderr)
        for item in broken:
            print(f"- {item}", file=sys.stderr)
        raise SystemExit(2)
    print(f"Link check passed: no confirmed 404/410 responses across {len(entries)} repositories.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-links", action="store_true")
    args = parser.parse_args()
    entries = validate()
    if args.check_links:
        check_links(entries)


if __name__ == "__main__":
    main()
