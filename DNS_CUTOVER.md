# Arthratan Mythology DNS cutover

Observed from an external GitHub Actions runner on 2026-08-31 at 17:04 UTC.

## Current live routing

- Authoritative nameservers: `ns1.vercel-dns.com`, `ns2.vercel-dns.com`
- Apex A records: `64.29.17.1`, `216.198.79.65`
- Live HTTP/HTTPS response server: `Vercel`
- The domain therefore still serves the previous Vercel deployment.

## Required GitHub Pages routing

Replace the two current apex A records with these four GitHub Pages A records:

- `185.199.108.153`
- `185.199.109.153`
- `185.199.110.153`
- `185.199.111.153`

Optional but recommended for `www`:

- `CNAME www -> micminemx.github.io`

Do not add an apex CNAME for `@` when using these A records.

## GitHub side already prepared

- GitHub Pages is enabled from `main` / repository root.
- `CNAME` contains `arthratanmythology.com`.
- The visual build is published with separate artwork files and chibi assets.
- `.github/workflows/dns-diagnostics.yml` can be rerun after DNS changes to verify propagation externally.

Once the authoritative DNS returns the four GitHub Pages A records, GitHub Pages should serve the custom domain. HTTPS may take additional time to provision after DNS verification.
