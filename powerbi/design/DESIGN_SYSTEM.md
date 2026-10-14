# Bergamo financial research design system

The approved final LinkedIn presentation is the primary visual reference. Its
slide XML supplies the exact RGB values and the dominant Aptos font. The Word
report and its original cover supply complementary gold and ivory accents.
`build_dashboard.py` extracts occurrence counts and source fingerprints into
`design-tokens.json`; it generates the theme from those tokens.

| Token | Exact color | Source / use |
|---|---|---|
| Navy | `#0D233A` | Final slides; editorial masthead, primary type |
| Canvas | `#F6F8FA` | Final slides; light analytical pages |
| Surface | `#FFFFFF` | Final slides; active navigation / controls |
| Blue | `#1C4C74` | Final slides; financial series |
| Teal | `#32B8B2` | Final slides; comparison series |
| Muted | `#64798B` | Final slides; contextual labels |
| Divider | `#DBE5EA` | Final slides; restrained grid / low-emphasis cells |
| Pale teal | `#ADCDD2` | Final slides; secondary text / positive sensitivity |
| Soft teal | `#9CCACD` | Final slides; secondary accents |
| Gold | `#C6A46C` | Approved cover source; baseline marker |
| Ivory | `#F7F5F0` | Approved cover source; documented reference |

## Conflicts resolved explicitly

The cover uses `#101C30` navy and Calibri. The latest carousel uses `#0D233A`
and Aptos; these take precedence for the interactive report. Default Office
theme colors remain in unused presentation theme parts. They are not dashboard
brand tokens. No unrelated palette or newly generated branding is introduced.

## Typography and composition

The source presentation includes 42pt headings, 20.25/21.75pt narrative runs,
11pt small labels and 8/9pt footer runs. The dashboard adapts that hierarchy to
a 1280 × 800 analytical canvas: 27pt page titles, 14/15pt section titles,
11/12pt narrative, 9/10pt metadata and 24/32pt numeric callouts. Source font-size
histograms are preserved in the tokens rather than presented as dashboard sizes.

Use 48px exterior margins, 24px gutters and an 8px alignment rhythm. A navy
masthead and consistent five-page navigation establish the editorial frame.
Financial callouts sit directly on the canvas, without repetitive card borders,
shadows, gradients or oversized pictograms. Native charts and tables carry the
analytical content; explanatory copy stays close to the evidence it qualifies.

Currency measures use two decimal places and negative-value parentheses. Counts
use whole numbers; assumptions retain full numeric precision. Rates use one
decimal percentage formatting. Rent-per-m² uses advertised surface area.

The masthead, active-page state and footer are consistent across pages. Chart
tooltips are enabled. Native source-URL table columns preserve evidence access.
Keyboard tab order follows creation order. Controls use real native slicers,
page-navigation actions and clear-slicer actions, not decorative imitations.

Gold marks the baseline sensitivity cell; financial direction is also conveyed
by signed values, not color alone. The live comparison is a scenario result,
not a statement of market-wide investment returns.
