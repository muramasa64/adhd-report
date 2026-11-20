# 仕様

## 1. 構成

```
adhd-report/
├── .claude-plugin/{plugin.json, marketplace.json}
├── hooks/{hooks.json, always-on.sh}
├── skills/adhd-report/SKILL.md
├── scripts/run_evals.py
├── evals/{cases.jsonl, rubric.md, README.md, runners.example.json}
├── tests/{test_run_evals.py, test_skill_rules.py}
├── .github/workflows/plugin-load-check.yml
├── docs/{use-cases.md, requirements.md, spec.md}
├── README.md, README_ja.md, LICENSE, .gitignore
```

元のリポジトリ: https://github.com/ayghri/i-have-adhd（MIT、Copyright (c) 2026 Ayoub Ghriss）。
コピー元の版は、`d94521d`（Merge pull request #66）。

## 2. 元から何を残し、足し、変えるか

### 残す

| 物 | 内容 |
|---|---|
| 決まり1〜10（5と9を除く） | 次の行動から始める、番号付き、次の一手で終える、脱線の抑制、時間の見積り、成果の可視化、エラーは淡々と、前置きなし |
| 「決まりを破る場合」「送る前の確認」 | 構造はそのまま。確認項目を1つ足す |
| フックの仕組み | SessionStart で、印のファイルがある時だけ本文を注入。POSIX sh。失敗しても exit 0 |
| eval と test の仕組み | `run_evals.py`（validate / plan / run / score）、`test_run_evals.py`、rubric |

### 足す

| 物 | 内容 |
|---|---|
| 決まり11〜17 | FR-B1〜B7。判断1件ずつ、単独で読める依頼、流れで書く、はい／いいえ、言語、運用情報を混ぜない、あなたの操作 |
| 節「Multi-agent sessions」 | FR-C1〜C6。括弧書き1行、一段落での決定待ち、状況の順、長い報告の分解、台帳の1行、起動直後の確認 |
| `tests/test_skill_rules.py` と新しい eval ケース | 本文の決まり、manifest の名前、フックの動作のテスト。足した決まりに対応する eval ケース |

### 変える

| 物 | 変更 |
|---|---|
| 決まり5（毎ターン状態を言い直す） | 通知が起点で、報告済みと同じ内容の時は、括弧書き1行で足りるとする（4節） |
| 決まり9（リストは5件まで） | 「判断の依頼は1件。一覧は5件まで」と書く |
| 名前 | 5節 |

### 削除する

Codex・Gemini・Cursor 向けの設定（`.codex-plugin`、`.agents`、`.cursor`、`gemini-extension.json`、`GEMINI.md`、`skills/*/agents/`）、`INSTALL.md`、ロゴ、`README.zh-CN.md`、`claude.yml`、`cursor-skill-sync.yml`、Antigravity 用の `plugin.json`。
README は、英語と日本語の2つにする（NFR6）。

## 3. SKILL.md の構成

```
frontmatter（name: adhd-report、disable-model-invocation: true、license: MIT）
# adhd-report
## Persistence          止める言葉は "stop adhd-report"
## What ADHD changes about reading    事実1〜5（元）＋事実6〜9（足す）
## Rules
  1〜10   元（5・9は直す）
  11 One decision at a time
  12 Make each decision ask stand alone
  13 Say it as who does what to where
  14 Answer "is my understanding right?" yes or no first
  15 Write in the reader's language
  16 Keep operations noise out of the report
  17 Open with "Your action:" when the reader must act
## Multi-agent sessions     C1〜C6
## When to break the rules  元の6項目
## Pre-send check          元の5項目＋「この1通だけで答えられるか」
```

事実6〜9（足す）:

6. 名詞が連なる圧縮文は、1回では読み取れない
7. 複数の判断を一度に渡されると、1件ずつに分けて聞き返す
8. 話題が切り替わると、直前の文脈が外れる。前の返事に戻る手間が大きい
9. 本題と関係ない状態の情報は、そこで引っかかる

### 判断の依頼の形（決まり12）

```
【project / topic】 <何を決めるか。1文>
今決める理由: <決めないと何が止まるか。1〜2行>
- A. <案の名前>: <選ぶと誰が何をするか>
- B. ...
おすすめ: A。<理由1つ>
```

「案1」「A」だけで案を書かない。AskUserQuestion では、質問の文にタスクと「何を決めるか」を、選択肢の文に「選ぶと誰が何をするか」を入れる。

## 4. ぶつかりの解決: 毎ターンの言い直しと、括弧書き1行

元の決まり5は、毎ターン状態を言い直す。FR-C1 は、報告済みと同じ通知への返事を短くする。次の順で両立させる。

1. 返事の起点が、読み手の発言なら、決まり5をそのまま守る
2. 起点が通知で、内容が報告済みと同じなら、返事は括弧書きの1行にする。これが、その時点の「状態の言い直し」である。書く物は、いま読み手を待っている物
   - 例: `（認証の移行の判断の返事を待っています）`
   - 何も待っていなければ: `（返事を待っている事はありません）`
3. 起点が通知で、内容が新しい（新しい完了、blocked、エラー）なら、普通に報告する。決まり5を守る
4. 完全な無出力にはしない。ハーネスが出力を求めるため
5. 括弧書きの1行は、台帳（ある場合）を更新した後に書く。台帳が無いセッションでは、記録の更新を省く

「報告済みと同じ」の例: 完了通知の重複、監視（Monitor）の期限切れ、起動時の既存の完了行、エージェントを片付けた時の通知。

## 5. 名前の変更

| 物 | 元 | 新 |
|---|---|---|
| plugin 名（plugin.json、marketplace.json の plugins） | `i-have-adhd` | `adhd-report` |
| marketplace 名 | `i-have-adhd` | `adhd-report` |
| スキル名・ディレクトリ | `skills/i-have-adhd` | `skills/adhd-report` |
| スラッシュコマンド | `/i-have-adhd` | `/adhd-report` |
| 常時有効の印のファイル | `~/.claude/.i-have-adhd-always` | `~/.claude/.adhd-report-always` |
| 止める言葉 | `stop adhd mode` / `normal mode` | `stop adhd-report` |
| フックの注入の先頭 | `ADHD MODE ACTIVE (always-on).` | `ADHD-REPORT ACTIVE (always-on).` |
| フックの statusMessage | `Checking i-have-adhd always-on flag...` | `Checking adhd-report always-on flag...` |
| 設定のキー（settings.json の enabledPlugins） | `i-have-adhd@i-have-adhd` | `adhd-report@adhd-report` |

`always-on.sh` は、新しい印だけを見る。元の印があっても、何も注入しない。

author は、plugin.json に、元の作者（Ayoub G.）と自分の両方を書く。版は `0.1.0` から始める。

## 6. フックの仕様

- 入力: 環境変数 `CLAUDE_CONFIG_DIR`（無ければ `~/.claude`）
- 印のファイル `$CLAUDE_CONFIG_DIR/.adhd-report-always` が無い: 何も出さず exit 0
- 有る: SKILL.md の frontmatter を除いた本文を、1行の案内に続けて標準出力に出す
- SKILL.md が無い、awk が失敗: 何も出さず exit 0

## 7. テストと eval

### test_skill_rules.py（unittest、標準ライブラリのみ）

| 区分 | 確かめること |
|---|---|
| 名前 | frontmatter の name とディレクトリ名が `adhd-report`。plugin.json、marketplace.json、hooks.json の名前。`i-have-adhd` が残っていない（許可する場所を除く） |
| フック | `CLAUDE_CONFIG_DIR` を一時ディレクトリにして実行する。印なしは空、新しい印で本文と案内が出る、元の印だけでは空 |
| 決まり11〜17 | 各見出しがある。各決まりの要点の語がある（1件ずつ／「N件あります」、5つの要素、誰が・何を・どこへ、はい／いいえ、言語、運用情報、「あなたの操作:」） |
| 節 Multi-agent sessions | C1〜C6 の要点。括弧書き1行、一段落、決定待ち→作業中→完了、40字と30字 |
| ぶつかり | 決まり5に、通知が起点の時の例外と、括弧書き1行がある。決まり9に、判断は1件がある |
| 長さ | 本文が元の約2倍以内（NFR5） |
| eval | 足した決まりに対応するケースが `cases.jsonl` にあり、`validate` が通る |

### eval ケース（足す）

`decision-one-at-a-time`、`decision-standalone`、`confirm-yes-no`、`duplicate-notification`、`user-action-needed`、`status-overview-order`、`abstract-sentence-rephrase`、`pending-decisions-pause`。プロンプトは日本語。

### 流し方

```bash
python3 -m unittest discover -s tests          # テスト（外部通信なし）
python3 scripts/run_evals.py validate           # ケースの形式の確認
python3 scripts/run_evals.py plan --trials 3    # 実行計画の表示（実行はしない）
# 以下は claude を呼ぶ（有料）。本リポジトリでは流さない
python3 scripts/run_evals.py run --runner claude --condition baseline --trials 3 --budget-usd 12.5 --output evals/results/responses.jsonl
python3 scripts/run_evals.py run --runner claude --condition candidate --condition-skill skills/adhd-report/SKILL.md --trials 3 --budget-usd 12.5 --output evals/results/responses.jsonl
python3 scripts/run_evals.py score evals/results/scores.jsonl
```

## 8. 入れ替えの手順（利用者の判断の後。このリポジトリの作業の範囲外）

1. 元の plugin を外す: `claude plugin uninstall i-have-adhd` と `claude plugin marketplace remove i-have-adhd`
2. リポジトリを GitHub に作って push する、またはローカルの marketplace として追加する: `claude plugin marketplace add <path または user/repo>`
3. `claude plugin install adhd-report@adhd-report`
4. nix の設定を変える（`~/.config/nix-configuration`）
   - `modules/home-manager/programs/claude.nix` の `.claude/.i-have-adhd-always` を `.claude/.adhd-report-always` に変える
   - `config/claude/settings.json` の `enabledPlugins` と `extraKnownMarketplaces` を `adhd-report` に変える
5. 元の印 `~/.claude/.i-have-adhd-always` を消す。両方が残ると、2つのルールが同時に注入され、決まり5が食い違う
6. chief-of-staff の CLAUDE.md に、同じ内容の決まりを書いていたら、スキルと二重にならないよう消す

## 9. 未決・注意

- 括弧書き1行の「何も待っていない時」の文言は `（返事を待っている事はありません）` に決定済み（利用者の判断）
- 通知への返事を括弧書き1行にすると、ツール呼び出しの後に1行を出して終われるかは、実機で試して確かめる必要がある
- 起動直後の確認（C6）は、画面を読む手段（hc など）に依存する。スキルは手段を指定しない
- タブ名の【操作待ち】の表示は、スキルの外
