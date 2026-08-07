#!/usr/bin/env python3
"""
Generate a projects.svg card showing the user's GitHub repositories.
Fetches live repo data from the GitHub API, excludes forks and the
profile repo, and renders a clean themed SVG.
"""

import json
import os
import sys
import urllib.request

GITHUB_USER = os.environ.get("GITHUB_USER", "vigneshsindhe")
EXCLUDE_FORKS = os.environ.get("EXCLUDE_FORKS", "true").lower() == "true"
MAX_REPOS = int(os.environ.get("MAX_REPOS", "8"))
OUTPUT_PATH = os.environ.get("OUTPUT_PATH", "output/projects.svg")

TOKEN = os.environ.get("GITHUB_TOKEN", "")

# Theme colors
DARK_BG0 = "#0A101F"
DARK_BG1 = "#0C1426"
DARK_BORDER = "#1E293B"
DARK_TITLE = "#22D3EE"
DARK_DESC = "#94A3B8"
DARK_LANG = "#7C3AED"
DARK_STAR = "#F8FAFC"
DARK_CARD = "#111A2E"


def fetch_json(url, use_token=True):
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "projects-svg-generator")
    req.add_header("Accept", "application/vnd.github+json")
    if use_token and TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def list_repos():
    url = (
        f"https://api.github.com/users/{GITHUB_USER}/repos"
        "?per_page=100&sort=updated"
    )
    try:
        repos = fetch_json(url, use_token=True)
    except Exception:
        # GITHUB_TOKEN may be restricted/invalid; public data works without auth
        repos = fetch_json(url, use_token=False)
    filtered = [
        r
        for r in repos
        if r["name"] != GITHUB_USER and not (EXCLUDE_FORKS and r["fork"])
    ]
    filtered.sort(key=lambda r: r["stargazers_count"], reverse=True)
    return filtered[:MAX_REPOS]


def esc(text):
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def truncate(text, maxlen):
    text = text or ""
    return text if len(text) <= maxlen else text[: maxlen - 1] + "…"


def render_card(repo, x, y, w):
    name = esc(repo["name"])
    desc = esc(truncate(repo["description"] or "No description provided.", 42))
    lang = esc(repo.get("language") or "—")
    stars = repo["stargazers_count"]
    url = esc(repo["html_url"])

    return (
        f'<a href="{url}">'
        f'<rect x="{x}" y="{y}" width="{w}" height="96" rx="12" fill="{DARK_CARD}" '
        f'stroke="{DARK_BORDER}" stroke-width="1"/>'
        f'<text x="{x + 18}" y="{y + 32}" font-family="Segoe UI, Ubuntu, sans-serif" '
        f'font-size="18" font-weight="600" fill="{DARK_TITLE}">{name}</text>'
        f'<text x="{x + 18}" y="{y + 56}" font-family="Segoe UI, Ubuntu, sans-serif" '
        f'font-size="13" fill="{DARK_DESC}">{desc}</text>'
        f'<text x="{x + 18}" y="{y + 82}" font-family="Segoe UI, Ubuntu, sans-serif" '
        f'font-size="12" fill="{DARK_LANG}">● {lang}</text>'
        f'<text x="{x + w - 18}" y="{y + 82}" text-anchor="end" '
        f'font-family="Segoe UI, Ubuntu, sans-serif" font-size="12" fill="{DARK_STAR}">'
        f'★ {stars}</text>'
        f"</a>"
    )


def build_svg(repos):
    cols = 2
    card_w = 570
    gap = 20
    rows = (len(repos) + cols - 1) // cols
    width = cols * card_w + (cols - 1) * gap + 40
    height = 120 + rows * 96 + (rows - 1) * gap + 40

    header = (
        f'<text x="20" y="52" font-family="Segoe UI, Ubuntu, sans-serif" '
        f'font-size="26" font-weight="700" fill="{DARK_TITLE}">📦 My Projects</text>'
        f'<text x="22" y="80" font-family="Segoe UI, Ubuntu, sans-serif" '
        f'font-size="13" fill="{DARK_DESC}">{len(repos)} public repositories · '
        f'@{GITHUB_USER}</text>'
    )

    cards = []
    for i, repo in enumerate(repos):
        r, c = divmod(i, cols)
        x = 20 + c * (card_w + gap)
        y = 110 + r * (96 + gap)
        cards.append(render_card(repo, x, y, card_w))

    gradient = (
        f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{DARK_BG0}"/>'
        f'<stop offset="1" stop-color="{DARK_BG1}"/>'
        f"</linearGradient>"
    )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height}" viewBox="0 0 {width} {height}">'
        f"<defs>{gradient}</defs>"
        f'<rect width="{width}" height="{height}" fill="url(#bg)" rx="16"/>'
        + header
        + "".join(cards)
        + "</svg>"
    )


def main():
    try:
        repos = list_repos()
        if not repos:
            print("No repositories found, keeping existing SVG.", file=sys.stderr)
            sys.exit(1)
        svg = build_svg(repos)
        os.makedirs(os.path.dirname(OUTPUT_PATH) or ".", exist_ok=True)
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"Generated {OUTPUT_PATH} with {len(repos)} repositories.")
    except Exception as e:
        import traceback

        traceback.print_exc()
        print(f"Error generating projects SVG: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
