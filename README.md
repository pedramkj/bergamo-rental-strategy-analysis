# More Tourists, Why Not More Profit?

*A Data-Driven Business Case Study on Rental Profitability in Bergamo*

Pedram Kojouri | October 2026

<a href="reports/Bergamo_Rental_Strategy_FINAL_2026.pdf"><img src="figures/report-cover.png" width="380" alt="More Tourists, Why Not More Profit? — approved navy-and-gold report cover"></a>

**More tourists do not automatically mean more profit for property owners.**

Would a vacant apartment in Bergamo retain more annual cash as a short-term tourist rental or a long-term residential lease? This independent Data Analytics case study combines official tourism and BGY airport trends, a manual rental-listing investigation and a Python financial model to compare the two strategies.

## Explore the project

| Resource | Open |
|---|---|
| Approved research report · 33 pages | [PDF](reports/Bergamo_Rental_Strategy_FINAL_2026.pdf) · [Editable Word](reports/Bergamo_Rental_Strategy_FINAL_2026.docx) |
| Interactive Power BI dashboard · five pages | [PBIX](powerbi/Bergamo.pbix) · [PBIP source and setup](powerbi/README.md) |
| LinkedIn carousel · nine slides | [PDF](publication/Bergamo_LinkedIn_Carousel_EN_Final.pdf) · [Editable PowerPoint](publication/Bergamo_LinkedIn_Carousel_EN_Final.pptx) |
| Research methods and limitations | [Methodology](docs/research-methodology.md) · [Complete candidate audit](reports/Rental_Listing_Investigation.md) |
| Data and provenance | [Data dictionary](data/rental/data-dictionary.md) · [Source register](data/rental/source-register.csv) · [Primary sample](data/rental/primary-comparable-sample.csv) |
| Reproducibility and release verification | [Instructions](docs/reproducibility.md) · [Release checks](docs/final-release-validation.md) · [Publication manifest](data/publication-manifest.json) |

## What the comparison shows

| Evidence-informed scenario | Annual net cash |
|---|---:|
| Short-term rental (STR) | €6,544.50 |
| Long-term rental (LTR) | €6,677.83 |
| Difference in favour of LTR | €133.33 |

The LTR illustration uses the **unrounded mean** of 14 selected primary comparables: **€894.29 displayed monthly asking rent**, with a **€850 median**. The original €900 monthly-rent scenario remains separate, with €6,732 annual LTR net cash.

These are **conditional model results, not observed city-wide profits**. The small gap does not establish a decisive winner. STR assumes 180 booked nights out of 330 available and €115 gross nightly revenue. Owner-paid cleaning, platform fees, eligible tax and operating allowances reduce gross receipts. LTR assumes 12 paid months. Actual bookings, realised prices, costs, payment continuity and conversion spending can reverse the ranking. Owner time is unpriced; acquisition, financing and professional management are outside base operating cash.

## Analytical work

- Reconciled **96 candidate rows** from 21 historical records, 20 leads and 55 additional advertisements; these are overlapping records, not 96 independent apartments.
- Checked property identity, contract terms and base rent, keeping unresolved cases visible. Strict criteria produced **14 primary** and **11 secondary** comparables; the 20-property primary target was not reached.
- Compared annual and monthly tourism with competing supply and BGY passenger trends, keeping airport movements distinct from local apartment bookings.
- Modelled retained cash, sensitivity and conversion thresholds with shared Python formulas. At €115/night, parity requires **183 booked nights**, or **240** with €15,000 incremental setup recovered over five years.

The research uses a selected convenience sample and combines historical 2024 STR estimates with 2026 asking rents. Asking rents are not signed contracts, tourism totals do not establish apartment occupancy, and the study estimates no causal airport effect. [Full limitations and source reconciliation](docs/research-methodology.md).

## Power BI

[Open the dashboard](powerbi/Bergamo.pbix) to explore the screened rental evidence and a simulator with 12 What-if controls. The imported PBIX can be viewed without refreshing; configure `RepositoryRoot` before a refresh on another machine.

![Power BI executive overview](powerbi/previews/01-overview.png)

[Desktop validation evidence](powerbi/validation/QA.md) records the earlier five-page review and 19 DAX scenarios with 114 checks. Current release checks and any branding-only differences are recorded in the [release notes](docs/final-release-validation.md).

## Reproduce the analysis

Core calculations and tests use Python's standard library:

```sh
python src/analysis.py
python src/airport_analysis.py
python src/rental_market_analysis.py
python -m unittest discover -s tests -v
```

Run generators in a disposable checkout when preserving the frozen release: some scripts write datasets and validation outputs. [Detailed build instructions](docs/reproducibility.md) distinguish generated drafts from the approved published report. No full report builder was run for this release.

The final report retains its numeric citations and references. Source metadata gaps remain disclosed in the [citation review backlog](docs/source-verification-backlog.md); publication does not imply every external source was independently reverified.

[Pedram Kojouri on LinkedIn](https://www.linkedin.com/in/pedram-kojouri/) · Independent Data Analytics Portfolio Project

Source rights and terms apply. No repository-wide reuse licence has been selected.
