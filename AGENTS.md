# Repository Guidelines

## Project Structure & Module Organization
リポジトリの中心は `kale/` ディレクトリで、キュー選択アルゴリズムやタスク基底クラスなどのコアロジックがまとまっています。`kale/tests/` にはユニットテストとテスト用設定が揃っており、SQS モック構成は `test_queue_config.yaml` に定義されています。Sphinx ドキュメントは `docs/`、ElasticMQ を使った動作例は `example/`、CI 設定は `.github/workflows/ci.yml` に格納されています。設定バージョン情報は `kale/version.py` を参照してください。

## Build, Test, and Development Commands
- `uv sync --group dev --extra test` — 開発・テスト依存関係を一括で解決します。
- `KALE_SETTINGS_MODULE=kale.tests.test_settings uv run python -m unittest discover -s kale/tests -p "test_*.py" -v` — CI と同じテストスイートを実行します。
- `uv run make -C docs html` — ドキュメントを `docs/_build/html` に生成します。Windows は `uv run sphinx-build docs docs/_build/html` を利用してください。
- `uv run python -m build` — 配布用のホイールと sdist を `dist/` 配下に作成します。

## Coding Style & Naming Conventions
Python 3.9 以降を前提に PEP 8 相当のスタイルと 4 スペースインデントを守ってください。公開 API には可能な限り型ヒントと docstring を付与し、タスククラスは `*Task`、キューセレクタは `*Selector` の語尾で統一するのが既存コードに揃える最短経路です。設定モジュールは `kale.default_settings` を継承する形で分離し、環境変数参照は `os.getenv` を介して安全に扱ってください。自動整形ツールは固定されていないため、変更前後の `git diff` を確認しながら局所的に整える方針です。

## Testing Guidelines
テストは標準の `unittest` ランナーで駆動し、`KALE_SETTINGS_MODULE=kale.tests.test_settings` を指定してモック設定を読み込みます。新規テストは `kale/tests/test_*.py` に配置し、テストクラスは `Test*`、メソッドは `test_*` の命名で揃えてください。キュー関連シナリオでは `test_queue_config.yaml` を更新し、ElasticMQ 依存の検証は `example/run_elasticmq.sh` を併用して再現性を確保します。SQS 例外の再試行パスやワーカーのシャットダウン経路も網羅することを推奨します。

## Commit & Pull Request Guidelines
Git 履歴では `fix: 🐛 …` や `chore: …` のように小文字の種別プレフィックスと任意の絵文字を組み合わせた一行要約が一般的です。本文には動機と影響範囲を箇条書きで簡潔に記載し、Breaking change があれば明示してください。PR ではテスト結果（例: `uv run python -m unittest …` の成功ログ）、関連 Issue 番号、UI 変更があればスクリーンショットや CLI 出力を添付します。レビューアが再現に迷わないよう使用した環境変数や外部サービスの状態も説明欄に列挙してください。

## Security & Configuration Tips
AWS 認証情報は OS シークレットや `.env` 管理ツールに保存し、リポジトリへ平文でのコミットを避けてください。ローカル検証は `example/run_elasticmq.sh` で ElasticMQ を起動し、`KALE_SETTINGS_MODULE` で対象設定を切り替えます。デフォルト設定ファイルを直接変更せず、新しい設定モジュールを作成して環境変数で指定する運用が安全です。公開前に `dist/` を確認し、不要な秘匿ファイルが含まれていないか必ず見直してください。
