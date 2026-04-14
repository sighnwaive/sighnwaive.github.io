#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib import error, request


ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "data" / "htb.json"


def build_headers() -> dict[str, str]:
    headers = {
        "accept": "application/json, text/plain, */*",
        "user-agent": "sighnwaive-site-build/1.0",
        "referer": "https://app.hackthebox.com/",
    }

    token = os.getenv("HTB_API_TOKEN", "").strip()
    cookie = os.getenv("HTB_COOKIE", "").strip()
    xsrf = os.getenv("HTB_XSRF_TOKEN", "").strip()

    if token:
        headers["authorization"] = f"Bearer {token}"
    if cookie:
        headers["cookie"] = cookie
    if xsrf:
        headers["x-xsrf-token"] = xsrf

    return headers


def request_json(url: str, headers: dict[str, str]) -> dict | list | None:
    req = request.Request(url, headers=headers)
    try:
        with request.urlopen(req, timeout=30) as resp:
            content_type = resp.headers.get("content-type", "")
            body = resp.read().decode("utf-8", errors="replace")
            if "application/json" not in content_type:
                return None
            return json.loads(body)
    except (error.URLError, error.HTTPError, TimeoutError, json.JSONDecodeError):
        return None


def request_text(url: str, headers: dict[str, str]) -> str | None:
    req = request.Request(url, headers=headers)
    try:
        with request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except (error.URLError, error.HTTPError, TimeoutError):
        return None


def extract_profile(payload: dict | list) -> dict | None:
    if isinstance(payload, list):
        return None

    for key in ("profile", "data", "info"):
        candidate = payload.get(key)
        if isinstance(candidate, dict):
            if "profile" in candidate and isinstance(candidate["profile"], dict):
                return candidate["profile"]
            return candidate

    return payload


def pick(*values):
    for value in values:
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        return value
    return None


def normalize(profile: dict, source: str) -> dict:
    rank = pick(
        profile.get("rank"),
        profile.get("rank_text"),
        profile.get("ranking"),
    )

    points = pick(
        profile.get("points"),
        profile.get("user_points"),
        profile.get("respects"),
    )

    boxes = pick(
        profile.get("machines_owned"),
        profile.get("machine_owns"),
        profile.get("system_owns"),
    )

    if boxes is None:
        user_owns = profile.get("user_owns")
        system_owns = profile.get("system_owns")
        if isinstance(user_owns, int) and isinstance(system_owns, int):
            boxes = user_owns + system_owns

    return {
        "fetched": True,
        "source": source,
        "username": pick(profile.get("name"), profile.get("username"), os.getenv("HTB_USERNAME", "SighnWaive")),
        "rank": str(rank) if rank is not None else None,
        "points": str(points) if points is not None else None,
        "boxes": str(boxes) if boxes is not None else None,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def parse_public_profile(markdown: str, user_id: str) -> dict | None:
    rank_match = re.search(r"Hack The Box Rank\s+###\s+([^\n]+)", markdown, re.MULTILINE)
    global_rank_match = re.search(r"Global Ranking#(\d+)", markdown)
    points_matches = re.findall(r"\nPoints\s+(\d+)\s+", markdown)
    seasonal_rank_match = re.search(r"Seasonal Ranking#(\d+)", markdown)
    machines_match = re.search(r"\nMachines\s+(\d+)\s*/", markdown)
    overall_points = points_matches[0] if len(points_matches) > 0 else None
    seasonal_points = points_matches[1] if len(points_matches) > 1 else None

    if not any([rank_match, overall_points, seasonal_points, machines_match]):
        return None

    return {
        "fetched": True,
        "source": f"https://app.hackthebox.com/public/users/{user_id}",
        "username": os.getenv("HTB_USERNAME", "SighnWaive"),
        "rank": rank_match.group(1).strip() if rank_match else None,
        "points": overall_points,
        "boxes": machines_match.group(1) if machines_match else None,
        "overall": {
            "rank": rank_match.group(1).strip() if rank_match else None,
            "ranking": global_rank_match.group(1) if global_rank_match else None,
            "points": overall_points,
        },
        "season": {
            "ranking": seasonal_rank_match.group(1) if seasonal_rank_match else None,
            "points": seasonal_points,
            "boxes": machines_match.group(1) if machines_match else None,
        },
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def fallback_payload() -> dict:
    return {
        "fetched": False,
        "source": None,
        "username": os.getenv("HTB_USERNAME", "SighnWaive"),
        "rank": None,
        "points": None,
        "boxes": None,
        "overall": {"rank": None, "ranking": None, "points": None},
        "season": {"ranking": None, "points": None, "boxes": None},
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def main() -> int:
    headers = build_headers()
    user_id = os.getenv("HTB_USER_ID", "").strip()

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not user_id or ("authorization" not in headers and "cookie" not in headers):
        public_url = f"https://r.jina.ai/http://https://app.hackthebox.com/public/users/{user_id}" if user_id else None
        if public_url:
            text = request_text(public_url, {"user-agent": "sighnwaive-site-build/1.0"})
            if text:
                parsed = parse_public_profile(text, user_id)
                if parsed:
                    OUT_PATH.write_text(json.dumps(parsed, indent=2) + "\n", encoding="utf-8")
                    print("HTB fetch succeeded via public profile scrape")
                    return 0

        OUT_PATH.write_text(json.dumps(fallback_payload(), indent=2) + "\n", encoding="utf-8")
        print("HTB fetch skipped: missing HTB_USER_ID and public scrape failed")
        return 0

    urls = [
        f"https://app.hackthebox.com/api/v4/user/profile/basic/{user_id}",
        f"https://app.hackthebox.com/api/v4/user/profile/{user_id}",
        f"https://labs.hackthebox.com/api/v4/user/profile/basic/{user_id}",
        f"https://labs.hackthebox.com/api/v4/user/profile/{user_id}",
    ]

    for url in urls:
        payload = request_json(url, headers)
        if not isinstance(payload, dict):
            continue
        profile = extract_profile(payload)
        if not isinstance(profile, dict):
            continue
        normalized = normalize(profile, url)
        if normalized["rank"] or normalized["points"] or normalized["boxes"]:
            OUT_PATH.write_text(json.dumps(normalized, indent=2) + "\n", encoding="utf-8")
            print(f"HTB fetch succeeded via {url}")
            return 0

    OUT_PATH.write_text(json.dumps(fallback_payload(), indent=2) + "\n", encoding="utf-8")
    print("HTB fetch failed: no supported endpoint returned profile data", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
