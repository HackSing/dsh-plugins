# Operations Playbook

This repository is operated as a useful directory first and a backup index second. The public promise is simple classification, bilingual consistency, transparent updates, and evidence-based maintenance.

## Daily: Topic discovery

The `Discover and publish DSH Topic plugins` workflow runs daily at 03:37 UTC and can also be started manually. It queries GitHub for `topic:dsh-plugin`, updates one rolling automation branch, and uses a configured OpenAI-compatible model provider to produce structured bilingual assessments. Repository variable `AUTO_PUBLISH=false` keeps the workflow in observation mode; `AUTO_PUBLISH=true` permits high-confidence candidates to be merged after the same workflow passes every validation.

Model configuration uses repository variables `LLM_BASE_URL` and `LLM_MODEL`, plus encrypted repository Secret `LLM_API_KEY`. GitHub Models is not supported because GitHub retired the service on July 30, 2026. Missing provider configuration degrades safely to `model_provider_unconfigured` and blocks automatic publication.

GitHub Search exposes at most 1,000 results per query, so the scanner automatically partitions larger Topics by repository creation date and rejects incomplete shards. README and root-structure enrichment is bounded per run; deferred candidates continue on later runs instead of exhausting the repository API quota.

Review the automation output in this order:

1. Confirm that the scan is complete and that the API did not return partial results.
2. Review `proposed` and `needs_review` candidates in `data/topic-candidates.json`.
3. Confirm the repository is a real plugin; never run candidate code as part of discovery.
4. In observation mode, review `would_accept` results to calibrate false positives; ordinary daily operation does not require per-plugin approval.
5. In publish mode, verify that each successful run produced a repository report and an `automation-report` Issue.

Topic removal, repository archival, and repository deletion do not automatically remove a published entry. They create a maintenance decision instead.

The `Weekly plugin candidate exceptions` workflow groups ambiguous candidates into one deduplicated Issue. It does not create an Issue when the exception snapshot has not changed.

### Publication report recovery

Every report under `reports/sync/` is keyed to the commit that first added it. At the end of each daily run, the workflow searches all published reports for their `report-sha` Issue marker and creates any missing notification. A notification failure therefore fails delivery without adding the plugin twice, and a later run retries it.

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
