from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont("DeckSans", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DeckBold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DeckSerif", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"))
import textwrap
O=Path(__file__).resolve().parent;O.mkdir(exist_ok=True)
R=Presentation();R.slide_width=Inches(13.333);R.slide_height=Inches(7.5)
C=canvas.Canvas(str(O/'StillTrue_Pitch.pdf'),pagesize=(960,540))
C.setTitle('StillTrue — Answers age. Evidence should travel with them.');C.setAuthor('Hanniel Vinu')
BG='F7F4EC';INK='14181F';MUT='4A5160';TEAL='0F5C4D';LINE='DDD7C7';RED='B42318';WHITE='FFFFFF';GOLD='8A5A00'
def color(h):return RGBColor.from_string(h)
def rect(x,y,w,h,fill,line=None):
 s=S.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h));s.fill.solid();s.fill.fore_color.rgb=color(fill);s.line.fill.background() if not line else None
 if line:s.line.color.rgb=color(line)
 C.setFillColor('#'+fill);C.setStrokeColor('#'+(line or fill));C.rect(x*72,540-(y+h)*72,w*72,h*72,fill=1,stroke=bool(line))
 return s
def txt(x,y,w,h,text,size=20,fill=INK,font='Aptos',bold=False):
 s=S.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h));tf=s.text_frame;tf.word_wrap=True;tf.margin_left=tf.margin_right=0;tf.margin_top=tf.margin_bottom=0
 for i,line in enumerate(text.split('\n')):
  p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line;p.font.name=font;p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=color(fill);p.space_after=Pt(3)
 # PDF companion uses portable equivalent fonts, same geometry.
 pdf_font='DeckSerif' if font=='Georgia' else ('DeckBold' if bold else 'DeckSans')
 C.setFont(pdf_font,size);C.setFillColor('#'+fill)
 yy=540-y*72-size*.85
 for line in text.split('\n'):
  for ln in textwrap.wrap(line,width=max(1,int(w*72/(size*.51)))) or ['']:
   C.drawString(x*72,yy,ln.replace('→',' > ').replace('—',' - ').replace('’',"'").replace('•','/'));yy-=size*1.2
 return s
def new(n,kicker,title=None,dark=False):
 global S
 S=R.slides.add_slide(R.slide_layouts[6]);S.background.fill.solid();S.background.fill.fore_color.rgb=color(INK if dark else BG)
 C.setFillColor('#'+(INK if dark else BG));C.rect(0,0,960,540,fill=1,stroke=0)
 txt(.55,.35,9,.25,kicker.upper(),10,'83D6BD' if dark else TEAL,bold=True)
 txt(.55,7.03,10,.25,'STILLTRUE  /  GLOBAL AI HACKATHON  /  HANNIEL VINU',9,'A5ADBB' if dark else MUT)
 txt(12,7.03,.8,.25,f'{n:02d} / 08',9,'A5ADBB' if dark else MUT)
 if title:txt(.55,.92,12,1.35,title,36,WHITE if dark else INK,'Georgia',True)
def end(notes):
 S.notes_slide.notes_text_frame.text=notes
 C.showPage()
def card(x,y,w,num,title,body,accent=TEAL):
 rect(x,y,w,2.15,WHITE);rect(x,y,.045,2.15,accent)
 txt(x+.2,y+.18,w-.4,.3,num,11,accent,bold=True);txt(x+.2,y+.63,w-.4,.55,title,22,INK,'Georgia',True);txt(x+.2,y+1.25,w-.4,.8,body,15,MUT)
new(1,'A second look, before you act',dark=True)
txt(.65,1.1,11,1.2,'StillTrue.',72,WHITE,'Georgia',True)
txt(.7,2.75,11,1.7,'Answers age.\nEvidence should travel with them.',36,'83D6BD','Georgia',True)
txt(.72,5.05,9,.8,'Check whether an AI answer is still true today —\nclaim by claim, against official sources.',21,WHITE)
rect(.72,6.18,5.65,.42,TEAL);txt(.9,6.25,5.4,.25,'BIFROST  +  TAVILY    /    ONE COMBINED PROJECT',11,WHITE,bold=True)
end('0:00–0:20. An AI answer can be helpful when it is written and risky when it is acted on later. StillTrue gives actionable claims a second look. Introduce yourself as Hanniel Vinu. This is one combined Bifrost and Tavily project.')
new(2,'The problem','A confident answer can outlive the rule.')
rect(.6,2.45,7.45,2.65,WHITE)
txt(.9,2.7,6.8,.4,'THE MOMENT THAT MATTERS',11,TEAL,bold=True)
txt(.9,3.25,6.7,1.2,'“Can I still act on this?”',34,INK,'Georgia',True)
txt(.9,4.45,6.8,.35,'An allowance. A filing deadline. An entry requirement.',16,MUT)
txt(8.5,2.5,4.1,.7,'The user is not a researcher.',24,INK,'Georgia',True)
txt(8.5,3.5,4.1,1.6,'They are about to make a decision.\n\nA plausible answer and a list of search links do not resolve freshness.',19,MUT)
txt(.7,5.75,11.8,.6,'OUR WEDGE: verify actionable facts, then expose the evidence and uncertainty.',17,TEAL,bold=True)
end('0:20–0:40. Focus on an ordinary person making a decision. Do not claim measured harm or invented customer research. Our hypothesis is that claim-level evidence is easier to assess than a long answer with generic search links.')
new(3,'The experience','One answer in. A claim-level report out.')
for x,num,title,body in [(.6,'01 / PASTE','Bring the answer','Choose the topic. Common personal identifiers are masked by default.'),(4.72,'02 / CHECK','Find the evidence','Extract actionable claims, search approved domains, read the source.'),(8.84,'03 / DECIDE','See what holds up','Verdicts, copied quotes, retrieval dates and transparent uncertainty.')]:card(x,2.55,3.88,num,title,body)
for x,label,fg,bg in [(.8,'STILL TRUE',TEAL,'E3F3EA'),(4.95,'CHANGED',RED,'FCE9E6'),(9.05,'UNCONFIRMED',GOLD,'FBF1D9')]:
 rect(x,5.3,3.4,.65,bg);txt(x+.15,5.48,3.1,.3,label,15,fg,bold=True)
txt(.8,6.25,11,.4,'A freshness score is a heuristic — not a probability of truth.',15,MUT)
end('0:40–1:00. Explain the three stages and three outcomes. Unconfirmed is an intentional outcome when official evidence is missing or models disagree. Scores are labelled heuristics. PII detection is best-effort, not a privacy guarantee.')
new(4,'Working prototype','Built to make evidence inspectable.')
# Cropped original browser capture; no synthetic screen or invented output.
p=Path(__file__).resolve().parents[1]/'screenshots/check-1280-light.png'
from PIL import Image
im=Image.open(p);ratio=im.height/im.width
pic=S.shapes.add_picture(str(p),Inches(.65),Inches(2.27),width=Inches(7.25))
# crop lower material into a fixed viewport without changing the source image
pic.height=Inches(4.15);pic.crop_bottom=max(0,1-(4.15/(7.25*ratio)))
# PDF crop uses a clipping path and proportional image.
C.saveState();path=C.beginPath();path.rect(.65*72,540-(2.27+4.15)*72,7.25*72,4.15*72);C.clipPath(path,stroke=0,fill=0);C.drawImage(str(p),.65*72,540-2.27*72-7.25*ratio*72,width=7.25*72,height=7.25*ratio*72);C.restoreState()
rect(8.25,2.27,4.45,.57,'FBF1D9');txt(8.4,2.43,4.1,.3,'REAL SCREENSHOT · MOCK DATA',12,GOLD,bold=True)
txt(8.3,3.15,4.2,2.6,'Streaming claim results\n\nQuotes and source provenance\n\nAnnotated original answer\n\nResponsive light / dark modes',18,INK)
txt(8.3,6.15,4.1,.55,'Synthetic fixture results.\nLive provider validation is pending.',12,MUT)
end('1:00–1:25. This is a real screenshot of the running prototype using synthetic offline fixtures, not a real tax verification. The banner stays visible. Show the interface structure, not the illustrative verdict as a factual finding. If credentials later become available, replace this slide with a screenshot from a verified real run and update the label.')
new(5,'Technical architecture','Two technologies. Distinct jobs.')
for x,y,w,h,fill,title,body in [(.65,2.5,2.6,1.1,WHITE,'INPUT + PRIVACY','React / FastAPI / PII masking'),(3.7,2.5,3.75,1.1,'E3F3EA','BIFROST','Claim extraction + model gateway'),(7.95,2.5,4.7,1.1,'E3F3EA','TAVILY','Official-domain search + page extraction'),(7.95,4.3,4.7,1.1,'E3F3EA','BIFROST','Independent evidence verification'),(3.7,4.3,3.75,1.1,WHITE,'DETERMINISTIC GATES','Official source + quote + agreement')]:
 rect(x,y,w,h,fill);txt(x+.18,y+.15,w-.36,.3,title,14,TEAL,bold=True);txt(x+.18,y+.62,w-.36,.4,body,13,MUT)
for x,y,label in [(3.3,2.78,'>'),(7.53,2.78,'>'),(9.9,3.67,'v'),(7.55,4.6,'<'),(3.3,4.6,'<')]:txt(x,y,.4,.4,label,24,TEAL,bold=True)
txt(.8,4.45,2.5,1.2,'SSE results\nback to the user',22,INK,'Georgia',True)
txt(.8,6.05,11.6,.5,'SQLite caches evidence, not pasted answers. Verification still runs on cache hits.',16,MUT)
end('1:25–1:50. Bifrost routes all LLM calls. Tavily retrieves sources, not final verdicts. Independent configured providers judge evidence; deterministic checks gate the answer. Different providers do not prove independent training. Semantic caching is not enabled; SQLite evidence caching is implemented.')
new(6,'Why this approach','Uncertainty is a product feature.')
for y,n,title,body in [(2.35,'01','Official evidence, or no definitive verdict.','Secondary sources can add context; they cannot establish Current or Changed.'),(3.65,'02','A quote must exist in its cited source.','We check quote provenance before accepting a model’s conclusion.'),(4.95,'03','Disagreement stays visible.','Different-provider checks can flag disagreement. A single-model mode is explicitly labelled.')]:
 rect(.65,y,.65,.65,TEAL);txt(.8,y+.18,.4,.3,n,16,WHITE,bold=True);txt(1.6,y,10.6,.5,title,25,INK,'Georgia',True);txt(1.6,y+.62,10.6,.5,body,17,MUT)
end('1:50–2:10. Our differentiator is the policy around evidence and uncertainty, not a claim to eliminate hallucinations. Exact quote matching establishes provenance, not correct interpretation. Official pages can also be stale. Source packs are initially conservative and await activation after network access is available.')
new(7,'Execution evidence','Working software. Measured honestly.')
for x,num,label in [(.75,'17','BACKEND TESTS PASSED'),(4.9,'7','FRONTEND TESTS PASSED'),(9,'12','LAYOUT / THEME RUNS')]:
 txt(x,2.45,3.7,1.15,num,66,TEAL,'Georgia',True);txt(x,3.75,3.7,.4,label,12,MUT,bold=True)
rect(.65,4.6,12,.75,WHITE);txt(.85,4.85,11.6,.4,'PASS  /  Lint · TypeScript · Production build · Docker startup · Dependency audits',16,INK,bold=True)
txt(.8,5.75,11.8,.8,'6 widths × 2 themes; mock runs, keyboard checks and no page errors.\nThese are engineering checks — not live accuracy or benchmark results.',17,MUT)
end('2:10–2:30. These are checks actually run during development. Seventeen backend and seven frontend tests passed. Six viewport widths in both themes completed mock runs. Docker started both services and app health reached Bifrost. No live accuracy metric is claimed, and no remote CI pass is inferred from local tests.')
new(8,'The path forward','A freshness layer wherever AI answers travel.',dark=True)
txt(.75,2.48,5.65,1.4,'Start with people.\nExtend through the API.',31,WHITE,'Georgia',True)
txt(.8,4.3,5.5,1.35,'Personal decisions today.\nResponse annotations for developers next.\nA potential usage-based service to validate.',19,'A5ADBB')
rect(7,2.5,5.55,3.45,'1E242C');txt(7.3,2.8,4.95,.35,'BEFORE LIVE SUBMISSION',12,'83D6BD',bold=True)
txt(7.3,3.45,4.95,1.95,'1  Configure Tavily + provider credentials\n\n2  Activate and review official sources\n\n3  Capture a real demo + label benchmarks',17,WHITE)
txt(.8,6.22,11.8,.4,'github.com/hannielvinu/StillTrue',19,'83D6BD',bold=True)
end('2:30–3:00. Close with the product direction, clearly framed as a hypothesis rather than traction. Current live prerequisites are credentials, accessible source activation, real captures and human benchmark labels. The repository is available for review. Never claim this deck guarantees awards, live accuracy or production readiness.')
R.core_properties.title='StillTrue — Answers age. Evidence should travel with them.';R.core_properties.author='Hanniel Vinu';R.core_properties.subject='Global AI Hackathon — combined Bifrost and Tavily project';R.save(O/'StillTrue_Pitch.pptx');C.save()
print(O/'StillTrue_Pitch.pptx');print(O/'StillTrue_Pitch.pdf')
