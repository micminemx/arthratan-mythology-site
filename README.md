# Arthratan Mythology Site

Public GitHub Pages mirror of the canonical Arthitean Codex website source maintained in Google Drive. The live site includes the visual atlas, Arthratan artwork, chibi navigation, canon data, and custom domain configuration.

## In-site wiki editor

The site includes a database-free, passphrase-protected editor for visible page text and shared navigation labels. Published edits are stored in `data/site-edits.json`, so every change is versioned by GitHub and automatically republished by GitHub Pages.

The first owner setup is opened through **Edit page**. It requires a fine-grained GitHub token limited to this repository with **Contents: Read and write** permission. The browser encrypts that token with AES-GCM using a key derived from the shared passphrase; neither the plaintext token nor the passphrase is committed. Use a generated high-entropy passphrase because the encrypted configuration is publicly readable, and revoke the repository token immediately if the shared passphrase is disclosed.
