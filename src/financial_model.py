"""Cash-income formulas shared by calculation and report generation.

Inputs live in data/assumptions.json. These functions do not infer market profits
or legal eligibility from the scenario tax and fee rates.
"""
import json
import math
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOKING_SCENARIOS = (150, 180, 210)
PRICE_SCENARIOS = (100, 115, 130)
RENT_SCENARIOS = (700, 800, 900, 1000, 1100)
COMPARISON_RENTS = (800, 900, 1000)
INCREMENTAL_COST_SCENARIOS = (600, 1200, 1800)
PREPARATION_SCENARIOS = (0, 5000, 10000, 15000)


def load_assumptions():
    return json.loads((ROOT / 'data' / 'assumptions.json').read_text(encoding='utf8'))


def snapshot_fingerprint(a):
    """Canonical JSON fingerprint, independent of checkout line endings."""
    return hashlib.sha256(json.dumps(a, sort_keys=True, separators=(',', ':')).encode('utf8')).hexdigest()


def validate_assumptions(a):
    for key in ['gross_nightly_eur', 'stay_nights', 'recovery_years', 'available_nights']:
        if a[key] <= 0:
            raise ValueError(f'{key} must be positive')
    if not 0 <= a['booked_nights'] <= a['available_nights']:
        raise ValueError('Booked nights must lie within available nights')
    if not 0 <= a['paid_months'] <= 12:
        raise ValueError('Paid months must lie between zero and twelve')
    if not (0 <= a['tax'] < 1 and 0 <= a['host_fee'] < 1 and a['tax'] + a['host_fee'] < 1):
        raise ValueError('Invalid tax or host fee rate')
    for key in ['cleaning_per_turnover', 'other_variable_per_night', 'common_fixed', 'str_incremental_fixed', 'long_monthly']:
        if a[key] < 0:
            raise ValueError(f'{key} cannot be negative')


def contribution(adr, a):
    return adr * (1 - a['tax'] - a['host_fee']) - a['cleaning_per_turnover'] / a['stay_nights'] - a['other_variable_per_night']


def str_cash(n, adr, a, incremental=None):
    return n * contribution(adr, a) - a['common_fixed'] - (a['str_incremental_fixed'] if incremental is None else incremental)


def ltr_cash(rent, a, months=None):
    return rent * (a['paid_months'] if months is None else months) * (1 - a['tax']) - a['common_fixed']


def booking_threshold(setup, a):
    margin = contribution(a['gross_nightly_eur'], a)
    if margin <= 0:
        raise ValueError('A positive contribution per booked night is required')
    exact = (ltr_cash(a['long_monthly'], a) + a['common_fixed'] + a['str_incremental_fixed'] + setup / a['recovery_years']) / margin
    return {'setup': setup, 'exact_nights': exact, 'minimum_whole_nights': math.ceil(exact)}


def required_nightly_price(setup, a):
    if a['booked_nights'] <= 0:
        raise ValueError('Booked nights must be positive for a price threshold')
    costs = a['cleaning_per_turnover'] / a['stay_nights'] + a['other_variable_per_night']
    return ((ltr_cash(a['long_monthly'], a) + a['common_fixed'] + a['str_incremental_fixed'] + setup / a['recovery_years']) / a['booked_nights'] + costs) / (1 - a['tax'] - a['host_fee'])


def cash_bridge(a):
    gross = a['booked_nights'] * a['gross_nightly_eur']
    return [gross, -gross * a['tax'], -gross * a['host_fee'],
            -a['booked_nights'] / a['stay_nights'] * a['cleaning_per_turnover'],
            -a['booked_nights'] * a['other_variable_per_night'],
            -a['common_fixed'] - a['str_incremental_fixed'],
            round(str_cash(a['booked_nights'], a['gross_nightly_eur'], a), 2)]
