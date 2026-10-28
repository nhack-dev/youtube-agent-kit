"""YouTube の数字（動画ごと）→ data/yt-<日付>.csv

  python3 scripts/yt_analytics.py --days 28 --go

使う数字：views（再生）estimatedMinutesWatched（見られた分数）averageViewDuration（平均視聴秒）
likes subscribersGained。数字は1〜2日遅れて入ります。
"""
from __future__ import annotations

import os as _ng_os, sys as _ng_sys  # N-Hack 専用の門（下の3行を消すとこのキットは動きません）
_ng_sys.path.insert(0, _ng_os.path.dirname(_ng_os.path.abspath(__file__)))
import nhack_gate as _nhack_gate  # noqa: E402,F401


import argparse
import csv
import datetime as dt

import yt
from _common import DATA, today

p = argparse.ArgumentParser()
p.add_argument("--days", type=int, default=28)
p.add_argument("--go", action="store_true")
a = p.parse_args()
end = dt.date.today()
start = end - dt.timedelta(days=a.days)
M = "views,estimatedMinutesWatched,averageViewDuration,likes,subscribersGained"
r = yt.get("reports", {"ids": "channel==MINE", "startDate": start.isoformat(), "endDate": end.isoformat(),
                       "metrics": M, "dimensions": "video", "sort": "-views", "maxResults": "50"}, a.go, base=yt.ANALYTICS)
if r:
    cols = [h["name"] for h in r.get("columnHeaders", [])]
    DATA.mkdir(exist_ok=True)
    path = DATA / f"yt-{today()}.csv"
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        w.writerows(r.get("rows", []))
    print(f"{len(r.get('rows', []))} 本 → data/{path.name}")
