import importlib.util
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path


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
