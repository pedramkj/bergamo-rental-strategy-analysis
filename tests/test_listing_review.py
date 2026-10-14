import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from listing_review import parse_monthly_eur, review

class ListingReviewTests(unittest.TestCase):
    def test_italian_separator(self):
        self.assertEqual(parse_monthly_eur('1.200'),1200)
        self.assertEqual(parse_monthly_eur('900'),900)
        self.assertEqual(parse_monthly_eur('900.50'),900.5)

    def test_missing_and_invalid_prices(self):
        for value in ['', 'unknown', '0', '-100', '1,200']:
            self.assertIsNone(parse_monthly_eur(value))

    def test_registry_statistics(self):
        data=review()
        self.assertEqual(data['registry_records'],21)
        self.assertEqual(data['missing_or_invalid_prices'],4)
        self.assertEqual(data['all_recorded_numeric_prices']['count'],17)
        self.assertAlmostEqual(data['all_recorded_numeric_prices']['arithmetic_mean_eur_month'],17240/17)
        self.assertEqual(data['all_recorded_numeric_prices']['median_eur_month'],1000)

    def test_mean_is_not_subgroup_median(self):
        subgroup=review()['historical_primary_subgroup']
        self.assertEqual(subgroup['count'],6)
        self.assertEqual(subgroup['arithmetic_mean_eur_month'],1000)
        self.assertEqual(subgroup['median_eur_month'],900)

    def test_no_unverified_claim(self):
        data=review()
        self.assertFalse(data['claimed_city_centre_mean_approximately_900_verified'])
        self.assertIsNone(data['eligible_21_listing_arithmetic_mean'])
        self.assertEqual(data['duplicate_listing_ids'],[])
        self.assertEqual(data['duplicate_listing_urls'],[])

if __name__=='__main__':unittest.main()
