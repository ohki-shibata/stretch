# Instagram 半自動投稿

`inbox/` に写真（JPEG）を入れておくと、定期実行で Claude が一言キャプションを付けて 1 枚ずつ投稿し、投稿済みの写真を `posted/` に移す。

## 写真の追加

GitHub アプリかブラウザで、ブランチ `claude/instagram-auto-post-ekb1ud` の `instagram/inbox/` に JPEG をアップロードする。
キャプションを自分で決めたいときは、同じ名前の `.txt`（例: `lunch.jpg` なら `lunch.txt`）に書いておく。

リポジトリは公開なので、`inbox/` に入れた写真は投稿前から誰でも見られる。

## 初回だけやること

1. Instagram をプロアカウント（クリエイター）に切り替え、Facebook ページと連携する
2. Meta for Developers でアプリを作り、`instagram_basic` と `instagram_content_publish` の権限で長期アクセストークンを取る
3. Instagram のユーザーID を調べる（Graph API エクスプローラーで `me/accounts?fields=instagram_business_account` を叩く）
4. クラウド環境の設定で次を登録する
   - 環境変数 `IG_USER_ID` と `IG_ACCESS_TOKEN`
   - ネットワークの許可ドメインに `graph.facebook.com`

長期アクセストークンは約 60 日で期限が切れるので、切れたら取り直して環境変数を更新する。

## 手動で投稿する

```sh
python3 instagram/post.py instagram/inbox/lunch.jpg "今日のランチ。" --dry-run  # URL だけ確認
python3 instagram/post.py instagram/inbox/lunch.jpg "今日のランチ。"
```
