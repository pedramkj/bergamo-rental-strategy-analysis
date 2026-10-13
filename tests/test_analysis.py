"""Regression and business-behaviour checks for the published research snapshot."""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import analysis
from financial_model import (booking_threshold, cash_bridge, load_assumptions,
    ltr_cash, required_nightly_price, str_cash, validate_assumptions)


class FinancialModelTests(unittest.TestCase):
    def setUp(self):
        self.a = load_assumptions()

    def test_base_cash(self):
        self.assertAlmostEqual(str_cash(180, 115, self.a), 6544.50)
        self.assertAlmostEqual(ltr_cash(900, self.a), 6732)
        self.assertAlmostEqual(str_cash(180, 115, self.a) - ltr_cash(900, self.a), -187.50)

    def test_price_and_booking_grid(self):
        expected = {150: [3525, 4953.75, 6382.5], 180: [4830, 6544.5, 8259], 210: [6135, 8135.25, 10135.5]}
        for n, values in expected.items():
            for rate, value in zip([100, 115, 130], values):
                self.assertAlmostEqual(str_cash(n, rate, self.a), value)

    def test_long_term_grid(self):
        for rent, expected in zip([700, 800, 900, 1000, 1100], [4836, 5784, 6732, 7680, 8628]):
            self.assertAlmostEqual(ltr_cash(rent, self.a), expected)

    def test_ceiling_thresholds(self):
        for setup, minimum in zip([0, 5000, 10000, 15000], [184, 203, 222, 241]):
            result = booking_threshold(setup, self.a)
            self.assertEqual(result['minimum_whole_nights'], minimum)
            target = ltr_cash(900, self.a) + setup / self.a['recovery_years']
            self.assertGreaterEqual(str_cash(minimum, 115, self.a), target)
            self.assertLess(str_cash(minimum - 1, 115, self.a), target)

    def test_price_threshold(self):
        required = required_nightly_price(0, self.a)
        self.assertAlmostEqual(str_cash(180, required, self.a), ltr_cash(900, self.a))

    def test_common_cost_cancels_gap(self):
        changed = {**self.a, 'common_fixed': 2700}
        self.assertAlmostEqual(str_cash(180, 115, changed) - ltr_cash(900, changed), -187.5)

    def test_differential_cost_changes_gap(self):
        self.assertAlmostEqual(str_cash(180, 115, self.a, 600) - ltr_cash(900, self.a), 412.5)

    def test_shorter_stays_increase_cleaning(self):
        self.assertAlmostEqual(str_cash(180, 115, {**self.a, 'stay_nights': 2}), 5644.5)

    def test_vacancy_alternative(self):
        self.assertAlmostEqual(ltr_cash(900, self.a, 11), 6021)

    def test_cash_bridge_reconciles(self):
        bridge = cash_bridge(self.a)
        self.assertAlmostEqual(sum(bridge[:-1]), bridge[-1])

    def test_invalid_inputs(self):
        for change in [{'stay_nights': 0}, {'booked_nights': 331}, {'tax': .9, 'host_fee': .2}]:
            with self.assertRaises(ValueError):
                validate_assumptions({**self.a, **change})

    def test_unreachable_threshold(self):
        with self.assertRaises(ValueError):
            booking_threshold(0, {**self.a, 'gross_nightly_eur': 10})


class AllocationAndValidationTests(unittest.TestCase):
    def test_allocation_totals_and_ties(self):
        for n in [0, 1, 134, 150, 180, 210]:
            values = analysis.allocate(n, [1 / 12] * 12)
            self.assertEqual(sum(values), n)
            self.assertLessEqual(max(values) - min(values), 1)
        self.assertEqual(analysis.allocate(1, [1 / 12] * 12)[0], 1)

    def test_validation_survives_optimisation(self):
        code = "from financial_model import validate_assumptions,load_assumptions; validate_assumptions({**load_assumptions(),'stay_nights':0})"
        result = subprocess.run([sys.executable, '-O', '-c', code], cwd=ROOT / 'src', capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('ValueError', result.stderr)

    def test_monthly_source_mismatch_rejected(self):
        original_read = analysis.read
        def altered_read(name):
            data = original_read(name)
            if name == 'validated-monthly-analysis.json':
                data[0]['guest_nights'] += 1
            return data
        analysis.read = altered_read
        try:
            with self.assertRaises(ValueError):
                analysis.run()
        finally:
            analysis.read = original_read


if __name__ == '__main__':
    unittest.main()
