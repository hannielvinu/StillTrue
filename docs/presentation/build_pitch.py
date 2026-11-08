from pathlib import Path
from io import BytesIO
from math import sin,cos,pi
from PIL import Image
from fontTools.ttLib import TTFont as Font
from fontTools.varLib.instancer import instantiateVariableFont
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/presentation';FD=OUT/'fonts';FD.mkdir(exist_ok=True)
for source,weight,name in [('fraunces',650,'StillTrue Display'),('inter',400,'StillTrue Sans'),('inter',650,'StillTrue Sans Bold'),('jetbrains-mono',450,'StillTrue Mono')]:
    dest=FD/(name.replace(' ','-')+'.ttf')
    if not dest.exists():
        folder=ROOT/'frontend/node_modules/@fontsource-variable'/source
        f=Font(folder/'files'/f'{source}-latin-wght-normal.woff2')
        axes={a.axisTag:(weight if a.axisTag=='wght' else a.defaultValue) for a in f['fvar'].axes}
        f=instantiateVariableFont(f,axes,inplace=True);f.flavor=None
        for id,value in [(1,name),(2,'Regular'),(4,name),(6,name.replace(' ','')),(16,name),(17,'Regular')]:
            for r in list(f['name'].names):
                if r.nameID==id:f['name'].setName(value,id,r.platformID,r.platEncID,r.langID)
        f.save(dest)
        licensefile=folder/'LICENSE'
        if licensefile.exists():(FD/f'{source}-LICENSE.txt').write_text(licensefile.read_text())
    pdfmetrics.registerFont(TTFont(name,str(dest)))
DISPLAY='StillTrue Display';SANS='StillTrue Sans';BOLD='StillTrue Sans Bold';MONO='StillTrue Mono'
NAVY='101F2C';CREAM='F5F3EB';LIME='C5F66B';TEAL='116D60';CORAL='F98A70';WHITE='FFFFFF';GREY='566571';MIST='DCE6DF';MUTED='A4B6BF';PANEL='1B303E'
R=Presentation();R.slide_width=Inches(13.333333);R.slide_height=Inches(7.5)
C=canvas.Canvas(str(OUT/'StillTrue_Pitch.pdf'),pagesize=(960,540));C.setTitle('StillTrue | Before you act, check the answer.');C.setAuthor('Hanniel Vinu')
previews=[]
def rc(v):return RGBColor.from_string(v)
def box(x,y,w,h,fill,stroke=None,r=0):
    shape=S.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if r else MSO_SHAPE.RECTANGLE,Inches(x/72),Inches(y/72),Inches(w/72),Inches(h/72))
    if r:
        try:shape.adjustments[0]=.12
        except Exception:pass
    shape.fill.solid();shape.fill.fore_color.rgb=rc(fill)
    if stroke:shape.line.color.rgb=rc(stroke);shape.line.width=Pt(1)
    else:shape.line.fill.background()
    C.setFillColor('#'+fill);C.setStrokeColor('#'+(stroke or fill));C.roundRect(x,540-y-h,w,h,r,fill=1,stroke=bool(stroke)) if r else C.rect(x,540-y-h,w,h,fill=1,stroke=bool(stroke))
    return shape

def line(x1,y1,x2,y2,col,width=1):
    sh=S.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1/72), Inches(y1/72), Inches(x2/72), Inches(y2/72));sh.line.color.rgb=rc(col);sh.line.width=Pt(width)
    C.setStrokeColor('#'+col);C.setLineWidth(width);C.line(x1,540-y1,x2,540-y2)

def circle(x,y,r,fill,stroke=None,width=1):
    sh=S.shapes.add_shape(MSO_SHAPE.OVAL, Inches((x-r)/72),Inches((y-r)/72),Inches(2*r/72),Inches(2*r/72))
    if fill:sh.fill.solid();sh.fill.fore_color.rgb=rc(fill)
    else:sh.fill.background()
    if stroke:sh.line.color.rgb=rc(stroke);sh.line.width=Pt(width)
    else:sh.line.fill.background()
    C.setFillColor('#'+(fill or NAVY));C.setStrokeColor('#'+(stroke or fill or NAVY));C.setLineWidth(width);C.circle(x,540-y,r,fill=bool(fill),stroke=bool(stroke))

def wrap(text,font,size,w):
    output=[]
    for para in text.split('\n'):
        words=para.split();cur=''
        if not words:output.append('');continue
        for word in words:
            trial=(cur+' '+word).strip()
            if cur and pdfmetrics.stringWidth(trial,font,size)>w:output.append(cur);cur=word
            else:cur=trial
        output.append(cur)
    return output

def text(x,y,w,content,size=18,col=NAVY,font=SANS,leading=None):
    leading=leading or size*1.2
    lines=wrap(content,font,size,w)
    height=leading*len(lines)+5
    sh=S.shapes.add_textbox(Inches(x/72),Inches(y/72),Inches(w/72),Inches(height/72));tf=sh.text_frame;tf.word_wrap=False;tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
    for i,ln in enumerate(lines):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=ln;p.font.name=font;p.font.size=Pt(size);p.font.color.rgb=rc(col);p.line_spacing=Pt(leading);p.space_before=Pt(0);p.space_after=Pt(0)
    C.setFont(font,size);C.setFillColor('#'+col)
    for i,ln in enumerate(lines):C.drawString(x,540-y-size*.88-i*leading,ln)
    if y+height>493:raise ValueError(('Text exceeds safe area',content,y,height))
    return height

def pill(x,y,w,label,fill=LIME,col=NAVY):
    box(x,y,w,27,fill,r=13);text(x+12,y+7,w-20,label,10,col,BOLD)

def clock(x,y,r,col=LIME):
    circle(x,y,r,None,col,2)
    for i in range(12):
        a=i*pi/6
        line(x+cos(a)*(r-6),y+sin(a)*(r-6),x+cos(a)*(r-11),y+sin(a)*(r-11),col,1)
    line(x,y,x,y-r*.53,col,3);line(x,y,x+r*.38,y+r*.18,col,3);circle(x,y,4,col)

def check(x,y,col=LIME):line(x,y,x+6,y+6,col,2);line(x+6,y+6,x+17,y-7,col,2)

def new(n,label,bg=CREAM):
    global S
    S=R.slides.add_slide(R.slide_layouts[6]);S.background.fill.solid();S.background.fill.fore_color.rgb=rc(bg)
    C.setFillColor('#'+bg);C.rect(0,0,960,540,fill=1,stroke=0)
    dark=bg in [NAVY,TEAL];fg=LIME if dark else TEAL
    text(42,25,700,'STILLTRUE   /   '+label.upper(),10,fg,MONO)
    # footer, custom helper to keep outside content bounds
    for x,w,s in [(42,700,'HANNIEL VINU  ·  GLOBAL AI HACKATHON 2026'),(865,60,f'{n:02d} / 08')]:
        sh=S.shapes.add_textbox(Inches(x/72),Inches(510/72),Inches(w/72),Inches(16/72));p=sh.text_frame.paragraphs[0];p.text=s;p.font.name=MONO;p.font.size=Pt(8);p.font.color.rgb=rc(MUTED if dark else GREY)
        C.setFont(MONO,8);C.setFillColor('#'+(MUTED if dark else GREY));C.drawString(x,22,s)
    line(42,498,918,498,PANEL if dark else 'D7DDD4',.6)

def end(note):S.notes_slide.notes_text_frame.text=note;C.showPage()

def photo(path,x,y,w,h,left=0,top=0,right=0,bottom=0):
    p=S.shapes.add_picture(str(path),Inches(x/72),Inches(y/72),width=Inches(w/72),height=Inches(h/72));p.crop_left=left;p.crop_top=top;p.crop_right=right;p.crop_bottom=bottom
    # Match the PowerPoint image viewport in the PDF companion.
    im=Image.open(path);iw,ih=im.size;im=im.crop((int(left*iw),int(top*ih),int((1-right)*iw),int((1-bottom)*ih)))
    C.drawImage(ImageReader(im),x,540-y-h,width=w,height=h)

new(1,'Before you act',NAVY)
pill(44,80,228,'AI ANSWERS HAVE A SHELF LIFE.')
text(40,135,590,'StillTrue.',91,CREAM,DISPLAY)
text(44,258,540,'Answers age.\nEvidence should travel\nwith them.',35,CREAM,DISPLAY,41)
text(46,413,470,'Claim-level freshness checks.\nOfficial sources. Visible uncertainty.',17,MUTED)
# Graphic: time at the centre, three outcomes around it.
clock(760,249,99,LIME);circle(760,249,123,None,PANEL,1)
for x,y,w,t,c in [(621,87,175,'STILL TRUE',LIME),(738,386,174,'! CHANGED',CORAL),(600,342,202,'? UNCONFIRMED','E1D8B6')]:
    box(x,y,w,42,c,r=11);text(x+16,y+13,w-24,t,12,NAVY,BOLD)
text(652,455,260,'BIFROST  ×  TAVILY',12,LIME,MONO)
end('0:00–0:20. Introduce Hanniel Vinu and StillTrue: before acting on an AI answer, check whether its actionable claims remain current. This is one combined project. No guarantee of accuracy or awards is implied.')

new(2,'The problem')
text(44,82,700,'A confident answer can\noutlive the rule.',43,NAVY,DISPLAY,48)
text(46,202,780,'The person reading it is about to make a decision.',19,GREY)
box(44,263,540,175,NAVY,r=15);text(68,282,480,'THE QUESTION BEHIND THE QUESTION',10,LIME,MONO)
text(68,322,480,'“Can I still\nact on this?”',37,CREAM,DISPLAY,42)
for y,num,title,body in [(269,'01','Money','Thresholds, rates, allowances'),(335,'02','Paperwork','Eligibility, fees, deadlines'),(401,'03','Software','Versions and deprecations')]:
    text(622,y,38,num,11,TEAL,MONO);text(671,y-4,235,title,20,NAVY,BOLD);text(671,y+24,240,body,12,GREY)
end('0:20–0:40. Our core persona is an ordinary person about to act on an AI answer. These are motivating scenarios, not measured user research. Generic links may leave them to determine which rule and year applies.')

new(3,'The product promise',TEAL)
text(44,82,800,'One answer in.\nA clear report out.',43,CREAM,DISPLAY,48)
for x,num,title,body in [(44,'01','Paste','Bring the answer. Choose a topic. Mask common personal details.'),(343,'02','Check','Extract actionable claims. Retrieve and read official evidence.'),(642,'03','Decide','Inspect the verdict, copied quote, source and retrieval time.')]:
    box(x,224,274,186,CREAM,r=13);text(x+22,244,220,num,13,TEAL,MONO);text(x+22,279,230,title,31,NAVY,DISPLAY);text(x+22,328,227,body,15,GREY)
for x,w,label,fill in [(44,210,'STILL TRUE',LIME),(343,210,'! CHANGED',CORAL),(642,245,'? UNCONFIRMED','E1D8B6')]:pill(x,439,w,label,fill)
end('0:40–1:00. Three outcomes are intentional. Unconfirmed means the evidence or agreement is insufficient; it is not a failure hidden from the user. Personal-data masking is best-effort. Scores are heuristics, not calibrated probabilities.')

new(4,'Prototype / real browser capture',NAVY)
text(44,82,870,'Evidence you can actually inspect.',36,CREAM,DISPLAY)
text(46,145,690,'A working interface. A visible boundary between demo and live evidence.',15,MUTED)
# Screenshot viewport with explicit source label; crop preserves screenshot aspect ratio.
shot=ROOT/'docs/screenshots/check-1280-light.png'
box(42,196,608,270,'273D4C',r=13)
photo(shot,52,222,588,234,left=0,top=.235,right=0,bottom=.488)
circle(63,209,3,CORAL);circle(74,209,3,'E1D8B6');circle(85,209,3,LIME)
text(105,202,490,'StillTrue / freshness report',9,CREAM,MONO)
pill(678,198,236,'REAL SCREENSHOT · MOCK DATA','E1D8B6')
for y,label,body in [(253,'01 / STREAM','Claim results as checks finish'),(323,'02 / INSPECT','Source, quote and uncertainty'),(393,'03 / REVIEW','Original answer stays visible')]:
    text(682,y,230,label,11,LIME,MONO);text(682,y+24,230,body,16,CREAM)
end('1:00–1:25. This is a real screenshot of the actual prototype with synthetic fixtures. It is not proof of a tax rule, nor a real captured model error. The slide explicitly labels mock data. Source activation and credentialed API checks remain pending. Walk through the input and result structure.')

new(5,'Architecture')
text(44,82,870,'Two technologies. Distinct jobs.',38,NAVY,DISPLAY)
text(46,143,850,'Bifrost handles models. Tavily finds evidence. Code enforces the verdict rules.',16,GREY)
# A snake flow: every node labelled, with arrows between rows.
nodes=[(44,210,'01','INPUT','React + FastAPI\nPII masking',NAVY,CREAM),(343,210,'02','BIFROST','Extract actionable\nclaims',TEAL,CREAM),(642,210,'03','TAVILY','Search official sources\nExtract page evidence',TEAL,CREAM),(642,358,'04','BIFROST','Independent model\nverification',TEAL,CREAM),(343,358,'05','TRUST GATES','Official source + quote\nModel agreement',NAVY,CREAM),(44,358,'06','REPORT','Stream claim results\nCache evidence in SQLite',NAVY,CREAM)]
for x,y,num,title,body,bg,fg in nodes:
    box(x,y,274,112,bg,r=12);text(x+18,y+13,25,num,10,LIME,MONO);text(x+53,y+12,199,title,13,fg,BOLD);text(x+18,y+49,238,body,15,fg)
for x,y,dx,dy in [(322,263,17,0),(621,263,17,0),(779,327,0,23),(638,411,-17,0),(339,411,-17,0)]:
    ex,ey=x+dx,y+dy
    line(x,y,ex,ey,TEAL,2)
    if dx:
        sign=1 if dx>0 else -1
        line(ex,ey,ex-sign*5,ey-4,TEAL,2);line(ex,ey,ex-sign*5,ey+4,TEAL,2)
    else:
        line(ex,ey,ex-4,ey-5,TEAL,2);line(ex,ey,ex+4,ey-5,TEAL,2)
end('1:25–1:50. All LLM calls go through Bifrost. Tavily supplies evidence, not the final verdict. Verification uses two different providers when configured; single-model mode is honest and explicit. The app cache stores evidence and judging still runs on cache hits. Semantic caching is disabled.')

new(6,'The differentiator')
text(44,82,830,'Uncertainty is\na product feature.',43,NAVY,DISPLAY,48)
text(668,100,226,'A false “Current”\nis worse than\n“Couldn’t confirm.”',22,TEAL,DISPLAY)
for x,num,title,body in [(44,'01','Authority first.','No approved official source? No definitive verdict.'),(343,'02','Show the quote.','A copied quote must exist in the cited official evidence.'),(642,'03','Disagreement.','If independent checks disagree, the claim stays Unconfirmed.')]:
    box(x,255,274,198,WHITE,r=14);circle(x+35,290,15,TEAL);text(x+27,281,30,num,11,CREAM,MONO);text(x+22,326,230,title,23,NAVY,DISPLAY);text(x+22,370,229,body,16,GREY)
end('1:50–2:10. The differentiator is a transparent policy, not a claim to eliminate hallucinations. Exact quotation proves provenance, not semantic correctness. Official sources can lag policy; models can agree on errors. Prefer uncertainty rather than unsupported confidence.')

new(7,'Engineering evidence',NAVY)
text(44,82,850,'Built. Tested.\nClearly bounded.',43,CREAM,DISPLAY,48)
for x,n,lab in [(46,'17','BACKEND TESTS'),(346,'7','FRONTEND TESTS'),(646,'12','LAYOUT / THEME RUNS')]:
    text(x,231,240,n,81,LIME,DISPLAY);text(x+3,331,255,lab+' PASSED',11,CREAM,MONO)
box(44,380,872,52,PANEL,r=11);check(62,406);text(92,397,800,'Lint  /  TypeScript  /  Production build  /  Docker startup  /  Dependency audits',13,CREAM,BOLD)
text(46,454,850,'Local engineering checks. Live verification accuracy and benchmark results: not yet measured.',12,MUTED)
end('2:10–2:30. These results were actually observed in the build session: seventeen backend tests, seven frontend tests and twelve responsive/theme mock runs. Docker app health reached Bifrost. Dependency audits reported no known vulnerabilities for the installed packages. These are not live accuracy results or a claim that remote CI passed.')

new(8,'What comes next',TEAL)
text(44,82,850,'Before you act,\ncheck the answer.',51,CREAM,DISPLAY,55)
text(46,229,450,'For people making decisions.\nFor developers shipping AI answers.',20,CREAM)
box(559,226,357,218,CREAM,r=16);text(582,247,305,'THE NEXT LIVE MILESTONE',10,TEAL,MONO)
for y,num,body in [(286,'01','Configure Tavily + model credentials'),(335,'02','Activate and review official sources'),(384,'03','Capture a real demo; label benchmarks')]:
    text(582,y,27,num,11,TEAL,MONO);text(620,y-3,269,body,15,NAVY)
pill(46,344,255,'ONE ENGINE. WEB + DEVELOPER API.')
text(46,402,430,'Start with actionable claims.\nExpand source coverage with evidence.',17,CREAM)
text(46,466,850,'github.com/hannielvinu/StillTrue',13,LIME,MONO)
end('2:30–3:00. Close on the value: a freshness layer for people and developers. The API exists; usage-based commercialization is a future hypothesis, not traction. Be explicit that real credentials, source activation, captured evidence and human-labelled benchmarks are prerequisites for a live submission. Invite judges to inspect the repository.')
R.core_properties.title='StillTrue | Before you act, check the answer.';R.core_properties.author='Hanniel Vinu';R.save(OUT/'StillTrue_Editable.pptx');C.save()
print('Created redesigned PPTX and PDF with eight slides and notes')

# Portable submission copy: full-slide renders preserve typography on judge devices.
# Editable native text and vector shapes remain available in StillTrue_Editable.pptx.
import tempfile
import subprocess
import os
with tempfile.TemporaryDirectory(prefix="stilltrue-deck-") as folder:
    env=dict(os.environ)
    env["XDG_CACHE_HOME"]=folder
    subprocess.run(["pdftoppm", "-scale-to", "1920", "-png", str(OUT/"StillTrue_Pitch.pdf"), folder+"/slide"],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,env=env)
    portable=Presentation()
    portable.slide_width=R.slide_width
    portable.slide_height=R.slide_height
    for source,image in zip(R.slides,sorted(Path(folder).glob("slide-*.png")),strict=True):
        target=portable.slides.add_slide(portable.slide_layouts[6])
        target.shapes.add_picture(str(image),0,0,width=portable.slide_width,height=portable.slide_height)
        target.notes_slide.notes_text_frame.text=source.notes_slide.notes_text_frame.text
    portable.core_properties.title=R.core_properties.title
    portable.core_properties.author="Hanniel Vinu"
    portable.save(OUT/"StillTrue_Pitch.pptx")
print("Portable submission deck and editable original saved")
