#!/usr/bin/env python3

from __future__ import annotations

import os
from pathlib import Path
from urllib import error, request
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "themes" / "sighnwaive" / "static" / "generated" / "github-grid.svg"
SVG_NS = "http://www.w3.org/2000/svg"


def color_for_score(score: int) -> str:
    if score <= 0:
        return "#111111"
    if score == 1:
        return "#4d2406"
    if score <= 3:
        return "#7a3708"
    if score <= 6:
        return "#a94a08"
    if score <= 10:
        return "#d65c0a"
    return "#ff6600"


def main() -> int:
    username = os.getenv("GITHUB_USERNAME", "sighnwaive").strip() or "sighnwaive"
    url = f"https://ghchart.rshah.org/ff6600/{username}"
    headers = {"user-agent": "sighnwaive-site-build/1.0"}

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    try:
        with request.urlopen(request.Request(url, headers=headers), timeout=30) as resp:
            svg_text = resp.read().decode("utf-8", errors="replace")
    except (error.URLError, error.HTTPError, TimeoutError):
        return 0

    try:
        root = ET.fromstring(svg_text)
    except ET.ParseError:
        return 0

    for rect in root.findall(f".//{{{SVG_NS}}}rect"):
        score = int(rect.attrib.get("data-score", "0") or "0")
        rect.set("rx", "2")
        rect.set("ry", "2")
        rect.set("style", f"fill:{color_for_score(score)};shape-rendering:crispedges;")

    for text in root.findall(f".//{{{SVG_NS}}}text"):
        text.set("fill", "#6f6f6f")
        style = text.attrib.get("style", "")
        parts = [p for p in style.split(";") if p and not p.strip().startswith(("fill:", "font-size:"))]
        parts.append("fill:#6f6f6f")
        parts.append("font-size:13px")
        text.set("style", ";".join(parts) + ";")

    width = int(root.attrib.get("width", "663"))
    height = int(root.attrib.get("height", "104"))
    root.set("width", str(int(width * 1.08)))
    root.set("height", str(int(height * 1.08)))

    root.set("style", "max-width:100%;height:auto;")
    OUT_PATH.write_text(ET.tostring(root, encoding="unicode"), encoding="utf-8")
    print(f"GitHub grid written to {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
