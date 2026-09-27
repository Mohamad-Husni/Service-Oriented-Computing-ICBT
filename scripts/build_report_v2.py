from pathlib import Path
import json,re,sys
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH,WD_TAB_ALIGNMENT,WD_TAB_LEADER
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from report_content_v2 import blocks,conclusion
from report_content import references
from report_diagrams import build
ROOT=Path(__file__).resolve().parent.parent
D=build();images={x['name']:x for x in json.loads((ROOT/'evidence/report-v2/manifest.json').read_text())}
OUT=ROOT/'output/WaterLink CSE5013 WRIT1.docx';QA=ROOT/'tmp/report-v2';QA.mkdir(parents=True,exist_ok=True)
heads=[('1 Architecture choice',1),('1.1 Monolithic and service oriented options',2),('1.2 Maintenance growth and choice',2),('2 Application design and development',1),('2.1 Architecture and scope',2),('2.2 Use cases and access rules',2),('2.3 Classes and code structure',2),('2.4 Payment sequence and data rules',2),('2.5 Service code and client calls',2),('2.6 Customer screens and payment output',2),('2.7 Meter readings and partner access',2),('3 Testing and debugging',1),('3.1 Test results',2),('3.2 Faults found and fixed',2),('4 Deployment options',1),('4.1 Server Docker and Kubernetes',2),('4.2 Recommended approach',2),('5 Conclusion',1),('Bibliography',1)]
figures=[
('architecture','Figure 1 Architecture diagram of the running system'),
('use-case','Figure 2 Use case diagram of the main user actions'),
('class','Figure 3 Class diagram of the payment service and client'),
('sequence','Figure 4 Sequence diagram for a new or repeated payment'),
('code-validation','Figure 5 Code screenshot showing amount validation'),
('code-retry','Figure 6 Code screenshot showing receipt reuse'),
('code-endpoint','Figure 7 Code screenshot showing the payment endpoint'),
('code-client','Figure 8 Code screenshot showing desktop API calls'),
('ui-login','Figure 9 Customer sign in screen'),
('ui-payment','Figure 10 Customer payment form'),
('ui-receipt','Figure 11 Receipt returned by the payment service'),
('ui-updated-balance','Figure 12 Balance after the demonstration payment'),
('ui-operator','Figure 13 Operator meter reading form'),
('ui-meter','Figure 14 Saved meter readings with dates'),
('ui-partner','Figure 15 Partner account lookup'),
('build-output','Figure 16 Saved build output after fixes')]
captions=dict(figures)
page_map=json.loads((QA/'pages.json').read_text()) if (QA/'pages.json').exists() else json.loads((ROOT/'docs/report-pages.json').read_text())
doc=Document();sec=doc.sections[0];sec.page_width=Inches(8.27);sec.page_height=Inches(11.69)
sec.left_margin=sec.right_margin=Inches(.85);sec.top_margin=Inches(.75);sec.bottom_margin=Inches(.7)
for el in doc.styles.element.iter():
 for child in list(el):
  if child.tag==qn('w:pBdr'):el.remove(child)
for style in doc.styles:
 if style.type in (1,2):
  style.font.name='Times New Roman';style.font.size=Pt(12);style.font.color.rgb=RGBColor(0,0,0)
for fonts in doc.styles.element.iter(qn('w:rFonts')):
 for attribute in list(fonts.attrib):
  if attribute.endswith('Theme'):del fonts.attrib[attribute]
 for attribute in ['ascii','hAnsi','eastAsia','cs']:fonts.set(qn('w:'+attribute),'Times New Roman')
normal=doc.styles['Normal'];normal.paragraph_format.line_spacing=1.12;normal.paragraph_format.space_after=Pt(7)
normal.paragraph_format.widow_control=True;normal.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
for name,size in [('Title',24),('Heading 1',16),('Heading 2',14)]:
 st=doc.styles[name];st.font.size=Pt(size);st.font.bold=True;st.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.LEFT;st.paragraph_format.space_before=Pt(10);st.paragraph_format.space_after=Pt(8);st.paragraph_format.keep_with_next=True
cap=doc.styles['Caption'];cap.font.bold=False;cap.font.italic=False;cap.font.size=Pt(12);cap.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.CENTER;cap.paragraph_format.space_before=Pt(4);cap.paragraph_format.space_after=Pt(9)
sec.different_first_page_header_footer=True
h=sec.header.paragraphs[0];h.alignment=WD_ALIGN_PARAGRAPH.RIGHT;h.add_run('WaterLink  |  CSE5013 WRIT1').font.size=Pt(12)
f=sec.footer.paragraphs[0];f.alignment=WD_ALIGN_PARAGRAPH.CENTER;f.add_run('Page ');field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');f._p.append(field)
# Minimal centered title page with aligned identity fields.
p=doc.add_paragraph();p.paragraph_format.space_after=Pt(60)
p=doc.add_paragraph('WaterLink','Title');p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.runs[0].font.size=Pt(30)
p=doc.add_paragraph('Service Oriented Solution for NWSDB','Title');p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.runs[0].font.size=Pt(20)
p=doc.add_paragraph('Application design, development and testing');p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_after=Pt(35)
for line in ['Service Oriented Computing','CSE5013 WRIT1','September 2026']:
 p=doc.add_paragraph(line);p.alignment=WD_ALIGN_PARAGRAPH.CENTER
p=doc.add_paragraph();p.paragraph_format.space_after=Pt(45)
for label in ['Student name','Student ID']:
 p=doc.add_paragraph(f'{label}: __________________________________');p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_after=Pt(16)

def page():doc.add_page_break()
def index_line(title,anchor,level=0):
 p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.LEFT;p.paragraph_format.left_indent=Inches(.2*level);p.paragraph_format.space_after=Pt(7);p.paragraph_format.tab_stops.add_tab_stop(Inches(6.45),WD_TAB_ALIGNMENT.RIGHT,WD_TAB_LEADER.DOTS)
 link=OxmlElement('w:hyperlink');link.set(qn('w:anchor'),anchor);r=OxmlElement('w:r');t=OxmlElement('w:t');t.text=title;r.append(t);link.append(r);p._p.append(link);p.add_run('\t'+str(page_map.get(title,'')))
page();doc.add_paragraph('Contents','Title')
for i,(title,level) in enumerate(heads):index_line(title,'h'+str(i),level-1)
page();doc.add_paragraph('Figures and tables','Title')
for i,(_,caption) in enumerate(figures):index_line(caption,'fig'+str(i))
for i,title in enumerate(['Table 1 Architecture comparison','Table 2 Recorded test cases','Table 3 Deployment choice for this application']):index_line(title,'table'+str(i))
body_words=[];image_words=[];table_words=[];count_on=True

def track(t):
 if count_on:body_words.extend(t.split())
def para(text):
 p=doc.add_paragraph(text);track(text);return p

def heading(title):
 level=dict(heads)[title];p=doc.add_heading(title,level);i=[x[0] for x in heads].index(title);anchor(p,'h'+str(i),i);track(title)
def anchor(p,name,id):
 e=OxmlElement('w:bookmarkStart');e.set(qn('w:id'),str(id));e.set(qn('w:name'),name);p._p.insert(0,e);e=OxmlElement('w:bookmarkEnd');e.set(qn('w:id'),str(id));p._p.append(e)
def textblock(key,selection=None):
 lines=blocks[key] if selection is None else [blocks[key][i] for i in selection]
 for text in lines:para(text)
def figure(key,width=6.4):
 item=D[key] if key in D else images[key]
 p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_after=Pt(0);p.paragraph_format.keep_with_next=True
 p.add_run().add_picture(str(ROOT/item['path']),width=Inches(width))
 caption=captions[key];p=doc.add_paragraph(caption,'Caption');p.paragraph_format.keep_together=True;anchor(p,'fig'+str([k for k,_ in figures].index(key)),100+[k for k,_ in figures].index(key));track(caption);image_words.extend(item['text'].split())
 # Useful alt text for navigation and screen readers.
 doc.inline_shapes[-1]._inline.docPr.set('descr',caption)

def table(caption,columns,rows,widths):
 p=doc.add_paragraph(caption,'Caption');p.alignment=WD_ALIGN_PARAGRAPH.LEFT;p.paragraph_format.keep_with_next=True;track(caption);anchor(p,'table'+str(int(caption.split()[1])-1),200+int(caption.split()[1]))
 t=doc.add_table(rows=1,cols=len(columns));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
 for col,w in zip(t.columns,widths):col.width=Inches(w)
 for c,value in zip(t.rows[0].cells,columns):c.text=value
 repeat=OxmlElement('w:tblHeader');t.rows[0]._tr.get_or_add_trPr().append(repeat)
 for row in rows:
  for c,value in zip(t.add_row().cells,row):c.text=value
 for j,row in enumerate(t.rows):
  cant=OxmlElement('w:cantSplit');row._tr.get_or_add_trPr().append(cant)
  for i,c in enumerate(row.cells):
   c.width=Inches(widths[i]);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER;tcpr=c._tc.get_or_add_tcPr()
   borders=OxmlElement('w:tcBorders')
   for edge in ['top','bottom','left','right']:
    e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'B8C5CA');borders.append(e)
   tcpr.append(borders)
   sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'EAF0F2' if j==0 else 'FFFFFF');tcpr.append(sh)
   for p in c.paragraphs:
    p.alignment=WD_ALIGN_PARAGRAPH.LEFT;p.paragraph_format.space_after=Pt(3 if caption.startswith('Table 2') else 5);p.paragraph_format.space_before=Pt(3 if caption.startswith('Table 2') else 5)
    for r in p.runs:r.font.bold=j==0
   if count_on:table_words.extend(c.text.split())
page();heading('1 Architecture choice');heading('1.1 Monolithic and service oriented options');textblock('1.1')
table('Table 1 Architecture comparison',['Area','Monolithic application','Service oriented design'],[
 ['Release','One program is released','Hosts can be released separately'],['Growth','Copy the whole program','Scale the busy service'],['Data','Related changes are easier to save together','Keep each transaction in one service'],['Operations','Fewer hosts to run','More network and failure handling']],[1.1,2.65,2.65])
para('The choice also depends on the team. Separate services only help when each has a clear purpose and owner. Splitting every small function into a new service would add calls and support work without a clear gain. Two business services give this prototype enough separation while keeping the local setup easy to understand.')
page();heading('1.2 Maintenance growth and choice');textblock('1.2')
para('For example, a new payment partner should only need the payment contract and access details. It should not need a copy of NWSDB\'s meter code. If the receipt layout changes, the payment rules can remain the same. If a payment service release changes a field name, however, both clients may be affected. A stable contract and tests are therefore as important as separate hosts.')
para('For NWSDB, this means that an increase in payment traffic need not force a larger meter service. It also means a meter service outage should not stop a partner from recording a payment. This depends on keeping the payment path free from calls to the usage service. The architecture follows that rule: the payment service owns the bill and receipt data needed to decide whether it can accept a collection.')
para('Before a partner joins, its developer should check the API examples and try both success and error cases. Clear messages help them handle a retry correctly. Keeping these examples with the source makes it easier to update the guide whenever the public contract changes.')
page();heading('2 Application design and development');heading('2.1 Architecture and scope');textblock('2.1');figure('architecture')
para('The browser talks to the portal rather than storing service tokens in page code. The portal keeps the selected demo identity in a protected login cookie and supplies the correct token when calling a service. The desktop client is a separate partner consumer. These are two different ways to use the same payment API, which shows why the service contract is useful across application boundaries.')
page();heading('2.2 Use cases and access rules');textblock('2.2');figure('use-case')
para('Each use case has a clear result. A successful payment gives a receipt; a rejected payment gives a reason. A saved reading appears in the account history with its time. A partner can select an account, but cannot use that selection to gain customer access. This keeps the different responsibilities visible in both the interface and service checks.')
page();heading('2.3 Classes and code structure');textblock('2.3');figure('class')
page();heading('2.4 Payment sequence and data rules');textblock('2.4',[0]);figure('sequence',6.25)
page();textblock('2.4',[1,2]);heading('2.5 Service code and client calls');textblock('2.5',[0]);figure('code-validation')
para('The request body carries accountId, amount and reference. The API guide states the allowed values and errors, and the OpenAPI file describes the JSON fields. A partner can use these files to build a client without opening the service project. Settings such as service addresses and database paths are kept outside the payment rules.')
para('The source layout also supports small changes. A new validation rule can be added to the shared checks and tested before either client is changed. A new screen can call the existing endpoint. When a public field must change, a versioned endpoint can let older clients continue working while their owners update them. This avoids forcing all partners to release on the same day.')
page();textblock('2.5',[1]);figure('code-retry',6.0);textblock('2.5',[2]);figure('code-endpoint',6.0)
page();figure('code-client');heading('2.6 Customer screens and payment output');textblock('2.6');figure('ui-login',5.9)
page();figure('ui-payment',5.8);figure('ui-receipt',6.3)
para('This output was captured from the running local website. The receipt identifies the accepted payment. The next screen shows the balance after the service accepted the payment, rather than a value calculated only in the browser.')
page();figure('ui-updated-balance',6.0);heading('2.7 Meter readings and partner access');textblock('2.7',[0]);figure('ui-operator',5.5)
page();textblock('2.7',[1]);figure('ui-meter',5.0);figure('ui-partner',5.9);textblock('2.7',[2])
page();heading('3 Testing and debugging');heading('3.1 Test results');para('All 56 checks passed: 16 unit, 26 HTTP integration, 10 browser and four desktop HTTP checks. Table 2 lists selected cases from the saved results; each result matched its expected outcome. Use separate seeded data and the supplied demo tokens. TC04 and TC05 follow TC03. Complete scripts and logs are included in the source package. Native desktop interaction remains unverified. Cases TC01 to TC08 use HTTP integration tests; TC09 uses Chromium, and TC10 checks the desktop client HTTP calls without opening a native window.')
table('Table 2 Recorded test cases',['Test ID','Test scenario','Prerequisites','Test steps','Result and status'],[['TC01', 'Missing identity', 'Payment API running', 'Request balance without a token.', 'Pass: 401'], ['TC02', 'Account access', 'Customer token', 'Request account 100000002 balance.', 'Pass: 403'], ['TC03', 'New payment', 'Own account; balance above 100', 'Send LKR 100 with a new reference.', 'Pass: 201; receipt'], ['TC04', 'Safe retry', 'TC03 completed', 'Repeat TC03; read balance.', 'Pass: same receipt; balance reduced once'], ['TC05', 'Changed retry', 'TC03 reference', 'Resend with amount 101.', 'Pass: 409'], ['TC06', 'Invalid amount', 'Customer token', 'Submit 0, then 1.001 with separate references.', 'Pass: 400 for both'], ['TC07', 'Competing payments', 'Partner token; account 100000002 funded', 'Send two full-balance payments together with different references; read balance.', 'Pass: 201 and 409; balance zero'], ['TC08', 'Meter update', 'Operator token; last reading 1258', 'Submit 1260 at current time; read usage.', 'Pass: 201; usage 2 m³'], ['TC09', 'Browser payment', 'Customer signed in; balance above 25', 'Enter 25 and a new reference; submit.', 'Pass: receipt shows 25.00'], ['TC10', 'Desktop API client', 'Partner token; funded account', 'Run desktop smoke mode: lookup, pay, retry, refresh.', 'Pass: all four checks']],[.55,1.05,1.2,2.0,1.6])
page();heading('3.2 Faults found and fixed');textblock('3.2');figure('build-output')
page();heading('4 Deployment options');heading('4.1 Server Docker and Kubernetes');textblock('4.1')
table('Table 3 Deployment choice for this application',['Option','Best fit','Main limit'],[['Server','Simple controlled deployment','One machine may fail'],['Docker Compose','Small pilot with clear setup','Needs tested storage and security'],['Kubernetes','Larger managed service estate','More skills and database changes']],[1.25,2.7,2.45])
heading('4.2 Recommended approach');textblock('4.2')
count_on=False
page();heading('5 Conclusion');para(conclusion);heading('Bibliography')
for author,title,url in references:
 p=doc.add_paragraph(f'{author} {title}. Available at: {url} (Accessed: 26 September 2026).');p.alignment=WD_ALIGN_PARAGRAPH.LEFT;p.paragraph_format.keep_together=True;p.paragraph_format.space_after=Pt(9)
# Font and body count are independently recorded; figure text is not silently omitted.
count=len(body_words)+len(image_words)+len(table_words)
audit={'body_words':count,'body_without_figure_text':len(body_words)+len(table_words),'paragraphs_headings_captions':len(body_words),'figure_text_including_source_and_ui':len(image_words),'tables':len(table_words),'excludes':'cover contents figure list conclusion bibliography','method':'whitespace separated words; text in each included screenshot and diagram counted once','figures':len(figures),'code_screenshots':4,'ui_screenshots':7,'diagrams':4,'build_output_screenshots':1}
(ROOT/'evidence/report-word-count.json').write_text(json.dumps(audit,indent=2));(QA/'outline.json').write_text(json.dumps({'headings':[h for h,_ in heads],'figures':[v for _,v in figures],'tables':['Table 1 Architecture comparison','Table 2 Recorded test cases','Table 3 Deployment choice for this application']},indent=2))
assert 2700 < count < 3200, count
doc.save(OUT);print(OUT,count)
