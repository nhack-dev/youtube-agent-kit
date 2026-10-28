# YouTube エージェントキット（ショート含む）

あなたの AI エージェント（Claude Code など）がこのフォルダを読むと、YouTube の**題名・説明文・タグの書き換え、コメントへの返信、数字のふり返り**を毎日続けられるようになるキットです。

**費用は、YouTube Data API と YouTube Analytics API は無料（1日1万ユニットまで）。** このキットはほかのサーバーに何も送りません。

---

## 最初の10分

1. このフォルダを自分のパソコンに置く（受け取ったリポジトリを clone する）
2. `python3 --version` で 3.11 以上か確かめる
3. `cp .env.example .env` → 下の「キーの取り方」でキーを入れる
4. コマンドは既定で「送る予定を表示するだけ」（dry-run）。**`--go` を付けたときだけ本当に動きます**
5. `python3 scripts/yt_auth.py login` → ブラウザで自分のチャンネルのアカウントを選んで許可（`data/yt_token.json` ができる）
6. まず見るだけ（何も変わらない）：
   ```
   python3 scripts/yt_description.py --video <動画ID> --file templates/yt-description.md
   python3 scripts/yt_analytics.py
   ```
7. `--go` を付けると本当に動く（例：`python3 scripts/yt_analytics.py --go`）
8. AI エージェントに「AGENT.md を読んで、今日の分をやって」

---

## キーの取り方

1. https://console.cloud.google.com/ でプロジェクトを作り、「YouTube Data API v3」と「YouTube Analytics API」を有効にする
2. 「OAuth 同意画面」を作る（種類：外部・自分をテストユーザーに足す）
3. 「認証情報」→「OAuth クライアント ID」→ 種類「デスクトップ アプリ」→ ID とシークレットを `.env` の `YT_CLIENT_ID` `YT_CLIENT_SECRET` へ
4. 注意：同意画面が「テスト中」のままだと、**ログインは7日で切れます**。週1で `yt_auth.py login` をやり直すか、同意画面を「本番」にする（Google の確認が要る場合あり）

使う権限：youtube.force-ssl（説明文・返信）／youtube.readonly・yt-analytics.readonly（数字）

---

## できること・できないこと（公式ドキュメントで確かめた範囲）

| やりたいこと | できるか | 道具 |
|---|---|---|
| 題名・説明文・タグの書き換え | できる（1回50ユニット） | `yt_description.py` |
| コメントの取得・返信 | できる（一覧1ユニット・返信1件50ユニット） | `yt_comments.py` |
| 動画ごとの数字（再生・視聴時間・平均視聴・高評価・登録者増） | できる（1〜2日遅れ） | `yt_analytics.py` |
| 動画の新規アップロード | このキットではやらない（YouTube Studio かアプリで） | ― |

- 1日1万ユニット。太平洋時間の0時（日本の16時か17時）に戻る
- 題名は100字・説明文は5000バイトまで
- snippet を書き換えるときは categoryId も必ず送る決まり。送らなかった欄は消えるので、道具が今の値を読んでから必要なところだけ差し替えます

## 道具

| 道具 | すること |
|---|---|
| `yt_auth.py` | ログイン（最初の1回）・更新（ほかの道具が自動で呼ぶ） |
| `yt_description.py` | 題名・説明文・タグの書き換え |
| `yt_comments.py` | コメント集め → 下書き → 確かめたものだけ返信（1回20件まで） |
| `yt_analytics.py` | 動画ごとの数字 → `data/yt-<日付>.csv` |

## 毎日の動かし方（cron の例）

```
0 7 * * * cd /path/to/youtube-agent-kit && python3 scripts/yt_analytics.py --go >> data/cron.log 2>&1
```
`/path/to/` は自分の置き場所に替えてください。

## 中身

```
README.md / AGENT.md / CLAUDE.md
playbooks/   01 手順 ／ 02 ふり返り
templates/   下書き・アカウントの軸・ふり返りの型
scripts/     道具（Python 3.11 の標準ライブラリだけ）
drafts/      下書きの置き場
data/        記録の置き場（git に入れない）
```

## 困ったとき

| 出たもの | 意味 | やること |
|---|---|---|
| `quotaExceeded` | 1日のユニットを使い切った | 日本の16時か17時に戻る。返信の件数を減らす |
| `invalid_grant` | ログイン切れ（テスト中の7日など） | `yt_auth.py login` をやり直す |
| 403 `forbidden` | 自分のチャンネルの動画でない・権限が足りない | 動画IDとログインしたアカウントを確かめる |

## ライセンス

LICENSE を見てください（再配布はできません）。


---

## このキットは N-Hack のAIエージェント専用です

このキットは N-Hack の受講生さん専用のプレゼントです。**N-Hack のAIエージェント
（N-Hack のプラグインを入れた Claude Code など）が、このパソコンで動いていること**を
前提にしています。

- どのスクリプトも、最初に `scripts/nhack_gate.py`（門）を通ります。門は、このパソコンに
  N-Hack のAIエージェントの「印」があるかを**読むだけ**で確かめます（ネットにつなぎません・
  何も書き換えません・プラグインには一切触れません）。
- 印が足りない環境では、スクリプトは動かずに止まります（終了コード 2）。この環境でだけ
  動くのが正しい姿です。
- いま N-Hack 環境かどうかは、次のコマンドで確かめられます。

```bash
python3 scripts/nhack_gate.py
```

N-Hack 以外のパソコンにコピーしても動きません。受講生ページ・コンサルチャンネルの案内に
沿ってご利用ください。


---

## 困ったとき・もっと伸ばしたいとき

分からない・動かない・時間がかかっている——そんなときは、ひとりで抱えないでください。
**N-Hack の受講生ページ／個別コンサルチャンネル**から、担当にそのまま相談できます。
あなた専用のAIと伴走しながら、最短で結果まで一緒に持っていきます。

このキットのAIは、あなたが詰まったときや区切りのときに、自分から相談先を案内します。
