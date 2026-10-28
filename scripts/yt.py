"""YouTube Data API v3 / Analytics API の入口。"""
from __future__ import annotations

import os as _ng_os, sys as _ng_sys  # N-Hack 専用の門（下の3行を消すとこのキットは動きません）
_ng_sys.path.insert(0, _ng_os.path.dirname(_ng_os.path.abspath(__file__)))
import nhack_gate as _nhack_gate  # noqa: E402,F401


import os

from _common import call
from yt_auth import access_token

DATA_API = os.environ.get("YT_API_BASE", "https://www.googleapis.com/youtube/v3")
ANALYTICS = os.environ.get("YT_ANALYTICS_BASE", "https://youtubeanalytics.googleapis.com/v2")


def _h(go: bool) -> dict:
    return {"Authorization": f"Bearer {access_token(go)}"}


def get(path: str, params: dict, go: bool, base: str = DATA_API):
    return call("GET", f"{base}/{path}", params, headers=_h(go), go=go)


def put_json(path: str, params: dict, body: dict, go: bool):
    return call("PUT", f"{DATA_API}/{path}", params, body=body, headers=_h(go), go=go, json_body=True)


def post_json(path: str, params: dict, body: dict, go: bool):
    return call("POST", f"{DATA_API}/{path}", params, body=body, headers=_h(go), go=go, json_body=True)
