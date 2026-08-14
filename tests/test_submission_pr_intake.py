import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "reconcile_submission_prs.py"
SPEC = importlib.util.spec_from_file_location("submission_intake", SCRIPT)
submission_intake = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = submission_intake
SPEC.loader.exec_module(submission_intake)


class SubmissionIntakeTests(unittest.TestCase):
    def test_extracts_explicit_repository_from_pr_body(self):
        pull_request = {
            "body": "## 收录请求\n\n- 仓库: https://github.com/Nwflower/dsh-chat-import",
            "title": "docs: add dsh-chat-import",
        }
        source, urls = submission_intake.extract_repository_urls(pull_request, [])
        self.assertEqual(source, "explicit")
        self.assertEqual(urls, ["https://github.com/Nwflower/dsh-chat-import"])

    def test_falls_back_to_repository_added_in_patch(self):
        pull_request = {"body": "Please add this plugin.", "title": "Add plugin"}
        files = [
            {
                "patch": "+ [plugin](https://github.com/example/dsh-plugin) — Description."
            }
        ]
        source, urls = submission_intake.extract_repository_urls(pull_request, files)
        self.assertEqual(source, "inferred")
        self.assertEqual(urls, ["https://github.com/example/dsh-plugin"])

    def test_multiple_repository_urls_are_ambiguous(self):
        pull_request = {
            "body": (
                "Compare https://github.com/example/one with "
                "https://github.com/example/two"
            ),
            "title": "Add plugins",
        }
        source, urls = submission_intake.extract_repository_urls(pull_request, [])
        self.assertEqual(source, "ambiguous")
        self.assertEqual(len(urls), 2)

    def test_classifies_published_and_candidate_repositories(self):
        catalog = {
            "plugins": [
                {
                    "category": "tools",
                    "name": "published",
                    "repository_id": 10,
                    "url": "https://github.com/example/published",
                }
            ]
        }
        candidates = {
            "candidates": [
                {
                    "category_suggestion": "tools",
                    "name": "candidate",
                    "reasons": ["model_analysis_deferred"],
                    "repository_id": 11,
                    "status": "needs_review",
                    "url": "https://github.com/example/candidate",
                }
            ]
        }
        published = submission_intake.classify_repository(
            "https://github.com/example/published", catalog, candidates
        )
        candidate = submission_intake.classify_repository(
            "https://github.com/example/candidate", catalog, candidates
        )
        self.assertEqual(published["intake_status"], "already_published")
        self.assertEqual(candidate["intake_status"], "candidate_needs_review")
        self.assertEqual(candidate["candidate_reasons"], ["model_analysis_deferred"])

    def test_build_report_skips_automation_pull_request(self):
        class FakeClient:
            repository = "HackSing/dsh-plugins"

            def list_open_pull_requests(self):
                return [
                    {
                        "body": "Repository: https://github.com/example/plugin",
                        "draft": False,
                        "head": {"ref": "feature/plugin"},
                        "html_url": "https://github.com/HackSing/dsh-plugins/pull/5",
                        "number": 5,
                        "title": "Add plugin",
                        "user": {"login": "contributor", "type": "User"},
                    },
                    {
                        "body": "",
                        "draft": True,
                        "head": {"ref": "automation/topic-sync"},
                        "html_url": "https://github.com/HackSing/dsh-plugins/pull/6",
                        "number": 6,
                        "title": "Automated update",
                        "user": {"login": "github-actions[bot]", "type": "Bot"},
                    },
                ]

            def list_pull_request_files(self, number):
                self.last_number = number
                return []

        with tempfile.TemporaryDirectory() as directory:
            original_plugins = submission_intake.PLUGINS_PATH
            original_candidates = submission_intake.CANDIDATES_PATH
            try:
                submission_intake.PLUGINS_PATH = Path(directory) / "plugins.json"
                submission_intake.CANDIDATES_PATH = Path(directory) / "candidates.json"
                report = submission_intake.build_report(FakeClient())
            finally:
                submission_intake.PLUGINS_PATH = original_plugins
                submission_intake.CANDIDATES_PATH = original_candidates
        self.assertEqual(report["open_prs_scanned"], 1)
        self.assertEqual(report["skipped_automation_prs"], 1)
        self.assertEqual(report["submissions"][0]["intake_status"], "new_submission")

    def test_closes_already_published_submission_idempotently(self):
        class FakeClient:
            def __init__(self):
                self.comments = []
                self.labels = []
                self.closed = []

            def ensure_label(self, name, color, description):
                self.labels.append(("ensure", name))

            def list_automation_report_issues(self):
                return []

            def list_pull_request_comments(self, number):
                return []

            def post_comment(self, number, body):
                self.comments.append((number, body))

            def add_labels(self, number, labels):
                self.labels.append((number, labels))

            def remove_label(self, number, label):
                self.labels.append((number, [f"removed:{label}"]))

            def close_pull_request(self, number):
                self.closed.append(number)

        report = {
            "submissions": [
                {
                    "category": "tools",
                    "intake_status": "already_published",
                    "plugin_name": "published-plugin",
                    "pr_number": 12,
                    "repository_id": 120,
                    "repository_url": "https://github.com/example/published-plugin",
                }
            ]
        }
        client = FakeClient()
        with mock.patch.object(
            submission_intake,
            "find_publication_evidence",
            return_value={"commit": "a" * 40},
        ):
            actions = submission_intake.close_already_published(report, client)
        self.assertEqual(actions[0]["action"], "closed_as_published")
        self.assertEqual(client.closed, [12])
        self.assertIn("已通过自动目录收录", client.comments[0][1])
        self.assertIn("dsh-submission:v1", client.comments[0][1])

    def test_existing_acceptance_comment_is_not_duplicated(self):
        class FakeClient:
            def ensure_label(self, name, color, description):
                pass

            def list_automation_report_issues(self):
                return []

            def list_pull_request_comments(self, number):
                return [{"body": "<!-- dsh-submission:v1 status=accepted repository=1 -->"}]

            def post_comment(self, number, body):
                raise AssertionError("duplicate comment")

            def add_labels(self, number, labels):
                pass

            def remove_label(self, number, label):
                pass

            def close_pull_request(self, number):
                self.closed = number

        report = {
            "submissions": [
                {
                    "category": "tools",
                    "intake_status": "already_published",
                    "plugin_name": "published-plugin",
                    "pr_number": 13,
                    "repository_id": 130,
                    "repository_url": "https://github.com/example/published-plugin",
                }
            ]
        }
        client = FakeClient()
        with mock.patch.object(
            submission_intake,
            "find_publication_evidence",
            return_value={"commit": "b" * 40},
        ):
            submission_intake.close_already_published(report, client)
        self.assertEqual(client.closed, 13)

    def test_queues_retryable_submission_for_trusted_targeted_review(self):
        class FakeClient:
            def __init__(self):
                self.dispatched = []
                self.labels = []
                self.comments = []

            def ensure_label(self, name, color, description):
                pass

            def dispatch_workflow(self, workflow, inputs):
                self.dispatched.append((workflow, inputs))

            def add_labels(self, number, labels):
                self.labels.append((number, labels))

            def list_pull_request_comments(self, number):
                return []

            def post_comment(self, number, body):
                self.comments.append((number, body))

            def remove_label(self, number, label):
                self.labels.append((number, [f"removed:{label}"]))

        report = {
            "submissions": [
                {
                    "candidate_reasons": ["model_analysis_deferred"],
                    "draft": False,
                    "intake_status": "candidate_needs_review",
                    "labels": [],
                    "pr_number": 5,
                    "repository_url": "https://github.com/example/dsh-example",
                }
            ]
        }
        client = FakeClient()
        actions = submission_intake.queue_targeted_reviews(report, client, limit=5)
        self.assertEqual(actions[0]["action"], "queued_targeted_review")
        self.assertEqual(client.dispatched[0][0], "sync-topic-plugins.yml")
        self.assertEqual(client.dispatched[0][1]["mode"], "submission")
        self.assertEqual(client.dispatched[0][1]["source_pr"], "5")
        self.assertIn("已进入自动复核", client.comments[0][1])

    def test_reviewing_label_prevents_duplicate_dispatch(self):
        report = {
            "submissions": [
                {
                    "draft": False,
                    "intake_status": "new_submission",
                    "labels": [submission_intake.REVIEWING_LABEL],
                    "pr_number": 6,
                    "repository_url": "https://github.com/example/dsh-example",
                }
            ]
        }

        class FakeClient:
            def list_pull_request_comments(self, number):
                return []

            def dispatch_workflow(self, workflow, inputs):
                raise AssertionError("duplicate workflow dispatch")

        self.assertEqual(
            submission_intake.queue_targeted_reviews(report, FakeClient(), limit=5), []
        )

    def test_requests_information_without_closing_unclear_submission(self):
        client = LifecycleClient()
        report = {
            "submissions": [
                {
                    "candidate_reasons": ["missing_plugin_structure"],
                    "intake_status": "candidate_needs_review",
                    "labels": [submission_intake.REVIEWING_LABEL],
                    "pr_number": 21,
                    "repository_url": "https://github.com/example/unclear",
                }
            ]
        }
        actions = submission_intake.handle_exception_states(report, client)
        self.assertEqual(actions, [{"action": "requested_information", "pr_number": 21}])
        self.assertEqual(client.closed, [])
        self.assertIn("/recheck", client.comments[0][1])
        self.assertIn(
            (21, [submission_intake.NEEDS_INFO_LABEL, submission_intake.AUTOMATION_LABEL]),
            client.labels,
        )

    def test_closes_deterministic_exclusion_as_declined(self):
        client = LifecycleClient()
        report = {
            "submissions": [
                {
                    "candidate_reasons": ["directory_or_collection"],
                    "intake_status": "candidate_excluded",
                    "labels": [submission_intake.REVIEWING_LABEL],
                    "pr_number": 22,
                    "repository_url": "https://github.com/example/directory",
                }
            ]
        }
        actions = submission_intake.handle_exception_states(report, client)
        self.assertEqual(actions, [{"action": "closed_as_declined", "pr_number": 22}])
        self.assertEqual(client.closed, [22])
        self.assertIn("不是安全性或质量评价", client.comments[0][1])

    def test_expires_needs_info_submission_after_fourteen_days(self):
        client = LifecycleClient()
        client.existing_comments = [
            {
                "body": "<!-- dsh-submission:v1 status=needs-info repository=unknown -->",
                "created_at": "2026-07-30T00:00:00Z",
                "user": {"type": "Bot"},
            }
        ]
        report = {
            "submissions": [
                {
                    "intake_status": "not_identified",
                    "labels": [submission_intake.NEEDS_INFO_LABEL],
                    "pr_number": 23,
                }
            ]
        }
        now = submission_intake.dt.datetime(
            2026, 8, 14, tzinfo=submission_intake.dt.timezone.utc
        )
        actions = submission_intake.handle_exception_states(report, client, now=now)
        self.assertEqual(actions, [{"action": "closed_as_expired", "pr_number": 23}])
        self.assertEqual(client.closed, [23])
        self.assertIn("自动归档", client.comments[0][1])

    def test_contributor_recheck_dispatches_new_review_cycle(self):
        client = LifecycleClient()
        client.existing_comments = [
            {
                "body": "<!-- dsh-submission:v1 status=needs-info repository=example/plugin -->",
                "created_at": "2026-08-14T00:00:00Z",
                "user": {"type": "Bot"},
            },
            {
                "body": "/recheck",
                "created_at": "2026-08-14T01:00:00Z",
                "user": {"login": "contributor", "type": "User"},
            },
        ]
        report = {
            "submissions": [
                {
                    "author": "contributor",
                    "candidate_reasons": ["missing_plugin_structure"],
                    "draft": False,
                    "intake_status": "candidate_needs_review",
                    "labels": [submission_intake.NEEDS_INFO_LABEL],
                    "pr_number": 24,
                    "repository_url": "https://github.com/example/plugin",
                }
            ]
        }
        actions = submission_intake.queue_targeted_reviews(report, client, limit=5)
        self.assertEqual(actions[0]["action"], "queued_targeted_review")
        self.assertEqual(client.dispatched[0][1]["source_pr"], "24")
        self.assertIn((24, [f"removed:{submission_intake.NEEDS_INFO_LABEL}"]), client.labels)

    def test_stalled_new_submission_is_retried_after_two_hours(self):
        client = LifecycleClient()
        client.existing_comments = [
            {
                "body": "<!-- dsh-submission:v1 status=reviewing repository=example/plugin -->",
                "created_at": "2026-08-14T00:00:00Z",
                "user": {"type": "Bot"},
            }
        ]
        report = {
            "submissions": [
                {
                    "draft": False,
                    "intake_status": "new_submission",
                    "labels": [submission_intake.REVIEWING_LABEL],
                    "pr_number": 25,
                    "repository_url": "https://github.com/example/plugin",
                }
            ]
        }
        now = submission_intake.dt.datetime(
            2026, 8, 14, 3, tzinfo=submission_intake.dt.timezone.utc
        )
        actions = submission_intake.queue_targeted_reviews(
            report, client, limit=5, now=now
        )
        self.assertEqual(actions[0]["action"], "queued_targeted_review")
        self.assertEqual(client.dispatched[0][1]["source_pr"], "25")


class LifecycleClient:
    def __init__(self):
        self.closed = []
        self.comments = []
        self.dispatched = []
        self.existing_comments = []
        self.labels = []

    def ensure_label(self, name, color, description):
        pass

    def list_pull_request_comments(self, number):
        return list(self.existing_comments)

    def post_comment(self, number, body):
        self.comments.append((number, body))

    def add_labels(self, number, labels):
        self.labels.append((number, labels))

    def remove_label(self, number, label):
        self.labels.append((number, [f"removed:{label}"]))

    def close_pull_request(self, number):
        self.closed.append(number)

    def dispatch_workflow(self, workflow, inputs):
        self.dispatched.append((workflow, inputs))


if __name__ == "__main__":
    unittest.main()
