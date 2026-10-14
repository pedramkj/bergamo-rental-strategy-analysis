# Rental evidence and reconstruction

Observation and review date: 14 October 2026. Method: **Manual online rental listing review**. This is advertising research, not an in-person survey or a census of properties available today.

## Files and provenance

`../listings.csv` is the immutable historical 21-record snapshot. `candidate-register.csv` preserves all C01–C21 original records, A01–A20 user-supplied preliminary leads, and N identifiers for additional advertisements actually investigated. The A-series prices remain preliminary even after a possible match is found.

`source-observations.csv` is the authoritative transcription of newly reviewed source facts. `deduplication-decisions.csv` contains reviewed identity edges. The analysis derives `master-listing-registry.csv`, `canonical-properties.csv`, the two origin audits and the primary/secondary samples. Do not edit these derived CSVs independently. `source-register.csv` is a compact, regenerated source index. The external indicators live in `market-benchmarks.csv` and never enter the property mean.

## Geographic rule and cohort definition

The selected urban study scope consists of advertisements in Comune di Bergamo carrying the source location label **Centro**, **Sant'Alessandro**, or an explicit **Piazzetta Santo Spirito** location. These are source-defined selection labels. This is a reproducible operational rule, not an official municipal polygon, cadastral zone, postcode or invented radius. San Paolo, Canovine, Borgo Palazzo, Corridoni/Cimitero and Stazione labels alone do not qualify. Conflicting addresses do not qualify. Border properties and alternative portal classifications can change membership; no precise address geocoding was performed. The OMI B2 zone is an independent benchmark, not a claim that every sampled apartment falls inside B2.

Primary: verified source content, entire furnished apartment with two rooms and one bedroom, advertised area 40–65 m² inclusive, explicit 4+4 contract, interpretable monthly base rent, and no unresolved identity/price/feature conflict. A 4+4 branch explicitly offered alongside a transitory branch may qualify; purely transitory, serviced, or unspecified-duration offers do not.

Secondary: same source/geography/furnishing/one-bedroom/base-rent safeguards, area 40–80 m² inclusive, but larger size or annual/free/unspecified ordinary residential duration. Secondary results are descriptive and never pooled into the primary benchmark. Advertising without explicit duration does not prove a conventional signed lease.

## Core fields

| Field | Meaning |
|---|---|
| candidate_id / origin | Input-row identity and original, preliminary or additional source set |
| property_id | Confirmed-merge group with P prefix or provisional unresolved group with U prefix; not a cadastral identifier |
| url / source_urls | Exact advertisement source and all links retained in a confirmed cluster; blank means unrecovered URL |
| recorded_price / recorded_size | Historical or preliminary values, never silently overwritten by later observations |
| status | verified_advertisement = source content checked; historical_index = earlier indexed facts only; unresolved = insufficient accessible evidence; verified_wrong_property = supplied URL resolves to a different offer |
| access_mode / listing_updated | Indexed-page or search-cache evidence and source's own update date where stated |
| observation_date / verification_date | Retrieval and review date, not contract-signing date |
| advertised_monthly_eur | Portal headline or explicitly transcribed advertised amount |
| base_monthly_eur | Separately identified owner rent; blank if an inclusive package cannot be decomposed |
| condominium_monthly_eur | Separately described charge or explicit reimbursement; blank is unknown, not zero |
| utilities / parking / bundled_services | Declared inclusion, optional amenity, or missing information; no inferred market pricing |
| advertised_m2 | Source's advertised area; may be commercial or include weighted accessories |
| price_per_advertised_m2 | Derived base rent divided by advertised_m2 for that record; does not equal an OMI net-area valuation |
| furnished / rooms / bedrooms / floor / contract | Source characteristics and declared duration; conflicting fields generate a review flag |
| duplicate_status / review_flag | Explicit identity or comparability issue; probable edges never trigger automatic merges |
| cohort / exclusion_reason | Reproducible decision with all applicable reasons; reason counts overlap |

An advertisement's accessibility or indexed presence does **not** confirm that the apartment remains available. Some update dates predate the review by months. No advertiser was contacted. Private telephone numbers, email addresses and personal names are omitted. Only short factual summaries are redistributed; original pages remain linked.

## Identity and prices

Exact URL repeats merge input rows. Cross-platform property merges require reviewed agreement in distinctive description, advertiser, floor, area and contract conditions. Shared street or rent alone is insufficient. Probable matches remain separate provisional records and are excluded from comparable cohorts. The total number of physical apartments behind unresolved leads is unknown; canonical record groups are not presented as that number.

Sant'Orsola25 has a confirmed cross-platform match but prices of €850 and €900 conflict. Neither value is chosen for the comparable mean. Borfuro9 and two third-floor Camozzi advertisements remain probable duplicate reviews. The historical Quarenghi32 and Borfuro9 price overlap was not valid duplication evidence: locations and floors differ.

Broseta44 advertises €900 inclusive of utilities and condominium. The claimed €590/€120/€190 split was not found, so base rent remains blank. Pignolo23 explicitly states €850 rent plus €50 reimbursement, €900 total. Its €850 headline already represents base rent; subtracting €50 again would be wrong. Deposits and separately billed condominium/utility charges are not rental income.

## Reproduction and statistical conventions

Run `python src/rental_market_analysis.py` from the repository root. Means use unrounded eligible property rents; model calculations retain full precision. Presentation rounds to cents. Sample standard deviation uses n−1. Quartiles use the inclusive linear interpolation convention in Python's `statistics.quantiles`. Unit-price mean averages individual rent/area ratios rather than dividing aggregate mean rent by aggregate mean area.

The €900 historical model and its inputs are preserved. A separate evidence-informed scenario uses the primary mean and the same financial formulas. It is a conditional illustration for this selected sample, not observed profit or a statistically representative market estimate. Parking and condition differences remain, and asking prices may differ from realised rents.

## Search coverage and stopping rule

All 41 supplied rows were audited. Exact URLs were attempted, missing lead URLs were searched using street, size, rent and platform, and source detail pages were checked where accessible. Three pages of Immobiliare's Centro bilocale results (64 displayed appearances, including repeated advertisements), Idealista's municipal/central and street results, and Subito's municipal results and targeted 4+4 searches were reviewed. Additional direct advertisements actually investigated are retained as N records. Search pages provide discovery, never standalone price verification.

The review exhausted the accessible results of these documented search rounds, not the entire changing internet or all city supply. The target of 20 strict comparables was not reached. Blocked/expired pages, incomplete contracts, conflicting identity, fees and different property characteristics remain explicit; the criteria were not loosened to reach the target. Future accessible sources or agent clarification can expand the cohort.
