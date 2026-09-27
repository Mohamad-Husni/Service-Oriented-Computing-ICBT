from pathlib import Path
import sys,json,re
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
from PIL import Image,ImageDraw,ImageFont
from report_content import sections,conclusion,references
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'output/WaterLink CSE5013 WRIT1.docx'
fontpath='/System/Library/Fonts/Supplemental/Times New Roman.ttf'
font=ImageFont.truetype(fontpath,40); bold=ImageFont.truetype('/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf',40)
diagram_words=[]
def diagram(name,boxes,arrows,size=(1500,950)):
 im=Image.new('RGB',size,'white');d=ImageDraw.Draw(im)
 for x,y,w,h,lines in boxes:
  d.rounded_rectangle((x,y,x+w,y+h),radius=12,fill='#f2f6f7',outline='#253f49',width=3)
  for i,line in enumerate(lines):
   diagram_words.extend(line.split());d.text((x+w/2,y+25+i*44),line,font=bold if i==0 else font,fill='#162f3b',anchor='mt')
 for start,end,label in arrows:
  d.line((start,end),fill='#253f49',width=4)
  import math
  a=math.atan2(end[1]-start[1],end[0]-start[0]);pts=[end,(end[0]-18*math.cos(a-.5),end[1]-18*math.sin(a-.5)),(end[0]-18*math.cos(a+.5),end[1]-18*math.sin(a+.5))];d.polygon(pts,fill='#253f49')
  if label:d.text(((start[0]+end[0])/2+10,(start[1]+end[1])/2-30),label,font=font,fill='#162f3b',anchor='mm');diagram_words.extend(label.split())
 path=ROOT/'docs/diagrams'/name;im.save(path);return path
architecture=diagram('architecture.png',[(20,20,650,120,['Customer and operator','JavaScript client']), (830,20,650,120,['Partner desktop client','.NET and public contracts']), (20,280,650,120,['ASP.NET Core portal','Cookie session and gateway']), (20,600,650,120,['Usage API','Accounts and meter readings']), (830,600,650,120,['Payment API','Bills and receipt ledger']), (20,820,650,100,['Usage database']), (830,820,650,100,['Payment database'])],[((345,140),(345,280),'HTTP'),((345,400),(345,600),'JSON'),((670,340),(1155,600),'JSON'),((1155,140),(1155,600),'JSON'),((345,720),(345,820),''),((1155,720),(1155,820),'')])
model=diagram('data-model.png',[(30,25,670,160,['Accounts','Id PK   Name   Address']), (30,340,670,260,['Readings','Id PK   AccountId FK','MilliUnits   RecordedAt','RecordedBy']), (800,25,670,160,['Bills','AccountId PK   AmountCents','DueDate']), (800,340,670,300,['Payments','Id PK   AccountId FK','AmountCents   RecordedAt','Reference   Channel','Unique Channel and Reference'])],[((360,185),(360,340),'1 to many'),((1135,185),(1135,340),'1 to many')],(1500,700))
sequence=diagram('payment-flow.png',[(30,20,670,110,['Client sends payment']), (800,20,670,110,['Authenticate and authorise']), (800,230,670,110,['Validate then start transaction']), (30,230,670,150,['Find channel and reference','Matching payload returns receipt']), (30,500,670,150,['New reference checks balance','Excess amount returns conflict']), (800,500,670,150,['Insert payment and commit','Return new receipt']), (800,810,670,100,['Client refreshes current balance'])],[((700,75),(800,75),''),((1135,130),(1135,230),''),((800,295),(700,295),''),((360,380),(360,500),'New'),((700,575),(800,575),''),((1135,650),(1135,810),'')])
doc=Document()
for element in doc.styles.element.iter():
 for child in list(element):
  if child.tag==qn('w:pBdr'):element.remove(child)
sec=doc.sections[0];sec.top_margin=Inches(.8);sec.bottom_margin=Inches(.8);sec.left_margin=Inches(.85);sec.right_margin=Inches(.85)
sec.page_width=Inches(8.27);sec.page_height=Inches(11.69)
for style in doc.styles:
 if style.type in (1,2):
  style.font.name='Times New Roman';style.font.size=Pt(12)
  style.font.color.rgb=RGBColor(0,0,0)
for name,size in [('Title',22),('Heading 1',16),('Heading 2',14)]:
 s=doc.styles[name];s.font.size=Pt(size);s.font.bold=True
 s.paragraph_format.space_before=Pt(12);s.paragraph_format.space_after=Pt(8)
doc.styles['Normal'].paragraph_format.line_spacing=1.15;doc.styles['Normal'].paragraph_format.space_after=Pt(7)
footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
footer.add_run('Page ');fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');footer._p.append(fld)
doc.add_paragraph('WaterLink Service Oriented Solution for NWSDB','Title')
doc.add_paragraph('Service Oriented Computing\nCSE5013 WRIT1')
doc.add_paragraph('Student name: __________________________\nStudent ID: __________________________')
doc.add_paragraph('Application design implementation testing and deployment')
doc.add_paragraph('September 2026')
doc.add_page_break();doc.add_paragraph('Contents','Title')
toc=[];headings=[]
for title,subs in sections:
 toc.append((title,0));toc.extend((sub,1) for sub,_ in subs)
toc.extend([('5 Conclusion',0),('Bibliography',0)])
page_map=json.loads((ROOT/'tmp/report/pages.json').read_text()) if (ROOT/'tmp/report/pages.json').exists() else {}
for i,(title,level) in enumerate(toc):
 p=doc.add_paragraph();p.paragraph_format.left_indent=Inches(.2*level)
 p.paragraph_format.space_after=Pt(4)
 p.paragraph_format.tab_stops.add_tab_stop(Inches(6.25-.2*level),WD_ALIGN_PARAGRAPH.RIGHT)
 link=OxmlElement('w:hyperlink');link.set(qn('w:anchor'),f'h{i}');r=OxmlElement('w:r');t=OxmlElement('w:t');t.text=title;r.append(t);link.append(r);p._p.append(link);p.add_run('\t'+str(page_map.get(title,'')))
doc.add_page_break();body_start=len(doc.paragraphs)
heading_i=0
def heading(text,level):
 global heading_i
 p=doc.add_heading(text,level=level);bookmark=OxmlElement('w:bookmarkStart');bookmark.set(qn('w:id'),str(heading_i));bookmark.set(qn('w:name'),f'h{heading_i}');p._p.insert(0,bookmark);end=OxmlElement('w:bookmarkEnd');end.set(qn('w:id'),str(heading_i));p._p.append(end);heading_i+=1

def picture(path,caption,width=6.5):
 p=doc.add_paragraph();p.paragraph_format.keep_with_next=True;p.add_run().add_picture(str(path),width=Inches(width))
 p=doc.add_paragraph(caption,'Caption');p.paragraph_format.space_after=Pt(12)
def table(caption,headers,rows):
 p=doc.add_paragraph(caption,'Caption');p.paragraph_format.keep_with_next=True
 t=doc.add_table(rows=1,cols=len(headers));t.style='Table Grid'
 for c,value in zip(t.rows[0].cells,headers):c.text=value
 repeat=OxmlElement('w:tblHeader');t.rows[0]._tr.get_or_add_trPr().append(repeat)
 for row in rows:
  for c,value in zip(t.add_row().cells,row):c.text=value
 for row in t.rows:
  for c in row.cells:
   for p in c.paragraphs:p.paragraph_format.space_after=Pt(5);p.paragraph_format.space_before=Pt(5)

def code(path,start,end,caption):
 lines=(ROOT/path).read_text().splitlines();text='\n'.join(lines[start-1:end]);doc.add_paragraph(caption,'Caption')
 p=doc.add_paragraph(text);p.paragraph_format.line_spacing=1;p.paragraph_format.space_after=Pt(10)
 return text
code_words=[]
for title,subs in sections:
 heading(title,1)
 for sub,text in subs:
  heading(sub,2)
  for paragraph in text.split('\n\n'):doc.add_paragraph(paragraph)
  if sub.startswith('1.2'):
   table('Table 1 Architecture comparison for NWSDB',['Criterion','Monolith','Service oriented design'],[
    ['Maintenance','One release includes all modules','Separate usage and payment releases'],['Scaling','Replicate the whole application','Scale individual hosts after database migration'],['Consistency','Local transactions are straightforward','Keep financial changes inside one service'],['Operations','Fewer processes and lower initial overhead','More monitoring and network failure handling'],['Integration','Endpoints possible but shared deployment','Reusable contracts for separate consumers']])
  if sub.startswith('2.1'):picture(architecture,'Figure 1 Implemented service and client deployment structure')
  if sub.startswith('2.2'):picture(model,'Figure 2 Separate service data models and local relationships');picture(sequence,'Figure 3 Payment processing with replay and conflict handling')
  if sub.startswith('2.3'):
   lines=(ROOT/'src/Water.Shared/Domain.cs').read_text().splitlines();start=next(i for i,l in enumerate(lines) if 'public static long Cents' in l)+1
   code_words.append(code('src/Water.Shared/Domain.cs',start,start+6,'Listing 1 Exact amount validation from Water.Shared Domain.cs'))
   lines=(ROOT/'src/Water.Desktop/PaymentClient.cs').read_text().splitlines();start=next(i for i,l in enumerate(lines) if 'public async Task<PaymentResult> Pay' in l)+1
   code_words.append(code('src/Water.Desktop/PaymentClient.cs',start,start,'Listing 2 Desktop API consumption from Water.Desktop PaymentClient.cs'))
  if sub.startswith('2.4'):
   # A legible crop of the actual interface, not a reconstruction.
   im=Image.open(ROOT/'evidence/balance-detail.png');im.save(ROOT/'tmp/report/dashboard-detail.png')
   picture(ROOT/'tmp/report/dashboard-detail.png','Figure 4 Actual outstanding balance card after the browser payment')
   table('Table 2 Implemented requirements and source evidence',['Requirement','Implementation evidence'],[['Reusable .NET services','Water.Usage and Water.Payments API hosts'],['Different API consumers','Water.Portal JavaScript and Water.Desktop .NET'],['Updated payments','Transactional receipt ledger and refreshed balance'],['Current recorded usage','Operator readings with timestamps and consumption'],['Maintainability','Public contracts repository interfaces and shared validation']])
  if sub.startswith('3.1'):
   table('Table 3 Observed verification results',['Test category','Passed','Principal coverage'],[['Unit assertions','16 of 16','Money references and reading rules'],['HTTP integration','26 of 26','Authorisation transactions and conflicts'],['Chromium browser','10 of 10','Payment flow roles and responsive layout'],['Desktop HTTP client','4 of 4','Lookup payment retry and balance'],['Total','56 of 56','Defined checks not coverage percentage']])
body_end=len(doc.paragraphs)
heading('5 Conclusion',1);doc.add_paragraph(conclusion).paragraph_format.keep_together=True
heading('Bibliography',1)
for author,title,url in references:doc.add_paragraph(f'{author} {title}. Available at: {url} (Accessed: 26 September 2026).')
# All run font sizes including captions and table content must be at least 12 pt.
for p in doc.paragraphs:
 for run in p.runs:
  run.font.name='Times New Roman'
  if run.font.size and run.font.size.pt<12:run.font.size=Pt(12)
# Count the assessed body including headings, captions, code and table text, plus diagram labels.
body_text=' '.join(p.text for p in doc.paragraphs[body_start:body_end])+' '+' '.join(c.text for t in doc.tables for r in t.rows for c in r.cells)
count=len(body_text.split())+len(diagram_words)+8
(ROOT/'evidence/report-word-count.json').write_text(json.dumps({'body_including_headings_captions_tables_code_diagram_labels':count,'body_without_diagram_labels':len(body_text.split()),'excludes':'cover contents conclusion bibliography','method':'whitespace-separated tokens; diagram labels and eight screenshot tokens counted separately'},indent=2))
assert 2700<count<3200,count
OUT.parent.mkdir(exist_ok=True);doc.save(OUT);print(OUT,count)
