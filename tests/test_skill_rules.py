from __future__ import annotations


import json
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "adhd-report" / "SKILL.md"
HOOK = ROOT / "hooks" / "always-on.sh"
UPSTREAM_SKILL_CHARS = 6700

NEW_EVAL_CASES = {
    "decision-one-at-a-time",
    "decision-standalone",
    "confirm-yes-no",
    "duplicate-notification",
    "user-action-needed",
    "status-overview-order",
    "abstract-sentence-rephrase",
    "pending-decisions-pause",
}


def skill_text() -> str:
    return SKILL.read_text(encoding="utf-8")


def section(heading_pattern: str, text: str | None = None) -> str:
    """Return the body under the first heading matching the pattern, up to the next heading of the same or higher level."""
    text = text if text is not None else skill_text()
    match = re.search(rf"^(#+) {heading_pattern}.*$", text, re.MULTILINE)
    if not match:
        raise AssertionError(f"heading not found: {heading_pattern}")
    level = len(match.group(1))
    rest = text[match.end():]
    end = re.search(rf"^#{{1,{level}}} ", rest, re.MULTILINE)
    return rest[: end.start()] if end else rest


class NamingTest(unittest.TestCase):
    def test_skill_name_matches_directory(self):
        self.assertRegex(skill_text(), r"(?m)^name: adhd-report$")
        self.assertTrue(SKILL.parent.name == "adhd-report")

    def test_manifests_use_new_names(self):
        plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
        market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
        self.assertEqual("adhd-report", plugin["name"])
        self.assertEqual("adhd-report", market["name"])
        self.assertEqual(["adhd-report"], [p["name"] for p in market["plugins"]])

    def test_upstream_name_does_not_leak_into_runtime_files(self):
        runtime = [
            SKILL,
            HOOK,
            ROOT / "hooks" / "hooks.json",
            ROOT / ".claude-plugin" / "plugin.json",
            ROOT / ".claude-plugin" / "marketplace.json",
        ]
        for path in runtime:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("i-have-adhd", text, path.name)
            self.assertNotIn("adhd mode", text.lower(), path.name)

    def test_license_keeps_upstream_notice_and_adds_own(self):
        text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("Copyright (c) 2026 Ayoub Ghriss", text)
        self.assertIn("Isobe Kazuhiko", text)


class HookTest(unittest.TestCase):
    def run_hook(self, flag_name):
        with tempfile.TemporaryDirectory() as tmp:
            if flag_name:
                (Path(tmp) / flag_name).write_text("")
            env = {**os.environ, "CLAUDE_CONFIG_DIR": tmp}
            done = subprocess.run(
                ["sh", str(HOOK)], env=env, capture_output=True, text=True, check=False
            )
        self.assertEqual(0, done.returncode)
        return done.stdout

    def test_no_flag_prints_nothing(self):
        self.assertEqual("", self.run_hook(None))

    def test_flag_injects_ruleset_without_frontmatter(self):
        out = self.run_hook(".adhd-report-always")
        self.assertTrue(out.startswith("ADHD-REPORT ACTIVE"))
        self.assertIn('"stop adhd-report"', out)
        self.assertIn("# adhd-report", out)
        self.assertNotIn("disable-model-invocation", out)

    def test_upstream_flag_alone_does_not_activate(self):
        self.assertEqual("", self.run_hook(".i-have-adhd-always"))


class AddedRulesTest(unittest.TestCase):
    def rule(self, number: int) -> str:
        return section(rf"{number}\. ")

    def assertMentions(self, body: str, *patterns: str):
        low = body.lower()
        for pattern in patterns:
            self.assertRegex(low, pattern)

    def test_rule_11_one_decision_at_a_time(self):
        self.assertMentions(
            self.rule(11), r"one decision", r"wait for the answer", r"n件あります|\bn items\b"
        )

    def test_rule_12_decision_ask_stands_alone(self):
        body = self.rule(12)
        self.assertMentions(
            body,
            r"which task",
            r"what to decide",
            r"why now",
            r"who does what",
            r"recommend",
            r"askuserquestion",
            r"scroll",
        )

    def test_rule_13_who_does_what_to_where(self):
        self.assertMentions(self.rule(13), r"who", r"what", r"where", r"one thing per sentence")

    def test_rule_14_yes_no_first(self):
        self.assertMentions(
            self.rule(14), r"yes or no", r"first word|opening word|first", r"one or two"
        )

    def test_rule_15_reader_language(self):
        self.assertMentions(self.rule(15), r"language", r"label", r"次:")

    def test_rule_16_operations_noise(self):
        self.assertMentions(self.rule(16), r"operations|housekeeping", r"cleanup|clean-up|cleaned up", r"monitor")

    def test_rule_17_your_action(self):
        self.assertMentions(self.rule(17), r"あなたの操作:", r"first line", r"numbered")


class MultiAgentSectionTest(unittest.TestCase):
    def body(self) -> str:
        return section("Multi-agent sessions")

    def test_section_exists_and_is_scoped(self):
        self.assertRegex(self.body().lower(), r"several agents|multiple agents")

    def test_c1_parenthetical_one_line_for_repeated_notifications(self):
        low = self.body().lower()
        for pattern in (r"already reported", r"parenthes", r"one line", r"new completion"):
            self.assertRegex(low, pattern)

    def test_c2_pending_decisions_at_a_pause(self):
        low = self.body().lower()
        for pattern in (r"pause", r"do not interrupt|never interrupt", r"not .*end of every report|not append"):
            self.assertRegex(low, pattern)

    def test_c3_status_order(self):
        low = self.body().lower()
        self.assertRegex(low, r"pending decisions.*in progress.*done")
        self.assertRegex(low, r"one line per agent")

    def test_c4_split_long_agent_reports(self):
        low = self.body().lower()
        self.assertRegex(low, r"long report")
        self.assertRegex(low, r"line numbers")

    def test_c5_ledger_lines_are_short(self):
        body = self.body()
        for token in ("40", "30", "TASKS.md"):
            self.assertIn(token, body)
        self.assertRegex(body.lower(), r"history")

    def test_c6_check_after_launch(self):
        low = self.body().lower()
        self.assertRegex(low, r"after (you )?(start|launch)")
        self.assertRegex(low, r"trust|approval")


class ConflictResolutionTest(unittest.TestCase):
    def test_rule_5_has_notification_exception(self):
        body = section(r"5\. ").lower()
        for pattern in (r"notification", r"already reported", r"one parenthetical line", r"still waiting"):
            self.assertRegex(body, pattern)
        self.assertIn("（返事を待っている事はありません）", section(r"5\. "))

    def test_rule_5_never_goes_fully_silent(self):
        self.assertRegex(section(r"5\. ").lower(), r"never (reply|respond) with nothing|not .*(empty|silent)")

    def test_rule_9_decisions_are_single(self):
        body = section(r"9\. ").lower()
        self.assertRegex(body, r"decision")
        self.assertRegex(body, r"one at a time|one decision")

    def test_rule_10_allows_item_count_line(self):
        body = section(r"10\. ")
        self.assertIn("N件あります", body)

    def test_rule_1_covers_decision_and_action_openers(self):
        low = section(r"1\. ").lower()
        self.assertIn("あなたの操作:", section(r"1\. "))
        self.assertRegex(low, r"decision")

    def test_preflight_has_standalone_check(self):
        low = section("Pre-send check").lower()
        self.assertRegex(low, r"scroll")


class SizeTest(unittest.TestCase):
    def test_skill_stays_within_twice_upstream(self):
        self.assertLess(len(skill_text()), UPSTREAM_SKILL_CHARS * 2)


class EvalCatalogTest(unittest.TestCase):
    def test_new_cases_exist(self):
        ids = {
            json.loads(line)["id"]
            for line in (ROOT / "evals" / "cases.jsonl").read_text().splitlines()
            if line.strip()
        }
        self.assertEqual(set(), NEW_EVAL_CASES - ids)

    def test_new_cases_are_japanese_and_have_criteria(self):
        for line in (ROOT / "evals" / "cases.jsonl").read_text().splitlines():
            case = json.loads(line)
            if case["id"] in NEW_EVAL_CASES:
                self.assertRegex(case["prompt"], r"[぀-ヿ一-鿿]")
                self.assertGreaterEqual(len(case["criteria"]), 2)


if __name__ == "__main__":
    unittest.main()
