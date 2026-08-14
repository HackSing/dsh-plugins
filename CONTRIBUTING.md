# Contributing to DSH Plugins

Thank you for helping keep this bilingual directory useful and current.

## What belongs here

A submitted project should:

- be publicly accessible and materially related to DeepSeek Harness;
- provide a clear README with purpose and installation or usage guidance;
- identify its license or usage terms;
- avoid obvious malicious, deceptive, or unrelated behavior;
- fit one primary category in this directory.

Inclusion means the project is discoverable. It is not a compatibility certification, security review, or endorsement.

## Contribution paths

- **New plugin:** use the `Submit a plugin` issue form or open a pull request.
- **Metadata correction:** use the `Update plugin information` form.
- **Unavailable repository:** use the `Report a broken link` form.
- **Open-ended recommendation or showcase:** use GitHub Discussions.

## Pull request requirements

1. Add or update the plugin in `data/plugins.json`; do not hand-edit generated directory entries.
2. Keep the plugin in one primary category only.
3. Provide matching, factual English and Chinese descriptions without rankings or unverifiable claims.
4. Run `python3 scripts/sync_topic_plugins.py render` to regenerate both READMEs.
5. Update `CHANGELOG.md` under `Unreleased`.
6. Run `python3 scripts/sync_topic_plugins.py check` and `python3 scripts/validate_directory.py` before submitting.

## Topic candidate review

The daily discovery workflow stores assessed repositories in `data/topic-candidates.json` and opens or updates one rolling pull request. Observation mode never publishes candidates. In publish mode, deterministic rules and the configured model provider may automatically accept a candidate only when both produce a high-confidence result.

To approve a candidate:

1. Verify that the repository contains a real DSH plugin and usable documentation.
2. Review its license, permissions, dependencies, installation, and removal path.
3. Set `status` to `accepted`.
4. Confirm `category_suggestion`, `description_en`, and `description_zh`.
5. Run `python3 scripts/sync_topic_plugins.py render`; the candidate will move into the published catalog.

Use `rejected` for a confirmed non-plugin or unsuitable project, and `watch` when the project may become eligible later. These manual decisions are preserved until the repository changes materially.

Successful automatic additions also update `CHANGELOG.md`, generate a permanent file under `reports/sync/`, and create an `automation-report` Issue after the merged commit is confirmed remotely.

Maintainers may adjust wording or placement to keep the directory consistent. A missing license, inaccessible repository, unclear DSH relationship, or unverified claim may pause acceptance.

## Review targets

- Initial response to a plugin submission: within 48 hours when practical.
- Broken-link review: within 7 days when practical.
- English/Chinese directory consistency: 100%.

## License

By contributing editorial content to this repository, you agree that your contribution may be distributed under [CC BY 4.0](LICENSE). Linked third-party projects retain their own licenses.
