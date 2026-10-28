"""YouTube（ショート含む）の題名・説明文・タグを書き換える。

  python3 scripts/yt_description.py --video <動画ID> --file drafts/yt-<動画ID>.md        # 差分を見るだけ
  python3 scripts/yt_description.py --video <動画ID> --file drafts/yt-<動画ID>.md --go   # 書き換える

drafts の md（templates/yt-description.md）：
  ## 題名 / ## 説明文 / ## タグ（カンマ区切り）
公式の決まり：snippet を書き換えるときは categoryId も必ず送る（このキットは今の値をそのまま送る）。
送らなかった欄は消えるので、今の値を読んでから必要なところだけ差し替えます。1回50ユニット（1日1万ユニット）。
"""
from __future__ import annotations

import os as _ng_os, sys as _ng_sys  # N-Hack 専用の門（下の3行を消すとこのキットは動きません）
_ng_sys.path.insert(0, _ng_os.path.dirname(_ng_os.path.abspath(__file__)))
import nhack_gate as _nhack_gate  # noqa: E402,F401


import argparse
import json
import re
import sys

import yt
from _common import append_log, read_text_arg


def parse(md: str) -> dict:
    out = {}
    for key, name in (("title", "題名"), ("description", "説明文"), ("tags", "タグ")):
        m = re.search(rf"^## {name}\s*\n(.*?)(?=^## |\Z)", md, re.S | re.M)
        if m and m.group(1).strip():
            out[key] = m.group(1).strip()
    if "tags" in out:
        out["tags"] = [t.strip().lstrip("#") for t in re.split(r"[,、\n]", out["tags"]) if t.strip()]
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--video", required=True)
    p.add_argument("--file", required=True)
    p.add_argument("--go", action="store_true")
    a = p.parse_args()
    new = parse(read_text_arg(None, a.file))
    if len(new.get("title", "")) > 100:
        sys.exit("[止めました] 題名は100字まで")
    if len(new.get("description", "").encode("utf-8")) > 5000:
        sys.exit("[止めました] 説明文は5000バイトまで")

    r = yt.get("videos", {"part": "snippet", "id": a.video}, a.go)
    if not a.go:
        yt.put_json("videos", {"part": "snippet"}, {"id": a.video, "snippet": {"title": new.get("title", "<今の題名>"),
                    "description": new.get("description", "<今の説明文>"), "tags": new.get("tags", []),
                    "categoryId": "<今の categoryId>"}}, a.go)
        print("\n（dry-run でした）")
        return
    items = (r or {}).get("items", [])
    if not items:
        sys.exit("[止めました] 動画が見つかりません（自分のチャンネルの動画IDか確かめる）")
    sn = items[0]["snippet"]
    body = {"id": a.video, "snippet": {"title": new.get("title", sn["title"]),
                                       "description": new.get("description", sn.get("description", "")),
                                       "tags": new.get("tags", sn.get("tags", [])),
                                       "categoryId": sn["categoryId"],
                                       "defaultLanguage": sn.get("defaultLanguage")}}
    if not body["snippet"]["defaultLanguage"]:
        body["snippet"].pop("defaultLanguage")
    print("変える前:", json.dumps({k: sn.get(k) for k in ("title", "tags")}, ensure_ascii=False))
    yt.put_json("videos", {"part": "snippet"}, body, a.go)
    append_log("yt-updated.jsonl", {"video": a.video, "before_title": sn["title"], "after_title": body["snippet"]["title"]})
    print("書き換えました")


if __name__ == "__main__":
    main()
