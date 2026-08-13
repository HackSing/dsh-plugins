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

1. Update both `README.md` and `README.zh.md`.
2. Keep the plugin in one primary category only.
3. Preserve matching names and repository URLs across both files.
4. Write one factual sentence about the plugin's primary value; avoid rankings and unverifiable claims.
5. Update `CHANGELOG.md` under `Unreleased`.
6. Run `python3 scripts/validate_directory.py` before submitting.

Maintainers may adjust wording or placement to keep the directory consistent. A missing license, inaccessible repository, unclear DSH relationship, or unverified claim may pause acceptance.

## Review targets

- Initial response to a plugin submission: within 48 hours when practical.
- Broken-link review: within 7 days when practical.
- English/Chinese directory consistency: 100%.

## License

By contributing editorial content to this repository, you agree that your contribution may be distributed under [CC BY 4.0](LICENSE). Linked third-party projects retain their own licenses.
