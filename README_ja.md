[English](README.md) | 日本語

# adhd-report

ADHD の読み手向けに、Claude Code の出力と報告の形を整えるスキルです。

土台は、Ayoub Ghriss 氏の [i-have-adhd](https://github.com/ayghri/i-have-adhd)（MIT）です。
元の10個の決まりは、そのまま残しています。
作者自身のセッションのログから、読み手が止まった場面を調べ、決まり11〜17と、複数エージェントのセッション向けの節を足しました。

## 足した内容

| 場所 | 決まり |
|---|---|
| 決まり5（変更） | 報告済みの通知が起点のターンは、読み手を待っている物を書いた、括弧書きの1行で返す。「毎ターン状態を言い直す」と「同じことを繰り返さない」のぶつかりを、これで解く |
| 決まり9（変更） | リストは5件まで。判断はもっと厳しく、1件ずつ |
| 決まり11 | 判断は1件ずつ。件数を言い、1件目を出し、答えを待つ |
| 決まり12 | 判断の依頼は、その1通だけで読める形にする。どのタスクか、何を決めるか、なぜ今か、各案で誰が何をするか、おすすめ。AskUserQuestion も同じ |
| 決まり13 | 名詞が連なる文を、「誰が・何を・どこへ」の流れにする。1文に1つの事だけ書く |
| 決まり14 | 「理解で合っていますか」には、はい／いいえを先に言い、根拠を1〜2点続ける |
| 決まり15 | 読み手の言語で書く。見出しの語も同じ（「Next:」ではなく「次:」） |
| 決まり16 | 関係のない運用の情報を、報告に混ぜない |
| 決まり17 | 読み手の操作が要る時は、1行目を「あなたの操作:」にし、番号付きの手順を続ける |
| 複数エージェントのセッション | 重複通知への括弧書き1行、一段落した時の決定待ちの知らせ、決定待ち→作業中→完了の順の状況、長い報告の分解、台帳の1行を短くする、起動直後の確認 |

全文は [skills/adhd-report/SKILL.md](skills/adhd-report/SKILL.md) にあります。
設計書は [docs/](docs/) にあります。

## インストール

このリポジトリの作業では、インストールしていません。
ローカルのクローン、または GitHub のリポジトリから入れる場合は、次のとおりです。

```bash
claude plugin marketplace add <path または user/repo>
claude plugin install adhd-report@adhd-report
```

続いて `/adhd-report` と入力します。

### 常時有効にする

```bash
touch ~/.claude/.adhd-report-always
```

SessionStart のフックが、startup、resume、clear、compact のたびにルールを注入します。
そのセッションだけ止めるには、「stop adhd-report」と伝えます。
ずっと止めるには、このファイルを削除します。

### i-have-adhd と並べて使う場合

名前が違うので、両方をインストールできます。
ただし、常時有効の印を両方作ると、2つのルールが同時に注入され、決まり5が食い違います。
i-have-adhd から入れ替える場合は、元の plugin をアンインストールし、`~/.claude/.i-have-adhd-always` を削除してください。

## 開発

設計書を先に更新し、次に失敗するテストを書き、最後に本文を直します。

```bash
python3 -m unittest discover -s tests       # テスト（外部通信なし）
python3 scripts/run_evals.py validate        # eval ケースの形式の確認
python3 scripts/run_evals.py plan --trials 3 # 実行計画を表示する（実行はしない）
```

`evals/` は、`claude` CLI で baseline と candidate の返事を比べます。
実行には費用がかかるので、流す前に [evals/README.md](evals/README.md) を読んでください。

## クレジット

- 元のスキル、フック、eval の仕組み: [Ayoub Ghriss](https://github.com/ayghri)、[ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd)、MIT。
- 元のスキルは、J. Russell Ramsay と Anthony L. Rostain による *The Adult ADHD Tool Kit* を大まかに参考にしている。
- 追加分: Isobe Kazuhiko。

## ライセンス

MIT。[LICENSE](LICENSE) を参照してください。
元の著作権表示を残し、このプロジェクトの分を足しています。
