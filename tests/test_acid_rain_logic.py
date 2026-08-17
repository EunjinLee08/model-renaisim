import pathlib
import random
import re
import textwrap
import types
import unittest


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE_PATH = PROJECT_ROOT / "game" / "minigames" / "acid_rain.rpy"


class FakeRenPy:
    def __init__(self):
        self.store = types.SimpleNamespace()
        self.random = random.Random(7)


class AcidRainLogicTests(unittest.TestCase):
    def setUp(self):
        source = SOURCE_PATH.read_text(encoding="utf-8")
        match = re.search(r"init python:\n(?P<body>.*?)(?=\nscreen acid_rain_screen)", source, re.S)
        self.assertIsNotNone(match, "init python 블록을 찾을 수 없습니다.")

        self.renpy = FakeRenPy()
        self.ns = {
            "renpy": self.renpy,
            "ACID_RAIN_TICK": 0.05,
            "ACID_RAIN_DURATION": 45.0,
            "ACID_RAIN_MAX_LIVES": 5,
        }
        exec(textwrap.dedent(match.group("body")), self.ns)
        self.ns["acid_rain_reset"]()

    def test_word_bank_and_stats_only_use_programming_languages(self):
        stats = self.renpy.store.acid_rain_stats
        self.assertEqual(set(stats), {"C", "Python"})
        self.assertEqual(
            {word["category"] for word in self.ns["ACID_RAIN_WORDS"]},
            {"C", "Python"},
        )
        self.assertTrue(all(word["text"].isascii() for word in self.ns["ACID_RAIN_WORDS"]))
        self.assertEqual(self.renpy.store.acid_rain_lives, 5)

    def test_code_display_escapes_renpy_markup_characters(self):
        code = 'result = {"score": items[0]}'

        escaped = self.ns["acid_rain_escape_code"](code)

        self.assertEqual(escaped, 'result = {{"score": items[[0]}')

    def test_submission_preserves_code_whitespace(self):
        self.renpy.store.acid_rain_active_words = [
            {"id": 1, "text": "return 0;", "category": "C", "x": 100, "y": 500, "speed": 100, "born_at": 0.0},
        ]
        self.renpy.store.acid_rain_stats["C"]["appeared"] = 1
        self.renpy.store.acid_rain_input = " return 0;"

        self.ns["acid_rain_submit"]()

        self.assertEqual(len(self.renpy.store.acid_rain_active_words), 1)
        self.assertEqual(self.renpy.store.acid_rain_wrong_inputs, 1)

    def test_correct_submission_removes_lowest_matching_word_and_scores(self):
        self.renpy.store.acid_rain_active_words = [
            {"id": 1, "text": 'printf("%d\\n", score);', "category": "C", "x": 100, "y": 100, "speed": 100, "born_at": 0.0},
            {"id": 2, "text": 'printf("%d\\n", score);', "category": "C", "x": 200, "y": 700, "speed": 100, "born_at": 0.0},
        ]
        self.renpy.store.acid_rain_stats["C"]["appeared"] = 2
        self.renpy.store.acid_rain_elapsed = 1.5
        self.renpy.store.acid_rain_input = 'printf("%d\\n", score);'

        self.assertIsNone(self.ns["acid_rain_submit"]())
        self.assertEqual([word["id"] for word in self.renpy.store.acid_rain_active_words], [1])
        self.assertEqual(self.renpy.store.acid_rain_score, 100)
        self.assertEqual(self.renpy.store.acid_rain_stats["C"]["correct"], 1)
        self.assertEqual(self.renpy.store.acid_rain_input, "")

    def test_missed_word_reduces_life_and_updates_its_category(self):
        self.renpy.store.acid_rain_active_words = [
            {"id": 1, "text": "#include <stdio.h>", "category": "C", "x": 100, "y": 889, "speed": 100, "born_at": 0.0},
        ]
        self.renpy.store.acid_rain_stats["C"]["appeared"] = 1

        self.ns["acid_rain_tick"](0.05)

        self.assertEqual(self.renpy.store.acid_rain_lives, 4)
        self.assertEqual(self.renpy.store.acid_rain_stats["C"]["missed"], 1)
        self.assertEqual(self.renpy.store.acid_rain_active_words, [])

    def test_result_contains_per_category_accuracy(self):
        stats = self.renpy.store.acid_rain_stats["Python"]
        stats.update({"appeared": 4, "correct": 3, "missed": 1})

        result = self.ns["acid_rain_make_result"]()

        self.assertEqual(result["categories"]["Python"]["accuracy"], 75.0)
        self.assertEqual(result["correct"], 3)
        self.assertEqual(result["missed"], 1)

    def test_result_reports_most_typed_category_or_tie(self):
        cases = [
            (3, 1, "C"),
            (1, 3, "Python"),
            (2, 2, "tie"),
            (0, 0, "tie"),
        ]

        for c_correct, python_correct, expected in cases:
            with self.subTest(c=c_correct, python=python_correct):
                self.renpy.store.acid_rain_stats["C"]["correct"] = c_correct
                self.renpy.store.acid_rain_stats["Python"]["correct"] = python_correct

                result = self.ns["acid_rain_make_result"]()

                self.assertEqual(result["most_typed_category"], expected)


if __name__ == "__main__":
    unittest.main()
