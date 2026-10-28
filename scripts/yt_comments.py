"""YouTube のコメントを集めて下書きを作り、確かめたものだけ返信する。

  python3 scripts/yt_comments.py fetch --go       # 自分のチャンネルの新しいコメント → data/yt-reply-drafts.json
  python3 scripts/yt_comments.py send             # 返す予定を見るだけ
  python3 scripts/yt_comments.py send --go        # approve=true だけ返す（1回20件まで）

費用（1日1万ユニットの中で）：一覧 1ユニット／返信 1件50ユニット → 1日に返せるのは多くて約190件。
"""
from __future__ import annotations

import os as _ng_os, sys as _ng_sys  # N-Hack 専用の門（下の3行を消すとこのキットは動きません）
_ng_sys.path.insert(0, _ng_os.path.dirname(_ng_os.path.abspath(__file__)))
import nhack_gate as _nhack_gate  # noqa: E402,F401


import argparse
import json
import time

import yt
from _common import DATA, append_log, read_log

DRAFTS = DATA / "yt-reply-drafts.json"


def load():
    return json.loads(DRAFTS.read_text(encoding="utf-8")) if DRAFTS.exists() else []


def store(rows):
    DATA.mkdir(exist_ok=True)
    DRAFTS.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


def fetch(go: bool) -> None:
    ch = yt.get("channels", {"part": "id", "mine": "true"}, go)
    cid = ((ch or {}).get("items") or [{}])[0].get("id", "<チャンネルID>")
    r = yt.get("commentThreads", {"part": "snippet", "allThreadsRelatedToChannelId": cid,
                                   "maxResults": "50", "order": "time", "textFormat": "plainText"}, go)
    if not go:
        print("\n（dry-run でした）")
        return
    done = {x["comment_id"] for x in read_log("yt-replied.jsonl")}
    rows = load()
    known = {x["comment_id"] for x in rows}
    added = 0
    for t in (r or {}).get("items", []):
        top = t["snippet"]["topLevelComment"]
        if top["id"] in done or top["id"] in known:
            continue
        if t["snippet"].get("totalReplyCount", 0) and t["snippet"].get("canReply") is False:
            continue
        s = top["snippet"]
        if s.get("authorChannelId", {}).get("value") == cid:
            continue
        rows.append({"comment_id": top["id"], "video": t["snippet"].get("videoId"), "from": s.get("authorDisplayName"),
                     "text": s.get("textDisplay"), "at": s.get("publishedAt"), "reply": "", "approve": False})
        added += 1
    store(rows)
    print(f"新しいコメント {added} 件")


def send(go: bool) -> None:
    rows = load()
    todo = [x for x in rows if x.get("approve") and x.get("reply") and not x.get("sent")][:20]
    for x in todo:
        yt.post_json("comments", {"part": "snippet"}, {"snippet": {"parentId": x["comment_id"], "textOriginal": x["reply"]}}, go)
        if go:
            x["sent"] = True
            append_log("yt-replied.jsonl", {"comment_id": x["comment_id"], "at": time.strftime("%Y-%m-%d %H:%M")})
            time.sleep(2)
    if go:
        store(rows)
    print(f"返信 {len(todo)} 件" + ("" if go else "（dry-run）"))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=["fetch", "send"])
    p.add_argument("--go", action="store_true")
    a = p.parse_args()
    fetch(a.go) if a.action == "fetch" else send(a.go)
