# Navy and gold cover assets

`native-cover.docx` is the reviewed, editable one-page Word cover master.
`src/report_cover.py` copies its native DrawingML/VML content, remapping the
single image relationship and drawing IDs. No report-body styles are imported.
The title and supporting text are editable text boxes. Rules, the curved mask,
and the four simple outline icons are native Word vector objects, locked to
page coordinates. Word's Selection Pane can select individual objects.

`approved-reference.png` is the exact 1073 × 1465 image supplied by the user on
16 October 2026. The full raster is embedded unchanged behind an opaque navy
native mask. Only the architectural area is visible; none of its lettering is
used as the report's typography. This avoids bitmap extraction, artificial
resolution enhancement and picture-fill distortion. Deleting the mask would
expose the underlying reference, so retain the mask when editing text.

The reference is supplied artwork, not a verified documentary photograph.
No photographer, landmark verification, license, or invented photo credit is
asserted. No replacement image was obtained. The user authorized its use for
this cover. The image's effective native resolution is approximately 130 ppi
at A4 cover scale: adequate for ordinary screen review, below a 300 ppi print
master. Exporting a larger preview does not add photographic detail.

The cover retains the photo's aspect ratio, using extra navy at the bottom to
fit A4. Its boundary is slightly farther right than the reference to exclude
all original lettering. The reference's faint skyline texture is omitted;
native editorial text, architecture, gold curve, rules and icons form the cover.
Microsoft Word rendering has been verified. Other editors may render floating
shapes or fallback content differently; cross-editor equivalence is untested.

The full analytical report builder was not run in this design task. It has
analytical side effects. Use the existing content-approved report for edits.
