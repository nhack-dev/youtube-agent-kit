"""YouTube（Google）のログイン。最初に1回だけ。

  python3 scripts/yt_auth.py login        # ブラウザで許可 → data/yt_token.json に保存（人に渡さない）
  python3 scripts/yt_auth.py refresh --go # 使う前の更新（ほかの道具は自動でこれを呼ぶ）

必要なもの（README の「キーの取り方」）：
  .env の YT_CLIENT_ID / YT_CLIENT_SECRET（Google Cloud の「デスクトップ アプリ」の OAuth クライアント）
"""
from __future__ import annotations

import os as _ng_os, sys as _ng_sys  # N-Hack 専用の門（下の3行を消すとこのキットは動きません）
_ng_sys.path.insert(0, _ng_os.path.dirname(_ng_os.path.abspath(__file__)))
import nhack_gate as _nhack_gate  # noqa: E402,F401


import argparse
import http.server
import json
import os
import sys
import time
import urllib.parse
import webbrowser

from _common import DATA, call, env, load_env

load_env()
TOKEN = DATA / "yt_token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl",
          "https://www.googleapis.com/auth/youtube.readonly",
          "https://www.googleapis.com/auth/yt-analytics.readonly"]
PORT = 8765
TOKEN_URL = os.environ.get("YT_TOKEN_URL", "https://oauth2.googleapis.com/token")


def access_token(go: bool) -> str:
    """有効なアクセストークンを返す（切れていれば更新）。dry-run なら仮の値。"""
    if not go:
        return "<YT_ACCESS_TOKEN>"
    if not TOKEN.exists():
        sys.exit("[止めました] まだログインしていません：python3 scripts/yt_auth.py login")
    t = json.loads(TOKEN.read_text())
    if t.get("expires_at", 0) - 60 > time.time():
        return t["access_token"]
    r = call("POST", TOKEN_URL,
             body={"client_id": env("YT_CLIENT_ID", go), "client_secret": env("YT_CLIENT_SECRET", go),
                   "refresh_token": t["refresh_token"], "grant_type": "refresh_token"}, go=go)
    t.update({"access_token": r["access_token"], "expires_at": time.time() + int(r.get("expires_in", 3600))})
    TOKEN.write_text(json.dumps(t))
    TOKEN.chmod(0o600)
    return t["access_token"]


def login() -> None:
    cid, secret = env("YT_CLIENT_ID", True), env("YT_CLIENT_SECRET", True)
    redirect = f"http://127.0.0.1:{PORT}/"
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
        "client_id": cid, "redirect_uri": redirect, "response_type": "code", "scope": " ".join(SCOPES),
        "access_type": "offline", "prompt": "consent"})
    got = {}

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            got["code"] = (q.get("code") or [None])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("ログインできました。この画面は閉じてください。".encode())

        def log_message(self, *a):
            pass

    print("ブラウザで開きます（開かなければ下のURLを開く）：\n" + url)
    webbrowser.open(url)
    http.server.HTTPServer(("127.0.0.1", PORT), H).handle_request()
    if not got.get("code"):
        sys.exit("[止めました] 許可のコードが返ってきませんでした。")
    r = call("POST", TOKEN_URL,
             body={"client_id": cid, "client_secret": secret, "code": got["code"],
                   "grant_type": "authorization_code", "redirect_uri": redirect}, go=True)
    DATA.mkdir(exist_ok=True)
    TOKEN.write_text(json.dumps({"access_token": r["access_token"], "refresh_token": r.get("refresh_token"),
                                 "expires_at": time.time() + int(r.get("expires_in", 3600))}))
    TOKEN.chmod(0o600)
    print("保存しました: data/yt_token.json（人に渡さない・git に入れない）")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=["login", "refresh"])
    p.add_argument("--go", action="store_true")
    a = p.parse_args()
    if a.action == "login":
        login()
    else:
        tok = access_token(a.go)
        print("更新しました" if a.go else f"（dry-run）{tok}")
