# StillTrue pitch deck

Upload **StillTrue_Pitch.pptx** to the hackathon PPT field. Eight editable 16:9 slides include three-minute speaker notes. StillTrue_Pitch.pdf is a portable reading copy with equivalent fonts. Mock screenshots and outstanding live checks are explicitly labelled.

To regenerate: install python-pptx, reportlab and Pillow in a local Python environment, then run `python docs/presentation/build_pitch.py`. The PDF renderer uses the DejaVu fonts at standard Linux paths; adjust paths on other systems. The PowerPoint uses Georgia and Aptos and may substitute fonts on systems without them. Review in PowerPoint before presenting. Before a final live submission, replace the offline screenshot and pending-status statements only after real validation has completed.
