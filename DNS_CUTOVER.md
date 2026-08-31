# Arthratan Mythology DNS cutover

## Status: DNS cutover successful

External GitHub Actions verification on 2026-08-31 at approximately 17:25 UTC confirms:

- `arthratanmythology.com` now resolves to all four GitHub Pages IPv4 addresses:
  - `185.199.108.153`
  - `185.199.109.153`
  - `185.199.110.153`
  - `185.199.111.153`
- Plain HTTP is served by `Server: GitHub.com`.
- The live artwork path `/assets/art/chibi-rhayhara.webp` returns HTTP 200 with `Content-Type: image/webp` from GitHub Pages.
- No conflicting AAAA record was returned.

## Remaining state

HTTPS certificate provisioning for `arthratanmythology.com` is not complete yet. External TLS verification currently reports that the certificate presented by GitHub Pages does not yet contain `arthratanmythology.com` as a valid subject name.

This is now a GitHub Pages certificate-provisioning step rather than a DNS-routing or artwork-deployment problem.

## DNS authority

The authoritative nameservers remain `ns1.vercel-dns.com` and `ns2.vercel-dns.com`, but the apex A records now override Vercel's default ALIAS and route the website to GitHub Pages. Vercel is therefore acting only as the DNS provider, not the website host.

## GitHub side

- GitHub Pages is enabled from `main` / repository root.
- `CNAME` contains `arthratanmythology.com`.
- The visual build is published with separate artwork files and chibi assets.
- `.github/workflows/dns-diagnostics.yml` provides repeatable external verification.
