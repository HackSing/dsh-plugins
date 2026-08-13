# Operations Playbook

This repository is operated as a useful directory first and a backup index second. The public promise is simple classification, bilingual consistency, transparent updates, and evidence-based maintenance.

## Daily: Topic discovery

The `Discover DSH Topic plugins` workflow runs daily at 03:37 UTC and can also be started manually. It queries GitHub for `topic:dsh-plugin`, updates one rolling Draft PR, preserves review decisions already made on that branch, and never writes directly to `main`.

Review the automation output in this order:

1. Confirm that the scan is complete and that the API did not return partial results.
2. Review `proposed` and `needs_review` candidates in `data/topic-candidates.json`.
3. Confirm the repository is a real plugin; never run candidate code as part of discovery.
4. Approve the category and both descriptions before setting `status` to `accepted`.
5. Run `python3 scripts/sync_topic_plugins.py render`, then both validation commands.

Topic removal, repository archival, and repository deletion do not automatically remove a published entry. They create a maintenance decision instead.

## Weekly: DSH Plugin Radar

Publish only when there is meaningful new information. Use an Announcement discussion with:

- newly added plugins;
- material plugin updates discovered during review;
- broken or moved links handled that week;
- one noteworthy use case, without unverifiable ranking language;
- links to the relevant pull requests or issues.

## Monthly: Ecosystem Snapshot

Create a `snapshot-YYYY-MM` Release containing:

- total plugin count;
- additions and removals during the month;
- counts across the four categories;
- broken-link findings and their resolution state;
- contributor acknowledgements;
- explicit verification boundaries.

## Quarterly review

- Review inaccessible and archived repositories.
- Recheck category placement and duplicate coverage.
- Refresh the selection guidance and contribution rules.
- Confirm that English and Chinese entries remain aligned.

## Service targets

- Plugin submission: initial response within 48 hours when practical.
- Broken link: confirm and resolve within 7 days when practical.
- English/Chinese name and URL consistency: 100%.
- Meaningful content update: at least weekly when ecosystem activity warrants it.
- Snapshot release: monthly.

## Metrics

Capture a weekly 14-day snapshot from GitHub Insights → Traffic:

| Week ending | Unique visitors | Views | Unique cloners | Stars | Issues | PRs | Discussions | Top referrer | Top path |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| YYYY-MM-DD |  |  |  |  |  |  |  |  |  |

Do not set growth targets until at least two complete 14-day observation windows exist. Treat Stars as one signal; prioritize discovery, useful participation, and directory quality.
