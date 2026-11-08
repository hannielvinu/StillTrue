# StillTrue pitch deck — redesigned

- **StillTrue_Pitch.pptx**: portable submission copy. Rendered slides preserve the exact typography and colors across devices without installing fonts. Speaker notes included.
- **StillTrue_Editable.pptx**: editable native text/vector source. Install bundled fonts before editing to prevent substitutions.
- **StillTrue_Pitch.pdf**: vector PDF reading copy with embedded fonts.
- **Preview.png**: overview of all eight slides.
- **StillTrue_Fonts.zip** / fonts/: custom-named static instances of Space Grotesk SemiBold, Inter and JetBrains Mono, with their licenses.

Design: midnight navy, warm ivory, electric lime, teal and coral; large modern sans-serif headings, concise UI-style labels, real screenshot and visual architecture. Offline fixtures and pending live checks remain labelled.

Regenerate with Python packages python-pptx, reportlab, Pillow and fonttools, plus pdftoppm. Install Brotli only if converting the npm WOFF2 font sources afresh. Run `python docs/presentation/build_pitch.py` from the repository. Already generated static TTFs are reused. Eight-slide speaker notes target three minutes. Before final live submission, update the screenshot and pending-status statements only after running the actual integrations.

Typography update: Space Grotesk SemiBold for titles and key numbers, Inter Regular/SemiBold for body and emphasis, JetBrains Mono for compact technical labels. Space Grotesk was obtained from the Google Fonts repository (ofl/spacegrotesk) and instantiated at weight 600 with a custom family name; its OFL license is bundled.
