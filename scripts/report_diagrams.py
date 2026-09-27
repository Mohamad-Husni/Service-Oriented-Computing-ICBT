from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import math,json
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'docs/diagrams/v2';OUT.mkdir(parents=True,exist_ok=True)
FONT='/System/Library/Fonts/Supplemental/Times New Roman.ttf'
BOLD='/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf'
class Canvas:
 def __init__(self,name,w,h):self.name=name;self.im=Image.new('RGB',(w,h),'white');self.d=ImageDraw.Draw(self.im);self.words=[]
 def text(self,xy,text,size=40,bold=False,anchor='mm',bg=False):
  f=ImageFont.truetype(BOLD if bold else FONT,size);self.words.extend(text.split())
  if bg:
   box=self.d.textbbox(xy,text,font=f,anchor=anchor);self.d.rectangle((box[0]-6,box[1]-4,box[2]+6,box[3]+4),fill='white')
  self.d.text(xy,text,font=f,fill='#193642',anchor=anchor)
 def line(self,points,dashed=False):
  if not dashed:self.d.line(points,fill='#506a75',width=3);return
  for a,b in zip(points,points[1:]):
   length=math.dist(a,b)
   for x in range(0,int(length),16):
    y=min(x+9,length);self.d.line([(a[0]+(b[0]-a[0])*x/length,a[1]+(b[1]-a[1])*x/length),(a[0]+(b[0]-a[0])*y/length,a[1]+(b[1]-a[1])*y/length)],fill='#506a75',width=3)
 def arrow(self,a,b,dashed=False,hollow=False,route=None):
  points=route or [a,b];self.line(points,dashed);end=points[-1];prev=points[-2];angle=math.atan2(end[1]-prev[1],end[0]-prev[0]);p1=(end[0]-20*math.cos(angle-.45),end[1]-20*math.sin(angle-.45));p2=(end[0]-20*math.cos(angle+.45),end[1]-20*math.sin(angle+.45));self.d.polygon([end,p1,p2],fill='white' if hollow else '#506a75',outline='#506a75',width=3)
 def box(self,xy,lines,width=3):
  x,y,w,h=xy;self.d.rounded_rectangle((x,y,x+w,y+h),radius=10,fill='#f2f6f7',outline='#506a75',width=width)
  for i,line in enumerate(lines):self.text((x+w/2,y+35+i*48),line,bold=i==0)
 def save(self):
  self.im.save(OUT/(self.name+'.png'));return {'path':str(OUT/(self.name+'.png')),'text':' '.join(self.words)}

def build():
 result={}
 c=Canvas('architecture',1500,1050)
 c.box((20,30,650,140),['Web browser','Customer partner and operator'])
 c.box((830,30,650,140),['Desktop partner client','Water.Desktop'])
 c.box((20,320,650,140),['Web host and gateway','Water.Portal'])
 c.box((20,650,650,140),['Usage API','Water.Usage'])
 c.box((830,650,650,140),['Payment API','Water.Payments'])
 c.box((20,920,650,100),['Usage SQLite database'])
 c.box((830,920,650,100),['Payment SQLite database'])
 c.arrow((345,170),(345,320));c.text((345,245),'HTTP and cookie',bg=True)
 c.arrow((345,460),(345,650));c.text((345,550),'HTTP JSON',bg=True)
 c.arrow((670,390),(1155,650));c.text((925,500),'HTTP JSON',bg=True)
 c.arrow((1155,170),(1155,650));c.text((1155,270),'HTTP JSON',bg=True)
 c.arrow((345,790),(345,920));c.arrow((1155,790),(1155,920))
 result['architecture']=c.save()
 c=Canvas('use-case',1500,1250)
 c.d.rectangle((250,20,1250,1180),outline='#506a75',width=3);c.text((750,70),'WaterLink key use cases',bold=True)
 def actor(x,y,label):
  c.d.ellipse((x-24,y-70,x+24,y-22),outline='#506a75',width=4);c.line([(x,y-22),(x,y+45)]);c.line([(x-48,y),(x+48,y)]);c.line([(x,y+45),(x-38,y+98)]);c.line([(x,y+45),(x+38,y+98)]);c.text((x,y+135),label)
 actor(105,340,'Customer');actor(1395,400,'Partner');actor(105,930,'Operator')
 cases=[(220,'View balance'),(410,'Record payment'),(600,'View payment history'),(790,'View recorded usage'),(980,'Add meter reading')]
 for y,label in cases:
  c.d.ellipse((360,y-60,1140,y+60),fill='#f2f6f7',outline='#506a75',width=3);c.text((750,y),label)
 for y in [220,410,600,790]:c.line([(155,340),(360,y)])
 for y in [220,410,600]:c.line([(1345,400),(1140,y)])
 for y in [790,980]:c.line([(155,930),(360,y)])
 c.text((750,1100),'Access is checked before each service action.')
 c.text((750,1215),'Customers use their own account. Partners see their own receipts.')
 result['use-case']=c.save()
 c=Canvas('class',1500,1350)
 def cls(x,y,w,title,fields,methods,interface=False):
  lines=(["<<interface>>"] if interface else [])+[title];h=90+(45 if interface else 0)+len(fields)*48+30+len(methods)*48
  c.d.rectangle((x,y,x+w,y+h),fill='#f2f6f7',outline='#506a75',width=3)
  ty=y+32
  for line in lines:c.text((x+w/2,ty),line,bold=line==title);ty+=45
  c.line([(x,ty),(x+w,ty)]);ty+=32
  for f in fields:c.text((x+18,ty),f,anchor='lm');ty+=48
  c.line([(x,ty),(x+w,ty)]);ty+=32
  for m in methods:c.text((x+18,ty),m,anchor='lm');ty+=48
  return h
 cls(30,30,650,'PaymentClient',['- client : HttpClient'],['+ GetBalance(account)','+ Pay(request)'])
 cls(830,30,640,'IPaymentRepository',[],['+ Balance(account)','+ History(account, channel)','+ Record(request, channel)'],True)
 cls(830,520,640,'PaymentRepository',['database : Database'],['+ Balance(account)','+ History(account, channel)','+ Record(request, channel)'])
 cls(30,520,650,'PaymentRequest',['+ AccountId : string','+ Amount : decimal','+ Reference : string'],[])
 cls(830,1050,640,'Database',[],['+ Open()','+ Initialize(sql)'])
 c.arrow((1150,520),(1150,339),True,True);c.text((1300,440),'implements',bg=True)
 c.arrow((1150,832),(1150,1050));c.text((1150,970),'uses',bg=True)
 c.arrow((355,294),(355,520),True);c.text((355,420),'sends',bg=True)
 c.arrow((830,680),(680,680),True);c.text((750,625),'reads',bg=True)
 c.text((420,1030),'Selected classes and members',bold=True)
 c.text((420,1100),'The client reaches the repository')
 c.text((420,1150),'through the HTTP API only.')
 c.text((750,1320),'The same repository interface is used by the payment API host.')
 result['class']=c.save()
 c=Canvas('sequence',1500,1800)
 xs=[160,540,920,1320];names=['Client','Payment API','Repository','Database']
 for x,name in zip(xs,names):
  c.box((x-145,20,290,80),[name]);c.line([(x,100),(x,1720)],True)
 def msg(a,b,y,text,ret=False):
  c.arrow((xs[a],y),(xs[b],y),ret);c.text(((xs[a]+xs[b])/2,y-27),text,size=40,bg=True)
 msg(0,1,180,'POST payment')
 c.arrow((540,230),(540,310),route=[(540,230),(650,230),(650,310),(540,310)]);c.text((830,270),'Check identity and account',bg=True)
 msg(1,2,390,'Record(request)');msg(2,3,480,'Begin transaction');msg(2,3,565,'Find reference');msg(3,2,650,'Existing or new',True)
 c.d.rectangle((30,700,1470,1585),outline='#506a75',width=3);c.text((215,733),'alt [matching retry]',bold=True,bg=True)
 msg(2,1,820,'Original receipt',True);msg(1,0,900,'200 replay',True)
 c.line([(30,950),(1470,950)],True);c.text((240,1000),'[new reference]',bold=True,bg=True)
 msg(2,3,1085,'Read balance');msg(3,2,1160,'Available amount',True)
 c.d.rectangle((70,1200,1430,1275),outline='#506a75',width=2);c.text((750,1238),'break [exceeds balance] rollback and return 409',bg=True)
 msg(2,3,1330,'Insert and commit');msg(3,2,1410,'Saved',True);msg(2,1,1480,'New receipt',True);msg(1,0,1560,'201 created',True)
 msg(0,1,1680,'GET balance');c.text((750,1750),'A changed payload with an existing reference returns 409.')
 result['sequence']=c.save()
 (OUT/'manifest.json').write_text(json.dumps(result,indent=2));return result
if __name__=='__main__':build()
