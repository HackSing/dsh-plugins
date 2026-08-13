import importlib.util
import sys
import unittest
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
            None,
        )
        self.assertEqual(result["status"], "excluded")
        self.assertIn("directory_or_collection", result["reasons"])

    def test_missing_readme_is_excluded(self):
        result = topic_sync.classify(repository(), None, None)
        self.assertEqual(result["status"], "excluded")
        self.assertIn("missing_readme", result["reasons"])

    def test_manual_rejection_is_preserved(self):
        previous = {
            "status": "rejected",
            "reasons": ["maintainer_rejected"],
            "description_zh": "",
        }
        result = topic_sync.classify(repository(), "# Valid plugin", previous)
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["reasons"], ["maintainer_rejected"])

    def test_unclear_repository_needs_review(self):
        result = topic_sync.classify(
            repository(description="Experimental utilities", license=None),
            "# Experimental utilities",
            None,
        )
        self.assertEqual(result["status"], "needs_review")
        self.assertIn("missing_detected_license", result["reasons"])
        self.assertIn("unclear_plugin_evidence", result["reasons"])


if __name__ == "__main__":
    unittest.main()
