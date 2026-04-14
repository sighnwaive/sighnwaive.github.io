# SighnWaive Site

## Local Dev

Run Hugo in Docker:

```bash
docker run --rm -p 1313:1313 -v "$PWD":/src -w /src klakegg/hugo:latest server -D --bind 0.0.0.0
```

## HTB Setup

The site fetches Hack The Box data at build time and writes it to `data/htb.json`.

It first scrapes the public profile page for user `1840809` via `r.jina.ai`, so auth is not required for the normal path.

Set these GitHub Actions secrets:

- `HTB_API_TOKEN`: bearer token if HTB exposes one for your session

Or use cookie-based auth instead:

- `HTB_USER_ID`: your numeric HTB user id
- `HTB_COOKIE`: full authenticated `Cookie` header from a logged-in HTB browser session
- `HTB_XSRF_TOKEN`: matching XSRF token value if HTB requires it

The workflow will try the public page scrape first, then authenticated `api/v4/user/profile` endpoints if secrets are present. If both fail, the site falls back to the static values in `hugo.toml`.

## Finding Your HTB User ID

While logged into HTB:

1. Open the browser devtools network tab.
2. Visit your HTB profile.
3. Look for a request containing `user/profile`.
4. Copy the numeric id used in the request URL.

If HTB changes their private API again, update `scripts/fetch_htb_stats.py` with the new endpoint.
