# Final publication validation — 16 October 2026

[Project overview](../README.md) · [Final PDF](../reports/Bergamo_Rental_Strategy_FINAL_2026.pdf) · [Editable Word](../reports/Bergamo_Rental_Strategy_FINAL_2026.docx)

## Approved report integrity

The approved files were copied without editing, rebuilding or redesigning. SHA-256:

- DOCX: `47ffb7dbf85fe8af8caaab01de0aa6f5bfcc821e4599f7a16a2ab94a4ce47f6b`
- PDF: `0b8d9fd5e4ed7a10fc7b3449969c9db936e6a6e2223b29cbce9cda3877d5d9ec`

Release inspection confirms 33 PDF pages, 14 analytical inline figures and 23 Word tables, including the cover container. The original cover, chapters, references and appendices remain in the exact approved bytes. Previous independent release QA opened the exact Word file read-only in Microsoft Word, checked its saved table-of-contents links and visually reviewed all 33 pages. This publication step does not claim a new editorial review or source revalidation.

The GitHub cover is the actual final PDF's first page rendered with Poppler at 1800 pixels on the long edge. The approved cover master and supplied artwork are preserved as generator dependencies under `assets/report-cover/`.

## Publication cleanup

A local recoverable Git tag and a private tracked-file archive were created before deletion. Uncommitted source work was backed up. Local editorial reviews, intermediate deliveries and unique audit evidence were preserved outside the active checkout; they were not discarded or uploaded as redundant publication files.

Five superseded published exports were removed:

- `reports/Bergamo_Rental_Strategies_Complete_EN_v03.docx`
- `reports/Bergamo_Rental_Strategies_Complete_EN_v03.pdf`
- `reports/Bergamo_Report_Contents_EN.docx`
- `reports/Bergamo_Report_Contents_EN.pdf`
- `reports/Bergamo_Report_Contents_EN.txt`

The separate old contents referred to the obsolete report's pagination and title. The approved final report contains its complete contents. Historical validation records retain their original filenames as audit evidence, not current download links.

README, current download paths, carousel title, caption, Power BI source-priority metadata and publication tests use the final identity. The report generator emits a clearly labelled ignored draft; it was not run. Earlier approved editorial and native-cover source updates are preserved, with their required assets.

## Carousel

Nine slides remain. The only changed PPTX ZIP member is `ppt/slides/slide1.xml`, replacing the second title line with “Why Not More Profit?”. Every other member, including all four native charts and four embedded workbooks, is byte-identical. The PDF was exported from this edited source using Microsoft PowerPoint, then the title slide was rendered and visually inspected. Slide count and all numerical tokens on slides 2–9 were checked against the previous PDF. No analytical content or narrative was rebuilt.

## Power BI

The existing PBIX was opened, its Overview title edited and saved in Power BI Desktop. The PBIP title and generator literal were synchronized. The native five-page PDF export was used to refresh the Overview preview. Binary ZIP comparison found only the Overview textbox definition and `SecurityBindings` changed; `DataModel` and every other existing package entry are byte-identical. Desktop normalised the edited textbox schema/alignment and colour case. No refresh or model change occurred. Existing 19-scenario/114-check Desktop evidence remains preserved, not re-labelled as a new run.

The new Overview export shows a serif fallback despite Aptos remaining specified and registered locally. The cause was not established in this publication task. Other page previews are the previous validated captures. No font definitions changed; this local rendering limitation does not affect the preserved model.

## Automated and link validation

See [machine-readable release checks](../results/final-publication-validation.json). Tests run in a disposable copy because some existing tests regenerate analysis outputs. The actual publication checkout is independently fingerprinted to confirm unchanged data, analytical results, analytical figures and semantic-model definitions. Protected results remain STR €6,544.50, LTR €6,677.83 and a €133.33 LTR advantage; the historical €900 scenario remains €6,732 LTR.

The prior case-sensitive narrative test was updated to accept the approved lower-case “manual online rental listing review”; its substantive requirement remains. A release-manifest hash check was added. Local Markdown/image paths and the publication checkout's research fingerprints are checked separately. External source availability is not equated with source validity; the [source metadata backlog](source-verification-backlog.md) remains disclosed.
