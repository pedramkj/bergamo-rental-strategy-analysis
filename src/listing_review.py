"""Audit recorded asking rents without claiming an eligible city-centre sample."""
import csv
import json
import re
import statistics
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def parse_monthly_eur(value):
    value = value.strip()
    if not value:
        return None
    # The source exports use Italian thousands separators, e.g. 1.200 = 1200.
    if re.fullmatch(r'\d{1,3}(?:\.\d{3})+', value):
        value = value.replace('.', '')
    elif not re.fullmatch(r'\d+(?:\.\d{1,2})?', value):
        return None
    number = float(value)
    return number if number > 0 else None


def describe(values):
    return {'count': len(values), 'arithmetic_mean_eur_month': statistics.mean(values) if values else None,
            'median_eur_month': statistics.median(values) if values else None,
            'minimum_eur_month': min(values) if values else None,
            'maximum_eur_month': max(values) if values else None,
            'sample_standard_deviation_eur_month': statistics.stdev(values) if len(values) > 1 else None}


def review(rows=None):
    if rows is None:
        with (ROOT / 'data/listings.csv').open(encoding='utf8', newline='') as f:
            rows = list(csv.DictReader(f))
    records = []
    for row in rows:
        price = parse_monthly_eur(row['monthly_eur'])
        records.append({'id': row['id'], 'url': row['url'], 'raw_price': row['monthly_eur'],
            'parsed_monthly_eur': price, 'recorded_area': row['area'] or None,
            'recorded_contract': row['contract'] or None, 'recorded_group': row['group'],
            'price_status': 'recorded_numeric_price' if price is not None else 'missing_or_invalid',
            'city_centre_study_area_membership': 'not_verified',
            'fee_comparability': 'not_fully_verified',
            'eligibility_for_21_listing_residential_mean': 'not_established',
            'existing_screening_note': row['reason']})
    values = [r['parsed_monthly_eur'] for r in records if r['parsed_monthly_eur'] is not None]
    primary = [r['parsed_monthly_eur'] for r in records if r['recorded_group'] == 'primary' and r['parsed_monthly_eur'] is not None]
    id_counts = Counter(r['id'] for r in records)
    url_counts = Counter(r['url'] for r in records)
    return {'review_date': '2026-10-14', 'registry_records': len(rows),
        'missing_or_invalid_prices': len(rows)-len(values), 'all_recorded_numeric_prices': describe(values),
        'historical_primary_subgroup': describe(primary), 'recorded_group_counts': dict(Counter(r['group'] for r in rows)),
        'area_label_missing_count': sum(not r['area'] for r in rows),
        'explicit_Centro_label_count': sum(r['area'] == 'Centro' for r in rows),
        'duplicate_listing_ids': [k for k,v in id_counts.items() if v>1],
        'duplicate_listing_urls': [k for k,v in url_counts.items() if v>1],
        'property_level_deduplication': 'not_verified; one existing record flags a possible cross-portal duplicate',
        'eligible_21_listing_arithmetic_mean': None,
        'claimed_city_centre_mean_approximately_900_verified': False,
        'baseline_monthly_rent_eur': 900,
        'baseline_status': 'retained scenario assumption; not verified as the arithmetic mean of 21 eligible city-centre rents',
        'interpretation': 'The 17-price descriptive mean includes heterogeneous screening candidates. It is not an eligible residential-rent benchmark. The separate six-record subgroup has a different selection and does not establish the requested 21-record statistic.',
        'records': records}


def run():
    result = review()
    path = ROOT / 'results/listing-review.json'
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n', encoding='utf8')
    print(json.dumps({k: result[k] for k in ['registry_records','missing_or_invalid_prices','all_recorded_numeric_prices','historical_primary_subgroup','claimed_city_centre_mean_approximately_900_verified']}, indent=2))
    return result


if __name__ == '__main__':
    run()
