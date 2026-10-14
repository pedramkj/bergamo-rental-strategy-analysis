# Power BI acceptance record

Review: 14 October 2026. Research baseline: f53e659a98b110904498613ff4b5e8beabfa212d.

## What was actually executed

Power BI Desktop 2.158.1304.0 opened the PBIP, imported all 25 tables and rendered
all five pages. A genuine PBIX was saved with Desktop's native Save As, reopened,
and its imported model passed the same 19 Python-reference cases / 114 checks.
The public PBIX retains its evidence cache with a documented portable source
parameter. No cloud workspace or publishing subscription was required.

`desktop-dax-validation.json` records actual ADOMD query results against the
Desktop local engine, not a DAX-text parser or a Python imitation. Numerical
tolerance is 0.000001. Cases cover each of the 12 inputs, historical €900 rent,
combined changes, zero bookings, zero paid months and negative contribution.

## Native interactions observed

- Simulator ADR selection: €115 → €50. STR cash became −€885.00, LTR stayed
  €6,677.83, difference became −€7,562.83 and required nights became 824. The
  model deliberately displays an unreachable threshold rather than claiming it
  is achievable within 330 offered nights. Reset restored base calculations.
- Masthead Rental Market action activated with Ctrl+Enter and navigated correctly.
- Neighborhood filter Piazzetta Santo Spirito returned one property, €850 rent,
  €850 median and €13.08 per advertised m². Clear filters restored 14 properties,
  €894.29 mean, €850 median and €17.22 per advertised m².
- Native page tabs and the five-page screenshot pass also reached every page.
  Navigation targets on every page are covered by source regression checks.

This is representative interaction testing, not an exhaustive accessibility or
all-combinations UI certification. Mathematical parameter coverage is broader
than the sampled native interaction paths.

## Visual review and repairs

Actual Desktop captures in `../previews/` were individually inspected. The final
pass checked typeface, hierarchy, clipping, currency precision, alignment and
chart interpretation. It corrected a missing local Aptos font, unique native
query references in the risk matrix, histogram order, clipped neighborhood labels,
scatter margins, categorical year/cost/preparation axes and table row spacing.
All nine sensitivity cells rendered with live measure values and conditional
fills; the final pages showed no error visuals.

The narrow right-side Filters strip belongs to Power BI Desktop. Previews are
supporting native captures. No HTML, generated bitmap dashboard or hand-drawn
chart substitutes for the actual report.

## Reproducibility and limits

`schema-validation.json` records public Microsoft JSON schema results; official
Microsoft authoring CLI validation also returned zero errors and zero warnings.
The repository unit suite passed all 50 tests, including five new Power BI
invariants. Source/data/model/research-output hashes were compared with the
baseline: only the dashboard, documentation, ignore rules and dashboard tests
were added/changed.

The 14-property sample is a selected comparable cohort, not a probability sample
of Bergamo. Asking prices are not executed rents. Airport movements are not
apartment reservations. Scenario inputs are not observed apartment occupancy.
The €500 narrow-gap band is display logic, not a researched investment criterion.
Cleaning remains owner-paid; there is no owner-time deduction.

Aptos must be available locally for exact typography. Fonts, local model caches,
SDK packages and authoring-tool installations are not redistributed. Remote
browser/Power BI Service deployment was not tested or claimed. No research
findings or technical authorship claims were changed.
