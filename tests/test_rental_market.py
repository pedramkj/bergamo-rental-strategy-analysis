import csv,json,math,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import rental_market_analysis as m
from financial_model import load_assumptions,str_cash,ltr_cash
class RentalReconstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=m.run();cls.master=m.read('master-listing-registry.csv');cls.obs={r['listing_id']:r for r in m.read('source-observations.csv')}
    def test_all_supplied_candidates_retained(self):
        ids={r['candidate_id'] for r in self.master}
        self.assertTrue({f'C{i:02}' for i in range(1,22)}<=ids)
        self.assertTrue({f'A{i:02}' for i in range(1,21)}<=ids)
        self.assertEqual(self.r['counts']['total_candidates'],96)
    def test_raw_arithmetic_independently(self):
        self.assertEqual(self.r['raw_original_numeric']['total'],17240)
        self.assertEqual(self.r['raw_original_numeric']['n'],17)
        self.assertEqual(self.r['raw_assistant_leads']['total'],17185)
        self.assertEqual(self.r['raw_assistant_leads']['mean'],859.25)
    def test_original_prices_are_unchanged(self):
        with (ROOT/'data/listings.csv').open(encoding='utf8') as f:original=list(csv.DictReader(f))
        audit=m.read('original-21-audit.csv')
        self.assertEqual([r['monthly_eur'] for r in original],[r['recorded_price'] for r in audit])
    def test_missing_does_not_become_zero(self):
        o=self.obs['36732340'];self.assertEqual(o['base_monthly_eur'],'')
        self.assertEqual(m.numeric(''),None)
    def test_recovered_prices_have_new_provenance(self):
        for ident,price in [('70888294',1300),('124638879',1000),('133410286',700),('121511946',1300)]:
            self.assertEqual(float(self.obs[ident]['advertised_monthly_eur']),price)
            self.assertEqual(self.obs[ident]['verification_date'],'2026-10-14')
    def test_bundle_without_evidenced_split_rejected(self):
        self.assertIsNone(m.normalise_price(900,bundled=True))
        self.assertEqual(self.obs['99990082']['base_monthly_eur'],'')
        self.assertNotEqual(self.obs['99990082']['base_monthly_eur'],'590')
    def test_base_and_charge_are_not_double_deducted(self):
        self.assertEqual(m.normalise_price(850,base=850,explicit_charges=50,bundled=True),850)
        self.assertEqual(m.normalise_price(900,explicit_charges=50,bundled=True),850)
        self.assertEqual(float(self.obs['663229251']['base_monthly_eur']),850)
    def test_temporary_contract_never_primary(self):
        self.assertEqual(m.contract_class('temporary_or_3+2'),'temporary')
        self.assertEqual(m.contract_class('4+4'),'4+4')
        self.assertNotEqual(m.screen(self.obs['99990082'])[0],'primary')
    def test_geography_requires_positive_selected_scope(self):
        r=dict(self.obs['132189102']);self.assertFalse(m.geographic_eligible(r))
        r.update(neighborhood='Centro');self.assertTrue(m.geographic_eligible(r))
        r.update(review_flag='conflicting_location');self.assertFalse(m.geographic_eligible(r))
    def test_no_automatic_street_or_price_merge(self):
        rows=[dict(candidate_id='X',url='one'),dict(candidate_id='Y',url='two')]
        groups=m.property_groups(rows,[dict(left_candidate='X',right_candidate='Y',decision='probable_duplicate')])
        self.assertNotEqual(groups['X'],groups['Y'])
        groups=m.property_groups(rows,[dict(left_candidate='X',right_candidate='Y',decision='confirmed_duplicate')])
        self.assertEqual(groups['X'],groups['Y'])
    def test_confirmed_matches_exclude_price_conflicts(self):
        a=next(r for r in self.master if r['candidate_id']=='A02')
        b=next(r for r in self.master if r.get('listing_id')=='663707911')
        self.assertEqual(a['property_id'],b['property_id']);self.assertEqual(a['cohort'],'excluded')
    def test_source_urls_preserved(self):
        with (ROOT/'data/listings.csv').open(encoding='utf8') as f:original=list(csv.DictReader(f))
        self.assertEqual({r['url'] for r in original},{r['url'] for r in self.master if r['origin']=='original_21'})
    def test_cohort_counts_and_reconciliation(self):
        c=self.r['counts'];self.assertEqual(c['primary_properties'],14);self.assertEqual(c['secondary_properties'],11)
        self.assertEqual(c['canonical_groups_including_unresolved'],c['primary_properties']+c['secondary_properties']+c['excluded_canonical_groups'])
        self.assertEqual(c['total_candidates'],c['canonical_groups_including_unresolved']+c['confirmed_duplicate_rows_removed'])
        self.assertIsNone(c['unique_physical_properties_total'])
    def test_primary_price_statistics(self):
        r=self.r['primary'];self.assertEqual(r['total'],12520);self.assertAlmostEqual(r['mean'],12520/14);self.assertEqual(r['median'],850)
        self.assertEqual(r['min'],650);self.assertEqual(r['max'],1200)
        self.assertEqual(r['q1'],755);self.assertEqual(r['q3'],987.5)
    def test_unit_price_uses_each_property_area(self):
        rows=m.read('primary-comparable-sample.csv');expected=sum(float(x['base_monthly_eur'])/float(x['advertised_m2']) for x in rows)/len(rows)
        self.assertAlmostEqual(expected,self.r['primary_price_per_advertised_m2']['mean'])
    def test_historical_financials_unchanged(self):
        h=self.r['historical_900_scenario'];self.assertAlmostEqual(h['str_net'],6544.5);self.assertEqual(h['ltr_net'],6732);self.assertAlmostEqual(h['gap'],-187.5)
        self.assertEqual([x['minimum_whole_nights'] for x in h['break_even']],[184,203,222,241])
    def test_evidence_model_uses_unrounded_mean(self):
        e=self.r['evidence_informed_scenario'];rent=12520/14
        self.assertEqual(e['monthly_base_rent'],rent);self.assertAlmostEqual(e['ltr_net'],12*rent*.79-1800);self.assertAlmostEqual(e['gap'],-133.328571428571)
    def test_new_break_even_is_minimal(self):
        a=load_assumptions();e=self.r['evidence_informed_scenario'];self.assertEqual([x['minimum_whole_nights'] for x in e['break_even']],[183,202,221,240])
        for row in e['break_even']:
            target=e['ltr_net']+row['setup']/a['recovery_years'];n=row['minimum_whole_nights']
            self.assertGreaterEqual(str_cash(n,115,a),target);self.assertLess(str_cash(n-1,115,a),target)
            self.assertAlmostEqual(str_cash(180,row['required_nightly_price'],a),target)
    def test_report_source_matches_reviewed_counts(self):
        narrative=(ROOT/'src/rental_report_sections.py').read_text(encoding='utf8')
        self.assertIn('manual online rental listing review',narrative.casefold())
        self.assertIn("r['primary']",narrative)
        self.assertNotIn('in-person field survey',narrative)
    def test_no_personal_contacts_in_public_observations(self):
        text=(ROOT/'data/rental/source-observations.csv').read_text(encoding='utf8')
        self.assertNotIn('@',text);self.assertNotIn('WhatsApp',text)
    def test_unresolved_prices_never_enter_sample(self):
        for r in m.read('primary-comparable-sample.csv')+m.read('secondary-sample.csv'):
            self.assertEqual(r['status'],'verified_advertisement');self.assertGreater(float(r['base_monthly_eur']),0)
if __name__=='__main__':unittest.main()
