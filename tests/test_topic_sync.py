import importlib.util
import io
import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "sync_topic_plugins.py"
SPEC = importlib.util.spec_from_file_location("topic_sync", SCRIPT)
topic_sync = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = topic_sync
SPEC.loader.exec_module(topic_sync)


def repository(**overrides):
    value = {
        "id": 101,
        "name": "dsh-example",
        "full_name": "example/dsh-example",
        "html_url": "https://github.com/example/dsh-example",
        "description": "A plugin for DeepSeek Harness that automates research workflows.",
        "archived": False,
        "disabled": False,
        "fork": False,
        "is_template": False,
        "size": 100,
        "pushed_at": "2026-08-14T00:00:00Z",
        "license": {"spdx_id": "MIT"},
    }
    value.update(overrides)
    return value


class ClassificationTests(unittest.TestCase):
    def test_publishable_repository_is_proposed(self):
        result = topic_sync.classify(
            repository(),
            "# dsh-example\nA DSH plugin for automated research workflows.",
            ["package.json", "src"],
            None,
        )
        self.assertEqual(result["status"], "proposed")
        self.assertEqual(result["category_suggestion"], "automation")

    def test_directory_is_excluded(self):
        result = topic_sync.classify(
            repository(
                name="awesome-dsh-plugins",
                full_name="example/awesome-dsh-plugins",
                description="A curated directory of DSH plugins.",
            ),
            "# Awesome DSH plugins",
            ["README.md"],
            None,
        )
        self.assertEqual(result["status"], "excluded")
        self.assertIn("directory_or_collection", result["reasons"])

    def test_missing_readme_is_excluded(self):
        result = topic_sync.classify(repository(), None, [], None)
        self.assertEqual(result["status"], "excluded")
        self.assertIn("missing_readme", result["reasons"])

    def test_manual_rejection_is_preserved(self):
        previous = {
            "status": "rejected",
            "reasons": ["maintainer_rejected"],
            "description_zh": "",
        }
        result = topic_sync.classify(
            repository(), "# Valid plugin", ["dsh.plugin.json"], previous
        )
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["reasons"], ["maintainer_rejected"])

    def test_unclear_repository_needs_review(self):
        result = topic_sync.classify(
            repository(description="Experimental utilities", license=None),
            "# Experimental utilities",
            ["package.json", "src"],
            None,
        )
        self.assertEqual(result["status"], "needs_review")
        self.assertIn("missing_detected_license", result["reasons"])
        self.assertIn("unclear_plugin_evidence", result["reasons"])

    def test_model_analysis_enables_observation_candidate(self):
        candidate = topic_sync.classify(
            repository(),
            "# dsh-example\nA DSH plugin for automated research workflows.",
            ["cordis.patch.yml", "src"],
            None,
        )
        analysis = topic_sync.parse_model_analysis(
            '{"is_plugin":true,"category":"automation",'
            '"description_en":"Automates research workflows.",'
            '"description_zh":"自动执行研究工作流。","confidence":"high",'
            '"evidence":["README identifies a DSH plugin"]}'
        )
        topic_sync.apply_model_analysis(candidate, analysis, auto_publish=False)
        self.assertEqual(candidate["status"], "would_accept")
        self.assertEqual(candidate["description_zh"], "自动执行研究工作流。")

    def test_model_analysis_can_auto_accept(self):
        candidate = topic_sync.classify(
            repository(),
            "# dsh-example\nA DSH plugin for automated research workflows.",
            ["package.json", "src"],
            None,
        )
        analysis = topic_sync.parse_model_analysis(
            '{"is_plugin":true,"category":"automation",'
            '"description_en":"Automates research workflows.",'
            '"description_zh":"自动执行研究工作流。","confidence":"high",'
            '"evidence":["Manifest and README agree"]}'
        )
        topic_sync.apply_model_analysis(candidate, analysis, auto_publish=True)
        self.assertEqual(candidate["status"], "accepted")

    def test_model_analysis_normalizes_deepseek_style_output(self):
        analysis = topic_sync.parse_model_analysis(
            "Analysis complete.\n```json\n"
            '{"is_plugin":true,"category":"Automation",'
            '"description_en":"Automates research workflows",'
            '"description_zh":"自动执行研究工作流","confidence":"HIGH",'
            '"evidence":"README identifies a DSH plugin"}'
            "\n```"
        )
        self.assertEqual(analysis["category"], "automation")
        self.assertEqual(analysis["confidence"], "high")
        self.assertEqual(analysis["evidence"], ["README identifies a DSH plugin"])

    def test_model_client_retries_once_after_invalid_json(self):
        valid = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "is_plugin": True,
                                "category": "automation",
                                "description_en": "Automates research workflows.",
                                "description_zh": "自动执行研究工作流。",
                                "confidence": "high",
                                "evidence": ["Manifest and README agree"],
                            },
                            ensure_ascii=False,
                        )
                    }
                }
            ]
        }
        responses = [
            io.BytesIO(json.dumps({"choices": [{"message": {"content": ""}}]}).encode()),
            io.BytesIO(json.dumps(valid, ensure_ascii=False).encode()),
        ]
        client = topic_sync.OpenAICompatibleClient(
            "test-token", "deepseek-test", "https://example.invalid/v1"
        )
        with mock.patch.object(topic_sync.urllib.request, "urlopen", side_effect=responses) as call:
            analysis = client.analyze(
                repository(), "# dsh-example\nA DSH plugin.", ["package.json+source"]
            )
        self.assertEqual(call.call_count, 2)
        self.assertEqual(analysis["model"], "deepseek-test")
        retry_body = json.loads(call.call_args_list[1].args[0].data.decode("utf-8"))
        self.assertIn("could not be parsed", retry_body["messages"][-1]["content"])

    def test_promoted_candidates_are_stably_grouped_by_readme_category(self):
        catalog = {
            "plugins": [
                {
                    "category": "interaction",
                    "name": "existing-interaction",
                    "url": "https://github.com/example/existing-interaction",
                },
                {
                    "category": "tools",
                    "name": "existing-tool",
                    "url": "https://github.com/example/existing-tool",
                },
            ]
        }
        candidates = {
            "candidates": [
                {
                    "category_suggestion": "automation",
                    "description_en": "Automates workflows.",
                    "description_zh": "自动执行工作流。",
                    "name": "new-automation",
                    "repository_id": 102,
                    "status": "accepted",
                    "url": "https://github.com/example/new-automation",
                },
                {
                    "category_suggestion": "interaction",
                    "description_en": "Adds an interface.",
                    "description_zh": "添加交互界面。",
                    "name": "new-interaction",
                    "repository_id": 103,
                    "status": "accepted",
                    "url": "https://github.com/example/new-interaction",
                },
            ]
        }
        promoted = topic_sync.promote_accepted(catalog, candidates)
        self.assertEqual(len(promoted), 2)
        self.assertEqual(
            [item["name"] for item in catalog["plugins"]],
            [
                "existing-interaction",
                "new-interaction",
                "existing-tool",
                "new-automation",
            ],
        )

    def test_approve_observed_uses_snapshot_limit_and_live_checks(self):
        candidates = {
            "candidates": [
                {
                    "name": f"candidate-{value}",
                    "repository_id": value,
                    "status": "would_accept",
                    "url": f"https://github.com/example/candidate-{value}",
                }
                for value in (201, 202, 203)
            ],
            "schema_version": 1,
        }

        class LiveClient:
            def __init__(self, token=""):
                pass

            def get_json(self, url):
                repository_id = int(url.rsplit("-", 1)[-1])
                return (
                    {
                        "archived": False,
                        "disabled": False,
                        "fork": False,
                        "id": repository_id,
                        "is_template": False,
                        "topics": ["dsh-plugin"],
                    },
                    {},
                )

        with tempfile.TemporaryDirectory() as directory:
            original_path = topic_sync.CANDIDATES_PATH
            try:
                topic_sync.CANDIDATES_PATH = Path(directory) / "topic-candidates.json"
                topic_sync.write_json(topic_sync.CANDIDATES_PATH, candidates)
                with mock.patch.object(topic_sync, "GitHubClient", LiveClient):
                    approved = topic_sync.approve_observed(limit=2)
                saved = json.loads(topic_sync.CANDIDATES_PATH.read_text(encoding="utf-8"))
            finally:
                topic_sync.CANDIDATES_PATH = original_path
        self.assertEqual(approved, 2)
        self.assertEqual(
            [item["status"] for item in saved["candidates"]],
            ["accepted", "accepted", "would_accept"],
        )

    def test_marketing_description_is_rejected(self):
        with self.assertRaises(topic_sync.SyncError):
            topic_sync.parse_model_analysis(
                '{"is_plugin":true,"category":"tools",'
                '"description_en":"The best DSH plugin.",'
                '"description_zh":"提供工具能力。","confidence":"high",'
                '"evidence":["README"]}'
            )

    def test_structure_evidence_requires_manifest_or_source(self):
        self.assertEqual(topic_sync.plugin_structure_evidence(["README.md"]), [])
        self.assertEqual(
            topic_sync.plugin_structure_evidence(["package.json", "src"]),
            ["package.json+source"],
        )

    def test_deferred_candidate_is_not_publishable(self):
        candidate = topic_sync.deferred_candidate(repository())
        self.assertEqual(candidate["status"], "needs_review")
        self.assertFalse(candidate["enriched"])
        self.assertEqual(candidate["reasons"], ["enrichment_deferred"])

    def test_search_shard_converges_when_topic_grows_during_pagination(self):
        class GrowingClient(topic_sync.GitHubClient):
            def __init__(self):
                pass

            def search_page(self, query_text, page):
                if page == 2:
                    return {
                        "total_count": 104,
                        "items": [{"id": value} for value in range(101, 105)],
                    }
                raise AssertionError("unexpected page")

        first = {
            "total_count": 102,
            "items": [{"id": value} for value in range(1, 101)],
        }
        items = GrowingClient().collect_query("topic:dsh-plugin", first)
        self.assertEqual(len(items), 104)

    def test_changelog_and_report_are_idempotent(self):
        promoted = [
            {
                "category_suggestion": "automation",
                "description_en": "Automates research workflows.",
                "description_zh": "自动执行研究工作流。",
                "model_analysis": {
                    "confidence": "high",
                    "evidence": ["README identifies a DSH plugin"],
                },
                "name": "dsh-example",
                "structure_evidence": ["package.json+source"],
                "url": "https://github.com/example/dsh-example",
            }
        ]
        with tempfile.TemporaryDirectory() as directory:
            original_changelog = topic_sync.CHANGELOG_PATH
            original_reports = topic_sync.REPORTS_PATH
            try:
                topic_sync.CHANGELOG_PATH = Path(directory) / "CHANGELOG.md"
                topic_sync.REPORTS_PATH = Path(directory) / "reports"
                topic_sync.CHANGELOG_PATH.write_text(
                    "# Changelog\n\n## Unreleased\n\n### Added\n", encoding="utf-8"
                )
                topic_sync.update_changelog(promoted, "run-1")
                first = topic_sync.CHANGELOG_PATH.read_text(encoding="utf-8")
                topic_sync.update_changelog(promoted, "run-1")
                self.assertEqual(
                    first, topic_sync.CHANGELOG_PATH.read_text(encoding="utf-8")
                )
                report = topic_sync.create_report(
                    promoted,
                    {"candidates": [], "source_total": 100},
                    94,
                    "run-1",
                    date(2026, 8, 14),
                )
                self.assertIsNotNone(report)
                self.assertIn("本次新增插件：1", report.read_text(encoding="utf-8"))
            finally:
                topic_sync.CHANGELOG_PATH = original_changelog
                topic_sync.REPORTS_PATH = original_reports


if __name__ == "__main__":
    unittest.main()
