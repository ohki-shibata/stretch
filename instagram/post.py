#!/usr/bin/env python3
"""inbox の写真を Instagram Graph API で投稿する。

使い方:
    python3 instagram/post.py instagram/inbox/photo.jpg "今日のランチ。"
    python3 instagram/post.py instagram/inbox/photo.jpg "今日のランチ。" --dry-run

必要な環境変数:
    IG_USER_ID       Instagram のプロアカウントのユーザーID
    IG_ACCESS_TOKEN  長期アクセストークン
任意:
    IG_REPO          画像を置いているリポジトリ（既定: ohki-shibata/stretch）
    IG_BRANCH        画像を置いているブランチ（既定: 現在の git ブランチ）

画像は push 済みであること。公開リポジトリの raw URL を Instagram に渡して取得させる。
Instagram が受け付ける画像は JPEG のみ。
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://graph.facebook.com/v21.0"


def current_branch():
    return subprocess.check_output(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True
    ).strip()


def repo_relative(path):
    root = subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"], text=True
    ).strip()
    return os.path.relpath(os.path.abspath(path), root)


def raw_url(path):
    repo = os.environ.get("IG_REPO", "ohki-shibata/stretch")
    branch = os.environ.get("IG_BRANCH") or current_branch()
    return "https://raw.githubusercontent.com/{}/{}/{}".format(
        repo, urllib.parse.quote(branch), urllib.parse.quote(repo_relative(path))
    )


def call(method, endpoint, params):
    data = urllib.parse.urlencode(params).encode()
    url = API + endpoint
    if method == "GET":
        url += "?" + data.decode()
        data = None
    req = urllib.request.Request(url, data=data, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as res:
            return json.load(res)
    except urllib.error.HTTPError as e:
        sys.exit("API エラー {}: {}".format(e.code, e.read().decode()))


def post(image_url, caption, user_id, token):
    container = call(
        "POST",
        "/{}/media".format(user_id),
        {"image_url": image_url, "caption": caption, "access_token": token},
    )["id"]

    # Instagram 側の画像取得が終わるまで待つ
    for _ in range(30):
        status = call(
            "GET",
            "/{}".format(container),
            {"fields": "status_code", "access_token": token},
        )["status_code"]
        if status == "FINISHED":
            break
        if status in ("ERROR", "EXPIRED"):
            sys.exit("メディアの準備に失敗しました: {}".format(status))
        time.sleep(2)
    else:
        sys.exit("メディアの準備がタイムアウトしました")

    return call(
        "POST",
        "/{}/media_publish".format(user_id),
        {"creation_id": container, "access_token": token},
    )["id"]


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("image")
    parser.add_argument("caption")
    parser.add_argument("--dry-run", action="store_true", help="投稿せず URL だけ表示する")
    args = parser.parse_args()

    if not args.image.lower().endswith((".jpg", ".jpeg")):
        sys.exit("JPEG 以外は投稿できません: {}".format(args.image))

    url = raw_url(args.image)
    if args.dry_run:
        print(url)
        print(args.caption)
        return

    user_id = os.environ.get("IG_USER_ID")
    token = os.environ.get("IG_ACCESS_TOKEN")
    if not user_id or not token:
        sys.exit("IG_USER_ID と IG_ACCESS_TOKEN を設定してください")

    media_id = post(url, args.caption, user_id, token)
    print("投稿しました: {}".format(media_id))


if __name__ == "__main__":
    main()
