"""Known-answer tests for Lab 16: python -m unittest test_asof -v"""
import contextlib
import io
import unittest

import asof


def quiet_run(decision, table=asof.TABLE):
    with contextlib.redirect_stdout(io.StringIO()):
        return asof.run(decision, table)


def printed(decision):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        asof.run(decision)
    return buf.getvalue()


class ProvenanceGateTests(unittest.TestCase):
    def test_row_funnel_matches_known_answer(self):
        r = quiet_run("2026-03-31")
        self.assertEqual(r["funnel"], [[11], [7], [3, 8, 10], [2]])
        self.assertEqual(r["panel"], [1, 4, 5, 6, 9, 12])

    def test_signals_match_known_answer(self):
        r = quiet_run("2026-03-31")
        self.assertEqual(r["asof"], {"AAA": (1.98, "2026-02"), "BBB": (-1.02, "2026-02"),
                                     "CCC": (0.91, "2026-02")})
        self.assertEqual(r["naive"], {"AAA": (5.83, "2026-03"), "BBB": (-5.15, "2026-03"),
                                      "CCC": (1.82, "2026-02")})

    def test_signals_against_hand_calculation(self):
        # Independent of the filter: the prices the lab says each signal should use.
        r = quiet_run("2026-03-31")
        hand = {"AAA": (103.0 / 101.0 - 1, 109.0 / 103.0 - 1),
                "BBB": (97.0 / 98.0 - 1, 92.0 / 97.0 - 1),
                "CCC": (111.0 / 110.0 - 1, 112.0 / 110.0 - 1)}
        for t, (asof_hand, naive_hand) in hand.items():
            self.assertEqual(r["asof"][t][0], round(asof_hand * 100, 2))
            self.assertEqual(r["naive"][t][0], round(naive_hand * 100, 2))
        # Handout: the AAA leak is +3.85 points nobody had on 31 March.
        self.assertEqual(round(r["naive"]["AAA"][0] - r["asof"]["AAA"][0], 2), 3.85)

    def test_revision_kept_not_original(self):
        # The classic error keeps row 2 (104.0) and reports AAA at +2.97%.
        r = quiet_run("2026-03-31")
        self.assertNotIn(2, r["panel"])
        self.assertIn(4, r["panel"])
        self.assertNotEqual(r["asof"]["AAA"][0], 2.97)

    def test_published_on_decision_date_is_knowable(self):
        # Row 4 (AAA Feb revision) was published 25 March: on that very day it counts.
        r = quiet_run("2026-03-25")
        self.assertIn(4, r["panel"])
        self.assertEqual(r["asof"]["AAA"][0], 1.98)
        # One day earlier only the original, row 2, was out: AAA would read +2.97%.
        r = quiet_run("2026-03-24")
        self.assertIn(2, r["panel"])
        self.assertEqual(r["asof"]["AAA"][0], 2.97)

    def test_swap_and_break_later_date_equals_naive(self):
        r = quiet_run("2026-04-15")
        self.assertEqual(r["asof"], r["naive"])

    def test_printed_report_names_month_and_two_decimals(self):
        out = printed("2026-03-31")
        for text in ("ROW FUNNEL", "AS-OF PANEL",
                     "+1.98% (February", "+5.83% (March",
                     "-1.02% (February", "-5.15% (March",
                     "+0.91% (February", "+1.82% (February"):
            self.assertIn(text, out)

    def test_pasting_full_lab_table_with_header(self):
        pasted = "| Row | Ticker | Month measured | Published on | Price |\n|---:|---|---|---|---:|\n"
        r = quiet_run("2026-03-31", pasted + asof.TABLE)
        self.assertEqual(r["panel"], [1, 4, 5, 6, 9, 12])

    def test_lab17_training_dates_preview(self):
        # Thursday's expected values on the training table; nothing extra is built for Lab 17 yet.
        early = printed("2026-02-28")
        self.assertIn("not enough knowable months", early)
        self.assertEqual(quiet_run("2026-02-28")["asof"], {})
        r = quiet_run("2026-04-30")
        self.assertEqual(r["asof"], r["naive"])


if __name__ == "__main__":
    unittest.main()
