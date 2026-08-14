# Changelog

All meaningful directory changes are recorded here. Dates use `YYYY-MM-DD`.

## Unreleased

### Added

<!-- topic-sync:31819872080 -->
- Automatically added [Code2Skill](https://github.com/leechen298/Code2Skill) to Development & Ecosystem from the `dsh-plugin` topic.

<!-- topic-sync:31809900757 -->
- Automatically added [dsh-chat-import](https://github.com/Nwflower/dsh-chat-import) to Tools & Capabilities from the `dsh-plugin` topic.

<!-- topic-sync:31801804894 -->
- Automatically added [DeepJIT](https://github.com/fly3366/DeepJIT) to Automation & Agents from the `dsh-plugin` topic.
- Automatically added [dsh-agent-message](https://github.com/GengDaPeng/dsh-agent-message) to Interaction & Experience from the `dsh-plugin` topic.
- Automatically added [dsh-enhance](https://github.com/vcxmug/dsh-enhance) to Tools & Capabilities from the `dsh-plugin` topic.
- Automatically added [dsh-plugins-store](https://github.com/ZASENJC/dsh-plugins-store) to Tools & Capabilities from the `dsh-plugin` topic.
- Automatically added [dsh-telemetry-redactor](https://github.com/030611/dsh-telemetry-redactor) to Tools & Capabilities from the `dsh-plugin` topic.

<!-- topic-sync:31800120653 -->
- Automatically added [dsh-drop-to-path](https://github.com/loudMore/dsh-drop-to-path) to Interaction & Experience from the `dsh-plugin` topic.
- Automatically added [dsh-email](https://github.com/STARDUSTLC666/dsh-email) to Tools & Capabilities from the `dsh-plugin` topic.
- Automatically added [widget-dock](https://github.com/MorGogh/widget-dock) to Tools & Capabilities from the `dsh-plugin` topic.

<!-- topic-sync:31799435506 -->
- Automatically added [dsh-model-modes](https://github.com/DTSFO/dsh-model-modes) to Interaction & Experience from the `dsh-plugin` topic.

- Added a structured plugin catalog and an approval-gated GitHub Topic discovery script.
- Added a daily workflow that maintains one rolling Draft PR for `dsh-plugin` candidates.
- Added deterministic candidate-classification tests and maintainer review guidance.
- Added provider-neutral model assessment, observation and automatic-publication modes, permanent collection reports, report delivery recovery, and a weekly exception summary.
- Added the Chinese full-automation product and operating plan under `docs/`.
- Added detailed Chinese methodologies for plugin-directory content operations and full automation.

### Changed

- Made `data/plugins.json` the source of truth for generated English and Chinese directory entries.
- Expanded successful collection into one transaction covering catalog data, both READMEs, CHANGELOG, validation, merge, remote confirmation, and report notification.
- Unified developer submissions under the `Submit a plugin` Issue Form, with automated Issue review and lifecycle feedback; legacy catalog-only plugin PRs now receive a safe redirect and close without merging.

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
