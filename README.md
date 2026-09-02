# Arthratan Mythology Site

GitHub Pages implementation of the Arthitean Codex website. **GitHub `main` is the authoritative implementation and published source of truth.** Google Drive hosts the coordination board, primary source materials and archival/project snapshots; the legacy Drive browser preview is reference/backup material and must not automatically overwrite repository implementation files.

## Source of truth and release direction

- Website implementation changes are coordinated through `ARTHRATAN_WEBSITE_WORK_BOUNTY_BOARD.md` and committed to GitHub `main` within each task's declared file/scope boundary.
- No scheduled Drive→GitHub writer is permitted to regenerate or overwrite `index.html`, `app.js`, `styles.css`, canon data, artwork or other implementation files.
- Any future Drive import must be explicit/manual, diff-reviewed and SHA/version guarded before it can write to the repository.
- Project snapshots/backups should preferentially flow from verified GitHub state to Drive, not from an older Drive preview back into production.

## In-site wiki editor

The site includes a database-free, passphrase-protected editor for visible page text and shared navigation labels. Published edits are stored in `data/site-edits.json`, so every change is versioned by GitHub and automatically republished by GitHub Pages.

The first owner setup is opened through **Edit page**. It requires a fine-grained GitHub token limited to this repository with **Contents: Read and write** permission. The browser encrypts that token with AES-GCM using a key derived from the shared passphrase; neither the plaintext token nor the passphrase is committed. Use a generated high-entropy passphrase because the encrypted configuration is publicly readable, and revoke the repository token immediately if the shared passphrase is disclosed.

Editors may opt to remember access on a private device. The site re-encrypts the publishing token with a non-exportable device key stored by the browser, making later editing one-press while preserving an explicit **Forget device** path through the editing toolbar.
