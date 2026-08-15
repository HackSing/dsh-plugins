import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
SCRIPT = SCRIPTS / "sync_collection_reports.py"
SPEC = importlib.util.spec_from_file_location("collection_report_sync", SCRIPT)
report_sync = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(report_sync)
topic_sync = report_sync.topic_sync


def git(directory: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=directory,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def report_payload():
    return {
        "schema_version": 1,
        "report_type": "plugin_collection",
        "status": "pending_publication",
        "run_id": "run-1",
        "review_date": "2026-08-15",
        "source_total": 1,
        "before_count": 0,
        "added_count": 1,
        "after_count": 1,
        "candidate_counts": {},
        "plugins": [
            {
                "category": "tools",
                "category_en": "Tools & Capabilities",
                "category_zh": "工具与能力",
                "confidence": "high",
                "description_en": "Adds a tool.",
                "description_zh": "增加一个工具。",
                "evidence": ["README"],
                "name": "dsh-example",
                "structure_evidence": ["package.json+source"],
                "url": "https://github.com/example/dsh-example",
            }
        ],
        "publication": {},
        "content_material": {
            "headline_zh": "DSH 插件目录新增 1 个插件",
            "summary_zh": "本次新增 dsh-example。",
            "fact_boundary_zh": "目录收录不代表安全审计。",
        },
    }


class CollectionReportSyncTests(unittest.TestCase):
    def test_selects_final_artifact_over_source_for_the_same_run(self):
        artifacts = [
            {
                "id": 1,
                "name": "plugin-collection-report-source-123",
                "created_at": "2026-08-15T00:00:00Z",
                "workflow_run": {"id": 123},
            },
            {
                "id": 2,
                "name": "plugin-collection-report-abcdef-123",
                "created_at": "2026-08-15T00:01:00Z",
                "workflow_run": {"id": 123},
            },
        ]
        selected = report_sync.select_report_artifacts(artifacts)
        self.assertEqual([item["id"] for item in selected], [2])

    def test_archives_a_final_report_once_by_publication_sha(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = root / "repo"
            archive = root / "archive"
            bundle = root / "bundle"
            (repository / "data").mkdir(parents=True)
            git(repository, "init", "-q")
            git(repository, "config", "user.name", "Test")
            git(repository, "config", "user.email", "test@example.com")
            (repository / "CHANGELOG.md").write_text(
                "# Changelog\n\n<!-- topic-sync:run-1 -->\n",
                encoding="utf-8",
            )
            (repository / "data" / "plugins.json").write_text(
                json.dumps(
                    {
                        "plugins": [
                            {
                                "name": "dsh-example",
                                "url": "https://github.com/example/dsh-example",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            git(repository, "add", ".")
            git(repository, "commit", "-q", "-m", "publish")
            commit_sha = git(repository, "rev-parse", "HEAD")
            payload = report_payload()
            topic_sync.write_report_bundle(bundle, payload)
            topic_sync.finalize_report_bundle(
                bundle,
                commit_sha=commit_sha,
                published_at="2026-08-15T00:00:00Z",
                run_url="https://github.com/HackSing/dsh-plugins/actions/runs/run-1",
                pr_url="https://github.com/HackSing/dsh-plugins/pull/1",
            )
            records = []
            artifact = {
                "id": 9,
                "name": f"plugin-collection-report-{commit_sha[:12]}-run-1",
            }
            first = report_sync.archive_bundle(
                bundle,
                artifact=artifact,
                archive_root=archive,
                manifest_records=records,
                gh="gh",
                repository="HackSing/dsh-plugins",
                repo_root=repository,
            )
            second = report_sync.archive_bundle(
                bundle,
                artifact=artifact,
                archive_root=archive,
                manifest_records=records,
                gh="gh",
                repository="HackSing/dsh-plugins",
                repo_root=repository,
            )
            self.assertEqual(first, "archived")
            self.assertEqual(second, "duplicate")
            self.assertTrue((archive / "latest.md").exists())
            self.assertEqual(len((archive / "manifest.jsonl").read_text().splitlines()), 1)
            date_dir = archive / "2026-08-15"
            self.assertEqual(len(list(date_dir.glob("*.md"))), 1)
            self.assertEqual(len(list(date_dir.glob("*.json"))), 1)
            self.assertTrue(
                (date_dir / f"plugin-collection-report-{commit_sha[:12]}-run-1.md").exists()
            )

    def test_recovers_a_source_bundle_after_the_publication_commit_exists(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = root / "repo"
            bundle = root / "bundle"
            (repository / "data").mkdir(parents=True)
            git(repository, "init", "-q")
            git(repository, "config", "user.name", "Test")
            git(repository, "config", "user.email", "test@example.com")
            (repository / "CHANGELOG.md").write_text(
                "# Changelog\n\n<!-- topic-sync:run-1 -->\n",
                encoding="utf-8",
            )
            (repository / "data" / "plugins.json").write_text(
                json.dumps(
                    {
                        "plugins": [
                            {
                                "name": "dsh-example",
                                "url": "https://github.com/example/dsh-example",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            git(repository, "add", ".")
            git(repository, "commit", "-q", "-m", "publish")
            commit_sha = git(repository, "rev-parse", "HEAD")
            git(repository, "update-ref", "refs/remotes/origin/main", commit_sha)
            topic_sync.write_report_bundle(bundle, report_payload())
            with mock.patch.object(
                report_sync,
                "publication_pr_metadata",
                return_value=(
                    "https://github.com/HackSing/dsh-plugins/pull/1",
                    "2026-08-15T00:00:00Z",
                ),
            ):
                recovered = report_sync.finalize_source_report(
                    bundle,
                    report_payload(),
                    gh="gh",
                    repository="HackSing/dsh-plugins",
                    repo_root=repository,
                )
            self.assertIsNotNone(recovered)
            self.assertEqual(recovered["publication"]["commit_sha"], commit_sha)
            self.assertEqual(recovered["status"], "published")

    def test_archives_a_legacy_markdown_report(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = root / "repo"
            archive = root / "archive"
            report = root / "legacy.md"
            (repository / "data").mkdir(parents=True)
            git(repository, "init", "-q")
            git(repository, "config", "user.name", "Test")
            git(repository, "config", "user.email", "test@example.com")
            (repository / "CHANGELOG.md").write_text(
                "# Changelog\n\n<!-- topic-sync:run-1 -->\n", encoding="utf-8"
            )
            (repository / "data" / "plugins.json").write_text(
                json.dumps(
                    {
                        "plugins": [
                            {
                                "name": "dsh-example",
                                "url": "https://github.com/example/dsh-example",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            git(repository, "add", ".")
            git(repository, "commit", "-q", "-m", "publish")
            commit_sha = git(repository, "rev-parse", "HEAD")
            git(repository, "update-ref", "refs/remotes/origin/main", commit_sha)
            report.write_text(
                "# DSH 插件自动收录报告 — 2026-08-15\n\n"
                "- 运行编号：`run-1`\n"
                "- 本次新增插件：1\n\n"
                "## 新增插件\n\n"
                "### [dsh-example](https://github.com/example/dsh-example)\n",
                encoding="utf-8",
            )
            records = []
            artifact = {
                "id": 10,
                "name": "plugin-collection-report-run-1",
                "workflow_run": {"id": "run-1"},
            }
            outcome = report_sync.archive_legacy_markdown(
                report,
                artifact=artifact,
                archive_root=archive,
                manifest_records=records,
                repo_root=repository,
            )
            self.assertEqual(outcome, "archived")
            date_dir = archive / "2026-08-15"
            self.assertEqual(len(list(date_dir.glob("*.md"))), 1)
            metadata = json.loads(
                next(date_dir.glob("*.json")).read_text()
            )
            self.assertEqual(metadata["publication"]["commit_sha"], commit_sha)
            self.assertEqual(metadata["report_type"], "legacy_markdown_plugin_collection")


if __name__ == "__main__":
    unittest.main()
