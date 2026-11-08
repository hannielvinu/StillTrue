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

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'deck';FD=OUT/'fonts';FD.mkdir(exist_ok=True)
for source,weight,name in [('space-grotesk',600,'StillTrue Grotesk'),('inter',400,'StillTrue Sans'),('inter',650,'StillTrue Sans Bold'),('jetbrains-mono',450,'StillTrue Mono')]:
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
DISPLAY='StillTrue Grotesk';SANS='StillTrue Sans';BOLD='StillTrue Sans Bold';MONO='StillTrue Mono'
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


# This deck is native/editable. The companion PDF shares fonts and measured line breaks.
import json
import yaml
from datetime import datetime
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
DATA=yaml.safe_load((OUT/'content.yaml').read_text())
STATUS=yaml.safe_load((OUT/'author_status.yaml').read_text())
pdfmetrics.registerFont(TTFont('StillTrue Editorial',str(FD/'StillTrue-Editorial.ttf')))
DISPLAY='StillTrue Editorial'
NAVY='14181F';CREAM='F7F4EC';TEAL='0F5C4D';GREY='4A5160';WHITE='FFFFFF'
STYLES=[];PLACEHOLDERS=[];BODY_COUNTS={};BOXES=[]

def contrast(a,b):
    def lum(s):
        c=[int(s[i:i+2],16)/255 for i in (0,2,4)]
        return sum((v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4)*w for v,w in zip(c,[.2126,.7152,.0722]))
    x,y=lum(a),lum(b)
    return (max(x,y)+.05)/(min(x,y)+.05)

_original_box=box

def B(x,y,w,h,fill=WHITE,stroke=None,r=0):
    BOXES.append((x,y,w,h,fill))
    return _original_box(x,y,w,h,fill,stroke,r)

def T(x,y,w,content,size=20,col=NAVY,font=SANS,role='body',leading=None):
    if '₹' in content and font==MONO:font=SANS  # Currency glyph fallback, documented in NOTES.md.
    # Measure the background behind this native text for contrast checks.
    bg=CREAM
    for bx,by,bw,bh,fill in BOXES:
        if bx<=x<=bx+bw and by<=y<=by+bh:bg=fill
    STYLES.append({'slide':ID,'text':content,'size':size,'role':role,'contrast':round(contrast(col,bg),2)})
    if role=='body':BODY_COUNTS[ID]+=len(content.split())
    return text(x,y,w,content,size,col,font,leading)

def common(index):
    global S,ID,BOXES
    row=DATA['slides'][index];ID=row['id'];BODY_COUNTS[ID]=0;BOXES=[]
    S=R.slides.add_slide(R.slide_layouts[6]);S.background.fill.solid();S.background.fill.fore_color.rgb=rc(CREAM)
    C.setFillColor('#'+CREAM);C.rect(0,0,960,540,fill=1,stroke=0)
    T(44,23,790,'STILLTRUE / '+('BACKUP' if index>=8 else 'GLOBAL AI HACKATHON 2026'),10,TEAL,MONO,'label')
    B(44,52,872,2,TEAL)
    if index:
        T(44,73,870,row['title'],36,NAVY,DISPLAY,'title',40)
    # Native footer with stable reading order and source line.
    sources='; '.join(DATA['sources'][key]['name'] for key in row['sources'])
    T(44,474,872,'Source: '+sources,10,GREY,SANS,'source',11)
    for x,w,content in [(44,740,'StillTrue · Global AI Hackathon 2026'),(840,90,ID+(' · Backup' if index>=8 else ' / 08'))]:
        sh=S.shapes.add_textbox(Inches(x/72),Inches(509/72),Inches(w/72),Inches(16/72))
        tf=sh.text_frame;tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
        q=tf.paragraphs[0];q.text=content;q.font.name=SANS;q.font.size=Pt(10);q.font.color.rgb=rc(GREY)
        C.setFont(SANS,10);C.setFillColor('#'+GREY);C.drawString(x,22,content)
    return row

def placeholder(x,y,w,h,description,asset):
    sh=B(x,y,w,h,CREAM,TEAL,8);sh.line.dash_style=MSO_LINE_DASH_STYLE.DASH
    C.saveState();C.setDash(5,4);C.setStrokeColor('#'+TEAL);C.roundRect(x,540-y-h,w,h,8,fill=0,stroke=1);C.restoreState()
    T(x+14,y+(8 if h<60 else 15),w-28,'INSERT REAL: '+description,20,TEAL,SANS,'placeholder',24)
    PLACEHOLDERS.append({'slide':ID,'description':description,'asset':asset})

def finish(row):
    urls='\n'.join(DATA['sources'][k]['url'] for k in row['sources'])
    S.notes_slide.notes_text_frame.text=(f"Timing: {row['seconds']} seconds. Event time limit is unknown.\nPoint: {row['body']}\nJudging criterion: {row['criterion']}\n\nScript: {row['script']}\n\nSources (provided in the author brief; not independently re-opened here):\n{urls}\n\nTransition: "+row.get('transition','We will now move to the next part of the story.'))
    # Set descriptive alt text on pictures and diagram shapes; XML order is reading order.
    for shape in S.shapes:
        props=shape._element.xpath('.//p:cNvPr')
        if props:
            description=shape.text if shape.has_text_frame and shape.text else f"{ID}: diagram or decorative frame supporting {row['title']}"
            props[0].set('descr',description)
    C.showPage()

row=common(0)
T(44,89,870,'StillTrue',64,NAVY,DISPLAY,'title')
T(46,190,840,DATA['slides'][0]['body'],26,NAVY,SANS,'body',33)
T(46,279,850,DATA['event'],20,TEAL,SANS,'body')
for x,label,fg,bg,symbol in [(44,'Still true','1B7A4B','E3F3EA','✓'),(341,'Changed','B42318','FCE9E6','!'),(638,'Couldn’t confirm','8A5A00','FBF1D9','?')]:
    B(x,337,278,60,bg,r=12);T(x+16,353,247,label,22,fg,BOLD,'diagram')
placeholder(44,417,872,43,'team name and presenter names','team.txt')
finish(row)

row=common(1)
T(44,192,872,DATA['facts']['threshold_label'],20,TEAL,SANS,'body')
B(44,239,872,124,WHITE,r=12)
T(69,263,340,DATA['facts']['old_threshold'],53,'B42318',MONO,'diagram')
line(432,300,512,300,TEAL,3);line(512,300,501,292,TEAL,3);line(512,300,501,308,TEAL,3)
T(548,263,345,DATA['facts']['current_threshold'],53,'1B7A4B',MONO,'diagram')
T(46,400,870,row['body'],24,NAVY,DISPLAY,'body')
finish(row)

row=common(2)
for x,item in zip([44,341,638],DATA['facts']['impact_cards']):
    figure,body=item['figure'],item['body']
    B(x,221,278,217,WHITE,r=12);T(x+17,243,244,figure,30,TEAL,MONO,'diagram')
    T(x+17,310,242,body,20,NAVY,SANS,'diagram',25)
finish(row)

row=common(3)
T(44,152,870,row['body'],20,GREY,SANS,'body')
for x,filename,label in [(44,'official-schedule-al.png','official Income Tax page screenshot, ₹1 crore'),(490,'secondary-tax-guide.png','secondary guide screenshot, ₹50 lakh')]:
    path=OUT/'assets'/filename
    if path.exists():
        photo(path,x,218,426,185)
    else:placeholder(x,218,426,185,label,'assets/'+filename)
placeholder(44,420,872,40,'capture dates for both source screenshots','capture-dates.txt')
finish(row)

row=common(4)
steps=[('Paste answer','Input'),('Extract time-sensitive claims','Models'),('Search official domains; read pages','Tavily'),('Two models judge evidence','Bifrost'),('Verdict + evidence + date','Report')]
for i,(body,label) in enumerate(steps):
    x=44+i*177
    B(x,206,164,151,WHITE,TEAL,9);T(x+12,219,140,label,11,TEAL,MONO,'label');T(x+12,252,140,body,20,NAVY,SANS,'diagram',24)
    if i<4:
        line(x+166,281,x+174,281,TEAL,2);line(x+174,281,x+169,277,TEAL,2);line(x+174,281,x+169,285,TEAL,2)
placeholder(44,380,550,79,'Changed card values, quote and source from a verified run','assets/verified-result.json')
B(617,380,299,79,'FBF1D9',r=9);T(633,394,266,row['body'],20,'8A5A00',SANS,'body',24)
finish(row)

row=common(5)
for x,title,description,asset in [(44,'A normal chatbot answer','captured answer text, model name and capture date','assets/captured-answer.json'),(490,'With StillTrue','screen recording of a real run, or verified live demo URL','assets/recorded-run.mp4 OR live-url.txt')]:
    T(x,178,426,title,22,NAVY,BOLD,'diagram')
    placeholder(x,221,426,183,description,asset)
placeholder(44,421,872,40,'Recorded run · date · models','assets/recording-metadata.json')
finish(row)

row=common(6)
# Native architecture; labels are data-flow nodes rather than paragraph text.
for x,y,w,label in [(44,188,90,'User'),(155,188,273,'StillTrue API'),(44,248,160,'Bifrost'),(238,248,190,'Model A / B'),(44,308,160,'Tavily'),(238,308,190,'Official sources'),(44,368,384,'Evidence cache · TTL by volatility')]:
    B(x,y,w,42,WHITE,TEAL,7);T(x+10,y+10,w-20,label,20,TEAL,SANS,'diagram')
for x1,y1,x2,y2 in [(136,209,151,209),(100,232,100,244),(208,269,234,269),(208,329,234,329),(100,292,100,304)]:line(x1,y1,x2,y2,TEAL,2)
T(44,431,390,'Tavily: '+('verified' if all(v=='verified' for v in STATUS['tavily'].values()) else 'planned')+' · Bifrost: '+('verified' if all(v=='verified' for v in STATUS['bifrost'].values()) else 'planned'),20,GREY,SANS,'diagram')
reports=sorted((ROOT/'benchmark/results').glob('*.json'))
if reports:
    data=json.loads(reports[-1].read_text())
    if data.get('mock') or not all(k in data for k in ['stilltrue','baseline']):raise ValueError('Benchmark file is not a compatible real report')
    n=data['stilltrue']['n'];T(488,188,428,('SMALL SAMPLE · ' if n<20 else '')+f'n={n}',20,TEAL,MONO,'diagram')
    cd=CategoryChartData();cd.categories=['Verdict accuracy','False-Still-true rate']
    for label,key in [('StillTrue','stilltrue'),('Plain LLM','baseline')]:cd.add_series(label,[data[key]['accuracy'],data[key]['false_current_rate'] or 0])
    chart=S.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED,Inches(488/72),Inches(232/72),Inches(428/72),Inches(165/72),cd).chart
    chart.has_legend=True
    for i,(label,key) in enumerate([('Accuracy','accuracy'),('False Still true','false_current_rate')]):
        T(488,235+i*90,410,label,20,NAVY,SANS,'diagram')
        for j,(group,col) in enumerate([('stilltrue',TEAL),('baseline',GREY)]):
            val=data[group][key]
            if val is not None:C.setFillColor('#'+col);C.rect(490,540-(265+i*90+j*20)-12,410*val,12,fill=1,stroke=0)
    T(488,418,428,f"Latency p50 / p95: {data['stilltrue']['latency_p50_ms']} / {data['stilltrue']['latency_p95_ms']} ms",20,GREY,SANS,'diagram')
else:placeholder(488,188,428,271,'benchmark chart; run make bench with real keys','../benchmark/results/*.json')
finish(row)

row=common(7)
for x,title,body in [(44,'Who uses it','People: free path. Developers: API / gateway.'),(341,'Next 30 days','More packs. Browser extension. Team audit logs. Planned.'),(638,'Honest limits','Official sources can lag. Models can err. Not professional advice.')]:
    B(x,210,278,187,WHITE,r=10);T(x+16,229,246,title,23,TEAL,DISPLAY,'diagram');T(x+16,277,246,body,20,NAVY,SANS,'diagram',25)
T(44,423,870,row['body'],23,TEAL,DISPLAY,'body')
finish(row)

row=common(8)
T(44,145,872,'StillTrue design: official-first, dated evidence, cross-model, web + API.',20,TEAL,SANS,'body')
for y,name,desc in [(192,'Verity','Chrome / MCP; CURRENT / OUTDATED verdicts'),(236,'jev','Claim checks: supported / contradicted / unverifiable'),(280,'402oracle','Paid claim and URL freshness checks')]:
    B(44,y,872,39,WHITE);T(55,y+7,160,name,20,TEAL,BOLD,'diagram');T(228,y+7,672,desc,20,NAVY,SANS,'diagram')
for x,y,t in [(44,341,'Search chat? Sources can age.'),(490,341,'No source? Unconfirmed.'),(44,382,'Real vs demo? Clearly labelled.'),(490,382,'Cost? Quotas; no billing claims.'),(44,423,'False verdicts? Quotes + gates.'),(490,423,'Privacy? Mask; avoid secrets.')]:T(x,y,426,t,20,GREY,SANS,'diagram')
finish(row)

row=common(9)
for y,title,body in [(180,'Models via Bifrost','Masked claims and evidence go to configured providers.'),(246,'Tavily','Derived search queries and official URLs are sent.'),(312,'Storage','Temporary jobs in memory; evidence cache on disk.'),(378,'Limits','Masking can miss PII. Sources and models can err.')]:
    T(44,y,250,title,22,TEAL,BOLD,'diagram');T(326,y,590,body,20,NAVY,SANS,'diagram',25)
T(44,443,870,'Not legal, tax or financial advice.',20,GREY,SANS,'body')
finish(row)

# Verify every native text shape stays inside its slide and has a role.
errors=[]
for style in STYLES:
    if style['size']<10:errors.append('Font below 10 pt: '+style['text'])
    if style['role']=='body' and style['size']<20:errors.append('Body font below 20 pt')
    if style['contrast']<4.5:errors.append('Contrast failure: '+str(style))
for sid,count in BODY_COUNTS.items():
    if count>35:errors.append(f'{sid}: body word count {count} exceeds 35')
for slide in R.slides:
    for sh in slide.shapes:
        if sh.left<0 or sh.top<0 or sh.left+sh.width>R.slide_width+1000 or sh.top+sh.height>R.slide_height+1000:errors.append('Shape outside slide')
assert len(R.slides)==10
if errors:raise ValueError('\n'.join(errors))
import re
allowed=set(DATA['facts']['number_provenance']) | {str(i) for i in range(1,11)} | {f'{i:02d}' for i in range(1,11)}
observed=set(re.findall(r'\d+', '\n'.join(sh.text for slide in R.slides for sh in slide.shapes if sh.has_text_frame)))
if not reports and observed-allowed:raise ValueError('Unsourced digits: '+str(observed-allowed))
R.core_properties.title='StillTrue — Global AI Hackathon pitch';R.core_properties.author='Hanniel Vinu'
R.save(OUT/'StillTrue_Pitch.pptx');C.save()
(OUT/'quality_report.json').write_text(json.dumps({'slides':10,'main':8,'backup':2,'all_native_editable':True,'minimum_body_font':20,'minimum_source_font':10,'minimum_contrast':min(s['contrast'] for s in STYLES),'body_word_counts':BODY_COUNTS,'placeholders':PLACEHOLDERS,'errors':errors,'benchmark_file':str(reports[-1]) if reports else None},indent=2,ensure_ascii=False))
# The listed placeholder file requirements must all appear in the exact checklist.
checklist=(OUT/'ASSETS_NEEDED.md').read_text()
for ph in PLACEHOLDERS:
    # Paths may be combined in one table cell but their asset descriptions must be accounted for.
    if ph['asset'].split(' OR ')[0] not in checklist:raise ValueError('Missing asset checklist entry: '+ph['asset'])
# Speaker script is generated from the same versioned content as the deck.
script=['# StillTrue speaker script','Event time limit unknown. Full main-deck target: 4:40 (280 seconds). Backup slides are Q&A only.','', '## Three-minute cut','S1 10s; S2 20s; S3 10s; S4 20s; S5 20s; S6 55s; S7 25s; S8 20s = 180s. S3 and S8 are shortened; trimming only those two cannot reduce 4:40 to 3:00. Other cuts and a shorter demo are necessary.','']
start=0
for row in DATA['slides']:
    script += [f"## {row['id']} — {row['title']}",f"Timing: {start//60}:{start%60:02d} · {row['seconds']} seconds. Criterion: {row['criterion']}",row['script'],'']
    start+=row['seconds']
(OUT/'SCRIPT.md').write_text('\n'.join(script))
print('10 editable slides + PDF + script generated; quality gates passed')
