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

- **New plugin:** use the `Submit a plugin` Issue form. This is the only official submission path.
- **Metadata correction:** use the `Update plugin information` form.
- **Unavailable repository:** use the `Report a broken link` form.
- **Open-ended recommendation or showcase:** use GitHub Discussions.

Plugin additions are not accepted through pull requests. The trusted automation reads the public plugin repository and generates the catalog, both READMEs, changelog, and report after the submission passes review.

## Repository improvement pull requests

Pull requests remain welcome for automation code, tests, governance, templates, and directory-system documentation. They should not add plugin entries directly.

1. Explain the repository-system problem and the proposed change.
2. Include evidence or tests appropriate to the change.
3. Do not hand-edit generated plugin entries in the READMEs.
4. Update `CHANGELOG.md` when the change affects users or operations.
5. Run `python3 scripts/sync_topic_plugins.py check`, `python3 scripts/validate_directory.py`, and the relevant unit tests.

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
