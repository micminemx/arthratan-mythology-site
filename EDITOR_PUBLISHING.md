# Arthratan Codex — Secure Editorial Publication

## Security posture

The public GitHub Pages build is **read-only**. It must never contain a reusable repository-write credential, encrypted credential payload, shared-passphrase unlock path, browser-side GitHub write client, or any equivalent mechanism that turns possession of a public asset plus a secret phrase into repository access.

The former public browser editor has been retired. Public visitors can read the source-preserving Codex, but publication is performed only through GitHub-authenticated tooling.

## Legitimate editing path

1. Sign in to GitHub with the editor's individual GitHub account. Do not share accounts, personal access tokens, session cookies, recovery codes, or shared publication passwords.
2. Work from the latest `main` revision and create a dedicated branch for the intended change.
3. Edit only the files allowed by the active bounty/task scope. Canon/source-preservation rules remain mandatory.
4. Open a pull request back to `main` with the task ID in the title or description and describe the exact files changed.
5. Resolve conflicts against the latest `main`; never force-overwrite a stale file. Re-read the target file after rebasing/merging and preserve unrelated concurrent work.
6. Review the diff and run the repository's applicable syntax, schema, preservation, route, and smoke checks before merge. As the CI quality gate is expanded, its required checks become the publication gate.
7. Merge using the authenticated GitHub account so the author, review discussion, exact commit and rollback point remain auditable.

For collaborators, grant only the minimum GitHub repository role needed for their work and remove access when it is no longer required. Prefer GitHub's normal account authentication and repository permissions over long-lived personal access tokens.

## Credential rules

- Never commit a GitHub token, deploy key, session token, encrypted token blob, password-derived token wrapper, or credential-recovery material to a public site asset.
- Never place reusable repository-write credentials in `localStorage`, `sessionStorage`, IndexedDB, service-worker caches, downloadable JSON, JavaScript bundles, HTML, CSS, source maps, or other browser-readable storage.
- If an automation later needs repository write access, keep its secret in the provider's protected server-side secret store, grant least privilege, scope it narrowly, and prefer short-lived credentials.
- A credential that was ever distributed to the public build must be treated as exposed even if it was encrypted. It must be revoked/rotated; deleting the ciphertext does not retroactively make the old credential trustworthy.

## Previous credential rotation

The credential represented by the retired `data/editor-config.json` payload must be revoked/rotated in the GitHub account or organization that issued it. The repository connector used for this maintenance task does not expose personal-access-token administration, so removal from the public build and credential revocation are separate actions.

After revocation, verify that the old credential can no longer authenticate and record that verification on the work bounty board. Do **not** paste the old token into logs, issues, commits, chat, CI output, or this document while testing.

## Conflict handling

Repository writes must use the current Git blob SHA/version or a branch/PR based on the latest target. If GitHub reports a conflict, fetch the latest file, merge only the intended scoped change, rerun validation, and retry. Force pushes to `main` are not an editorial conflict-resolution mechanism.

## Browser and content-security review

The public site should remain usable without any privileged API credential. Browser code may fetch public read-only content, but it should not require authenticated cross-origin GitHub API calls for publication.

Where compatible with the current static architecture, future hardening should prefer a Content Security Policy that restricts scripts and connections to explicitly required origins, avoids `unsafe-eval`, and minimizes inline executable code. External links opened in a new browsing context should use appropriate `rel="noopener noreferrer"` behavior. These controls must not remove or rewrite preserved canon/source material.

## Failure behavior

If GitHub authentication, review, validation or deployment is unavailable, publication fails closed: the public site remains read-only and the current deployed canon stays intact. No client-side fallback may silently regain direct repository-write capability.
