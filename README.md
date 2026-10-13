# Rental Strategies in Bergamo: More Tourists, More Profit?

By Pedram Kojouri — research snapshot, 13 October 2026.

## Business question
Does growing tourism make short-term renting financially preferable to a residential lease in the **City of Bergamo**? Market demand is observed; owner cash income is modelled. This project does not estimate average city profit or guarantee investment returns.

## Reproduce
Python 3.10 or newer; no external dependencies for the core analysis.

```sh
python analysis.py
python airport_analysis.py
```

The script validates 72 monthly observations against six annual controls, reconstructs seasonal allocations, calculates both strategies, checks ceiling break-even requirements and generates `results/analysis.json`. It runs entirely offline using the frozen snapshots. Assertions fail on missing controls or changed arithmetic. It does not download current listings.

To rebuild the illustrated Word report, install `requirements-report.txt` and run `build_report.py` from this repository directory. The report is written to `report/`. Matplotlib generates eight figures with titles, units and source notes in their document captions.

## Findings and assumptions
- City guest nights rose from 791,353 in 2019 to 1,208,189 in the 2024 regional extract. The 2025 local report gives 1,359,923; this is a different release and no validated 2025 monthly series is included.
- April–October is a recurring broad high-demand season. City guest nights are not apartment booked nights. The assumed 180 booked nights are seasonally distributed, not estimated from a reservation panel.
- Base short-term annual net cash: EUR 6,544.50. Long-term: EUR 6,732. Difference: EUR -187.50. These inputs cannot support a robust ranking.
- 180 bookings, 330 available nights, EUR 115 gross nightly revenue, 15.5% host fee and eligible 21% tax are conditional assumptions. EUR 115 is reference-informed, **not verified as directly comparable gross ADR**.
- Owner-paid cleaning: EUR 30 per turnover and three-night stays. No separate guest cleaning charge. Other variable allowance: EUR 10 per booked night. Common fixed allowance EUR 1,800; additional short-term allowance EUR 1,200. No owner-time valuation is deducted.
- Acquisition, borrowing, exceptional repairs, professional management and incremental preparation are excluded from base cash. Five-year preparation recovery is a separate, undiscounted illustration.

## Listing screening
`data/listings.csv` records 21 unique candidate IDs: original three plus 18 additional candidates. Only six furnished one-bedroom offers with a 4+4 option and approximately 45–60 dwelling square metres enter the primary cohort. Sample median EUR 900 is descriptive, not a city benchmark. Furnishing, parking, surface definitions and quality are not perfectly matched. Temporary, annual, serviced and unconfirmed contracts are separated. A later failed re-fetch does not erase the earlier snapshot or establish current availability.

**The proposed 15–30 genuinely comparable listings target remains unmet.** Including unsuitable offers to inflate sample size would mislead. No probability sample, causal estimate or confidence interval is claimed.

## Data provenance and rights
Regional monthly source: https://www.dati.lombardia.it/d/mzxz-sz25
Regional annual control: https://www.dati.lombardia.it/d/vyxt-7jdx
City scope: Comune di Bergamo, ISTAT 016024 (some portal fields omit leading zero).

Source endpoints: `https://www.dati.lombardia.it/resource/{dataset_id}.json` filtered to `comune='Bergamo'`. Frozen files preserve the project extract; rerunning on a live release may produce revisions. Monthly derived data are aggregate numerical observations with source attribution. Annual control contains only city aggregate rows. No claim of ownership of source data is made; reuse remains subject to provider terms. Provider metadata should be consulted before broader redistribution.

FULL research (Chiodelli and Cassiani, 2026) uses AirDNA estimates for historical short-term performance. FULL and AirDNA are **not independent corroborations**. Proprietary listing-level reservation data are not redistributed here. Listing registry contains independently tabulated factual fields, URLs and screening decisions only: no copied descriptions, photographs, names, phone numbers or contacts. Other source URLs and qualifications appear in the report references.

2024 regional/local releases differ by one arrival and four guest nights overall, and by 27 October guest nights. This unresolved revision discrepancy is retained in the report rather than silently pooled.

## Interpretation limits
Tourism peaks do not imply full occupancy. Blocked platform calendars are not verified bookings. Airport traffic and Milan events have not been linked causally to Bergamo property income. Local legal eligibility, current municipal amendments, taxes and supplier costs require property-specific verification; CIN alone does not establish compliance. Fixed-cost line items and stress ranges are analyst budgeting assumptions, not local quotes.

## Files
`analysis.py`: dependency-free calculations and validation.
`data/`: frozen inputs and listing decisions.
`results/analysis.json`: generated results.
`build_report.py`: English Word report and charts.
`report/`: generated deliverables, included in the downloadable local package.

Conclusion: a credible market opportunity with conditional competitiveness; no proven general advantage for converting homes across Bergamo.

## Complete v03 report and publication assets
The two previous report versions were compared. The v02 financial model and limitations were retained, duplicates removed, and the airport comparison plus a dedicated methodology/challenges chapter added. Eight chapters now include a separate contents page and a clickable author LinkedIn header on every report page.

- `report/Bergamo_Rental_Strategies_Complete_EN_v03.pdf`: complete English report.
- `report/Bergamo_Rental_Strategies_Complete_EN_v03.docx`: editable report.
- `report/Bergamo_Report_Contents_EN.pdf`: separate contents (page numbers refer to v03).
- `publication/Bergamo_LinkedIn_Carousel_EN_Final.pdf`: nine-page LinkedIn carousel.
- `publication/LinkedIn_Caption_EN.txt`: 193-word caption, prepared for review, not posted.

`airport_analysis.py` validates seven 2019–2025 annual airport totals against two Assaeroporti tables for each year and produces a city join, indexed growth and year-on-year changes. In 2025, passengers declined 2.4% while city arrivals grew 10.7% and guest nights grew 12.6%. This divergence prevents treating airport passengers as a direct reservation proxy. No causal airport-to-profit effect is estimated. Annual passenger movements are not unique local tourists.

`data/airport-bgy-source-rows.json` contains only numeric Bergamo rows from Assaeroporti traffic tables, with source URLs. Both monthly December and cumulative January–December records are preserved for audit; the analysis uses cumulative passenger totals. The analyst-tabulated `airport-city-annual.json` joins these values to official city observations. City 2025 is from the 14 May 2026 Provincia release, rather than the regional series through 2024. Source rights remain with providers. No source page text, photographs or personal data are redistributed.

The Word builder creates a live contents field. Refresh fields in Microsoft Word before PDF export to populate the contents and page numbers. Word or another compatible renderer is required for PDF output; the Python builder does not render PDFs itself. The carousel follows Pedram Kojouri's existing brand kit and uses editable chart/table objects. Its displayed index values round to two decimals; full calculations remain in the data and JSON output.
