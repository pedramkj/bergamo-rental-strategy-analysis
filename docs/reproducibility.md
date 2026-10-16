# Reproducibility and publication boundaries

[Project overview](../README.md) · [Approved report](../reports/Bergamo_Rental_Strategy_FINAL_2026.pdf)

## Calculations

From the repository root, with Python 3:

```sh
python src/analysis.py
python src/airport_analysis.py
python src/rental_market_analysis.py
python -m unittest discover -s tests -v
```

The computations and unit tests use the standard library. Some tests run generators that write canonical analysis outputs: use a disposable checkout to validate a frozen release. The release validation follows this approach and separately fingerprints the publication checkout.

`src/financial_model.py` owns the shared financial formulas. `src/rental_market_analysis.py` owns cohort statistics and the separate sample-mean scenario. The full-precision primary mean (12520 / 14) is used in calculations; €894.29 is display rounding. Historical assumptions and the €900 case remain separate.

## Generated Word drafts and figures

```sh
python -m pip install -r requirements.txt
python src/rental_figures.py
python src/build_report.py
```

The report builder writes `generated/report/Bergamo_Rental_Strategies_Generated_Draft.docx` and related draft contents. It also invokes analytical generators; do not run it over a frozen release without reviewing those side effects. Drafts are ignored by Git. The builder does not export PDFs; native Word field/pagination checks and PDF export are separate steps.

The approved release is `reports/Bergamo_Rental_Strategy_FINAL_2026.docx` and its corresponding PDF. These were copied byte for byte from the approved final delivery and were not regenerated. Source literals include earlier approved editorial work but do not establish byte-for-byte reproduction of the manually reviewed final file. Do not replace the approved report with a generated draft.

`src/report_cover.py` uses the editable native Word cover master and supplied artwork in [assets/report-cover](../assets/report-cover/README.md). The GitHub cover is a raster extraction of the actual approved PDF page 1, not the older schematic artwork. Historical schematic files remain because source history and earlier workflows may refer to them.

## Frozen inputs and provenance

The [publication manifest](../data/publication-manifest.json) retains all existing research fingerprints and adds approved release hashes. Do not update research fingerprints without reviewing dependent narrative and outputs. Historical reconstruction records such as `results/reconstruction-validation.json` retain original filenames as evidence of that earlier validation; they are not current download links.

See [research methodology](research-methodology.md), [data dictionary](../data/rental/data-dictionary.md), [source register](../data/rental/source-register.csv) and [Power BI setup](../powerbi/README.md).
