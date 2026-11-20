English | [日本語](README_ja.md)

# adhd-report

A Claude Code skill that shapes output and reports for a reader with ADHD.

It is built on [i-have-adhd](https://github.com/ayghri/i-have-adhd) by Ayoub Ghriss (MIT). The ten original rules are kept. Rules 11 to 17 and a section for multi-agent sessions are added, based on where the author's own session logs showed the reader getting stuck.

## What it adds

| Where | Rule |
|---|---|
| Rule 5 (changed) | A turn started by an already-reported notification gets one parenthetical line naming what still waits on the reader. This resolves the clash between "restate state every turn" and "do not repeat yourself" |
| Rule 9 (changed) | Lists stay at 5 items. Decisions are stricter: one at a time |
| Rule 11 | One decision at a time. Say the count, give the first, wait for the answer |
| Rule 12 | Every decision ask stands alone: which task, what to decide, why now, who does what for each option, recommendation. Same for AskUserQuestion |
| Rule 13 | Stacked abstract nouns become "who does what to where", one thing per sentence |
| Rule 14 | "Is my understanding right?" gets yes or no first, then one or two reasons |
| Rule 15 | Reply in the reader's language, labels included (「次:」, not "Next:") |
| Rule 16 | No unrelated operations news in a report |
| Rule 17 | When the reader must act, line 1 is 「あなたの操作:」 plus numbered steps |
| Multi-agent sessions | Parenthetical line for repeated notifications, pending decisions announced at a pause, status ordered pending → in progress → done, long agent reports split into single decisions, short ledger lines, a check after launching an agent |

Full text: [skills/adhd-report/SKILL.md](skills/adhd-report/SKILL.md). Design documents: [docs/](docs/).

## Install

Not installed by this repository's setup. To install from a local clone or a GitHub repository:

```bash
claude plugin marketplace add <path-or-user/repo>
claude plugin install adhd-report@adhd-report
```

Then type `/adhd-report`.

### Always on

```bash
touch ~/.claude/.adhd-report-always
```

A SessionStart hook injects the ruleset on startup, resume, clear, and compact. Say "stop adhd-report" to turn it off for the current session. Delete the file to turn it off for good.

### Using it alongside i-have-adhd

The names are different, so both can be installed. Do not enable both always-on flags: both rulesets would be injected, and their rule 5 conflicts. If you are replacing i-have-adhd, uninstall it and delete `~/.claude/.i-have-adhd-always`.

## Develop

Specification first, then a failing test, then the change.

```bash
python3 -m unittest discover -s tests       # tests, no network
python3 scripts/run_evals.py validate        # check the eval cases
python3 scripts/run_evals.py plan --trials 3 # print the run matrix, runs nothing
```

`evals/` compares baseline and candidate responses with the `claude` CLI. Those runs cost money, so see [evals/README.md](evals/README.md) before running them.

## Credits

- Original skill, hooks, and eval harness: [Ayoub Ghriss](https://github.com/ayghri), [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd), MIT.
- Original skill is loosely based on *The Adult ADHD Tool Kit* by J. Russell Ramsay and Anthony L. Rostain.
- Additions: Isobe Kazuhiko.

## License

MIT. See [LICENSE](LICENSE). It keeps the original copyright notice and adds this project's.
