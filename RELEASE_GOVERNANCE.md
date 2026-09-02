# Arthratan Mythology publication governance

GitHub `main` is the implementation and publication source of truth. Google Drive is coordination/source/archive storage and must not automatically overwrite the repository.

## Release checks

A candidate is release-eligible only after the following checks pass on the exact candidate SHA:

1. **Publication Quality Gate / `publication-gate`** — JavaScript syntax, JSON parsing, QA-006 data contracts/references, Zubaida preservation counts, required archive assets/routes, and a local Chromium reader/mobile smoke test.
2. **QA-006 Data Contract Validation / `validate-data-contracts`** — dataset schema and referential-integrity validation. The workflow currently expands the compact ZUB-003 `e`/`t` encoding only in the ephemeral runner checkout so the existing validator evaluates the semantic entity/transmission objects without modifying the canonical JSON.
3. **Verify live Zubaida source archive / `verify-live-source-archive`** — post-deployment Chromium proof against `https://arthratanmythology.com/`. It waits for the custom-domain publication surface to byte-match the checked-out candidate, then verifies the archive UI, 118/118 public source files, first/middle/final verbatim source rendering, search, deep-link reload, browser history, mobile overflow, and browser console/runtime errors. Its JSON evidence is uploaded as a workflow artifact rather than committed back into `main`.

The exact candidate/deployed SHA is therefore traceable in the GitHub Actions run metadata, the publication-gate step summary, and the live-verification artifact name/content.

## Required repository enforcement

At the time this document was introduced, `main` was not branch-protected and had no required status checks. Workflow files alone cannot prevent GitHub Pages' branch-source deployment from publishing a direct push before checks finish.

To make the gate **enforcing rather than observational**, repository administration must configure one of these equivalent protected-publication models:

### Preferred: protected `main`

- Require pull requests before changes reach `main`.
- Require the `publication-gate` check before merge.
- Require `validate-data-contracts` before merge while QA-006 remains a separate check.
- Prevent bypass/direct pushes except an explicitly controlled emergency path.
- Keep GitHub Pages sourced from `main` only after the protected merge.

This preserves one publication source of truth: a candidate is tested on its branch/PR; only a passing candidate can become `main`; Pages then publishes that validated `main` SHA.

### Equivalent: protected release branch / Pages Actions workflow

If the repository's GitHub plan/workflow requires direct worker pushes to `main`, use a separate protected release ref or GitHub Pages Actions deployment that accepts only a candidate SHA whose publication gate passed. Switching the Pages build source is a repository-administration action and must not be simulated by a second content copy or Drive-generated site.

Do **not** re-enable the retired scheduled Drive-to-GitHub overwrite or any public browser-side GitHub write credential.

## Deployment verification

For every release checkpoint:

1. Record the intended `main` SHA.
2. Confirm the GitHub Pages build/deploy check succeeds for that SHA.
3. Run **Verify live Zubaida source archive** manually if its path trigger did not run for the candidate.
4. Accept the release only when the custom-domain verifier confirms the live publication surface matches the candidate and all required browser checks pass.
5. Record the deployed SHA in the coordination/bounty board when the relevant release task completes.

A GitHub Pages `success` result alone is not sufficient if QA-006 or the publication gate is failing.

## Rollback

Rollback is repository-first and auditable:

1. Identify the last known-good deployed commit whose required checks and live verification passed.
2. Revert the faulty commit(s) with a new Git commit; do not force-reset shared history and do not restore a stale Drive snapshot.
3. Run the same publication gate on the revert candidate.
4. Publish the validated revert through the same protected path.
5. Re-run custom-domain live verification and record the new deployed revert SHA.

If an emergency requires immediate mitigation, prefer a minimal additive/revert commit over broad file replacement. Preserve source-canon files and concurrent worker changes unless they are the verified defect.
