# Build notes and verification

## Scope

This new deck follows the supplied brief: eight main slides and two Backup slides; native editable text, shapes, connectors, logical XML reading order, descriptive alt text, citations, full notes and a timed speaker script. It supersedes the older eight-slide design under docs/presentation for the new brief. No benchmark percentages, screenshots, recording, team name or capture dates have been invented.

## Fonts and color

Fraunces weight 650 (custom family StillTrue Editorial) is used for headings; Inter for body; JetBrains Mono for evidence/figures. Static instances and licenses are included in fonts/. They must be installed to reproduce native PowerPoint typography on a new device. The PDF embeds the same fonts. Source WOFF2 Latin subsets lacked rupee/approximation glyphs. Full Google Fonts Inter and JetBrains Mono sources were used for the static instances; currency figures fall back to Inter because JetBrains Mono still lacks the rupee glyph. No silent missing-glyph substitution is intended. Fonts and sources are openly licensed, not purchased.

Warm paper, ink, teal and status colors match the requested design. The builder checks all recorded text/background pairs: minimum measured contrast 4.65:1. Body text is at least 20pt, source/labels at least 10pt. Word counts exclude diagrams and source footers as requested. The title wordmark and numeric pull elements are larger by design.

## Facts and placeholders

External facts come from the user-supplied fact base and are attributed in slide footers and full URLs in notes. They were not independently re-opened: active network policy denies those hosts. The tax anecdote remains a reported case; no assessment year is asserted. Air Canada is explicitly a fabrication case, not stale information. Competitor listings are marked not tested by us. Sponsor feature status starts planned in author_status.yaml; no new author verification is inferred from fixture tests.

ASSETS_NEEDED.md maps every missing asset to its frame. quality_report.json records all rendered placeholders. Benchmark chart code reads the actual benchmark/results schema when reports are present and refuses mock reports. No results file exists now, so the chart remains a placeholder. Team membership and registration must be confirmed by the entrant.

## Export limitation

LibreOffice is not installed. The system package helper and sudo are unavailable to the current user, so no privileged package installation was attempted. The PDF was rendered using ReportLab with the same font files, measured line breaks and geometry as the native PPTX. This differs from the brief's requested LibreOffice export; it is not represented as that export. Native editable content is preserved in the PPTX; there are no slide-sized rasterized images.

## Checks

- Builder: exactly 10 slides, source notes, body/label font thresholds, contrast, word counts, shape bounds and placeholder checklist passed.
- PDF was rendered using pdftoppm and each slide inspected; currency glyph issues found during inspection were corrected.
- Notes include timings, point, judging criterion, exact script, sources and transitions.
- Main timings total 280 seconds (4:40). The script explains the additional cuts needed for 3:00; shortening only S3 and S8 cannot save 100 seconds.
- Digits are limited to supplied fact values, event year, structural slide/flow numbers, planned next-30-day label and the diagram's model labels. No measured accuracy, first-place prediction or invented current-data claim is included.

## Regeneration

Use Python packages python-pptx, PyYAML, reportlab, Pillow and fonttools; run `python deck/build_deck.py`. Static font files are already committed. Review the rendered output before presenting. Update real assets and author_status.yaml only after actual verification; do not turn placeholders into claims just to make the deck look finished.
