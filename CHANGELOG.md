# Changelog

All meaningful directory changes are recorded here. Dates use `YYYY-MM-DD`.

## Unreleased

### Added

- Added a structured plugin catalog and an approval-gated GitHub Topic discovery script.
- Added a daily workflow that maintains one rolling Draft PR for `dsh-plugin` candidates.
- Added deterministic candidate-classification tests and maintainer review guidance.
- Added GitHub Models assessment, observation and automatic-publication modes, permanent collection reports, report delivery recovery, and a weekly exception summary.
- Added the Chinese full-automation product and operating plan under `docs/`.

### Changed

- Made `data/plugins.json` the source of truth for generated English and Chinese directory entries.
- Expanded successful collection into one transaction covering catalog data, both READMEs, CHANGELOG, validation, merge, remote confirmation, and report notification.

### Removed

### Fixed

- Updated the workflow checkout runtime after live Actions verification reported the Node.js 20 deprecation warning.

## snapshot-2026-08 — 2026-08-13

### Added

- Published the first bilingual directory snapshot with 94 plugins.
- Grouped entries into four broad categories: Interaction & Experience (40), Tools & Capabilities (20), Automation & Agents (10), and Development & Ecosystem (24).
- Added contribution forms, community Discussions, directory validation, and a weekly link-health workflow.

### Verification boundary

- English and Chinese names and repository URLs are aligned one to one.
- Directory inclusion does not certify installation, compatibility, maintenance quality, or security.
