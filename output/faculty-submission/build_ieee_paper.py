from pathlib import Path
import re,html
from reportlab.platypus import BaseDocTemplate,PageTemplate,Frame,Paragraph,Spacer,Table,TableStyle,KeepTogether,FrameBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY,TA_CENTER,TA_LEFT
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing,Rect,String,Line,Polygon
from reportlab.graphics import renderSVG
ROOT=Path(__file__).resolve().parent
W,H=612,792;M=42;G=18;CW=(W-2*M-G)/2
styles={'body':ParagraphStyle('body',fontName='Times-Roman',fontSize=10,leading=11.5,alignment=TA_JUSTIFY,spaceAfter=5), 'h':ParagraphStyle('h',fontName='Times-Roman',fontSize=10,leading=12,alignment=TA_CENTER,spaceBefore=9,spaceAfter=6,keepWithNext=True),'sub':ParagraphStyle('sub',fontName='Times-Italic',fontSize=10,leading=11.5,spaceBefore=5,spaceAfter=4,keepWithNext=True),'caption':ParagraphStyle('caption',fontName='Times-Roman',fontSize=8,leading=9,spaceBefore=4,spaceAfter=7),'ref':ParagraphStyle('ref',fontName='Times-Roman',fontSize=8,leading=9,spaceAfter=4,wordWrap='CJK'),'cell':ParagraphStyle('cell',fontName='Times-Roman',fontSize=8,leading=9)}
def normalize(s):
 for a,b in [('−','-'),('–','-'),('—','-'),('≤','<='),('≥','>='),('×',' x '),('’',"'"),('“','"'),('”','"')]:s=s.replace(a,b)
 return s

def box(d,x,y,w,h,lines):
 d.add(Rect(x,y,w,h,strokeColor=colors.HexColor('#303030'),fillColor=colors.HexColor('#f3f5f4'),strokeWidth=.7))
 for i,t in enumerate(lines):d.add(String(x+w/2,y+h/2+(len(lines)-1)*4.5-i*9,t,fontName='Helvetica',fontSize=7,textAnchor='middle'))
def arrow(d,x1,y1,x2,y2):
 d.add(Line(x1,y1,x2,y2,strokeWidth=.7));d.add(Polygon([x2,y2,x2-2.5,y2+4,x2+2.5,y2+4],fillColor=colors.black,strokeWidth=0))
d=Drawing(CW,240)
box(d,20,208,CW-40,28,['Sentinel-2 L2A / Planetary Computer'])
box(d,0,148,122,40,['Reservoir polygons + QC','60 m scaled reflectance'])
box(d,135,148,120,40,['Separate CyFi crops + QC','Original native-grid inputs'])
arrow(d,66,208,66,188);arrow(d,195,208,195,188)
box(d,0,93,122,36,['Chlorophyll estimate','Observed FAI snapshot'])
box(d,135,93,120,36,['Five pretrained LightGBM','Experimental cells/mL'])
arrow(d,66,148,66,129);arrow(d,195,148,195,129)
box(d,20,45,CW-40,28,['File-backed results + provenance / FastAPI'])
arrow(d,66,93,66,73);arrow(d,195,93,195,73)
box(d,20,0,CW-40,28,['React + Leaflet dashboard'])
arrow(d,CW/2,45,CW/2,28)
renderSVG.drawToFile(d,str(ROOT/'NEERWATCH_Architecture.svg'))
chart=Drawing(CW,132)
for i,(label,n) in enumerate([('Chlorophyll',46),('QC-approved FAI',45),('Experimental CyFi',32)]):
 y=100-i*32
 chart.add(String(0,y+4,label,fontName='Helvetica',fontSize=7.8))
 chart.add(Rect(95,y,130,14,fillColor=colors.HexColor('#e5e7eb'),strokeWidth=0))
 chart.add(Rect(95,y,130*n/46,14,fillColor=colors.HexColor('#345c52'),strokeWidth=0))
 chart.add(String(231,y+3,f'{n}/46',fontName='Helvetica',fontSize=7.5))
chart.add(String(95,4,'Reservoirs with eligible displayed results',fontName='Helvetica',fontSize=7))
renderSVG.drawToFile(chart,str(ROOT/'NEERWATCH_Coverage.svg'))

def page(c,doc):
 c.setFont('Times-Roman',8);c.drawCentredString(W/2,24,str(doc.page))
 if doc.page==1:
  t=Paragraph('NEERWATCH: Satellite-Based Algal Indicator<br/>Monitoring for Karnataka Reservoirs',ParagraphStyle('title',fontName='Times-Roman',fontSize=20,leading=23,alignment=TA_CENTER))
  t.wrap(W-2*M,60);t.drawOn(c,M,724)
  names=['Shriya HR','Sudeeksha V','Shradha Kubhal','Sandya K']
  for i,name in enumerate(names):
   col=i%2;row=i//2;x=M+col*(CW+G);y=658-row*61
   p=Paragraph(f'<b>{name}</b><br/>Department of Computer Science and Engineering<br/>Dayananda Sagar College of Engineering<br/>Bengaluru, Karnataka, India',ParagraphStyle('author'+str(i),fontName='Times-Roman',fontSize=9,leading=10.5,alignment=TA_CENTER))
   p.wrap(CW,50);p.drawOn(c,x,y)
first=[Frame(M,42,CW,535,id='first-left',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0),Frame(M+CW+G,42,CW,535,id='first-right',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)]
normal=[Frame(M,42,CW,H-84,id='left',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0),Frame(M+CW+G,42,CW,H-84,id='right',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)]
output=ROOT/'NEERWATCH_IEEE_Research_Paper.pdf'
doc=BaseDocTemplate(str(output),pagesize=(W,H),title='NEERWATCH: Satellite-Based Algal Indicator Monitoring for Karnataka Reservoirs',author='Shriya HR; Sudeeksha V; Shradha Kubhal; Sandya K',leftMargin=M,rightMargin=M,topMargin=M,bottomMargin=M)
doc.addPageTemplates([PageTemplate(id='first',frames=first,onPage=page,autoNextPageTemplate='normal'),PageTemplate(id='normal',frames=normal,onPage=page)])
story=[];text=(ROOT/'NEERWATCH_IEEE_Research_Paper.md').read_text();paras=text.split('\n\n');refs=False
for p in paras:
 p=p.strip()
 if not p or p.startswith('# ') or p.startswith('Authors:'):continue
 if p=='[[FIGURE1]]':story.append(KeepTogether([d,Paragraph('Fig. 1. Implemented processing paths. CyFi is separate from the chlorophyll/FAI reflectance workflow.',styles['caption'])]));continue
 if p=='[[FIGURE2]]':story.append(KeepTogether([chart,Paragraph('Fig. 2. Reservoir coverage in the inspected snapshot. Coverage is not a measure of environmental accuracy.',styles['caption'])]));continue
 if p=='[[TABLE1]]':
  rows=[['Estimate, cells/mL','Reference band'],['0 <= D < 20,000','Lower'],['20,000 <= D < 100,000','Moderate'],['100,000 <= D <= 10,000,000','High'],['D > 10,000,000','Very high'],['Invalid / withheld / missing','Not assessed']]
  table=Table([[Paragraph(html.escape(x),styles['cell']) for x in row] for row in rows],colWidths=[165,CW-165]);table.setStyle(TableStyle([('LINEABOVE',(0,0),(-1,0),.6,colors.black),('LINEBELOW',(0,0),(-1,0),.4,colors.black),('LINEBELOW',(0,-1),(-1,-1),.6,colors.black),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]));story.append(KeepTogether([Paragraph('TABLE I<br/>EXPERIMENTAL CELL-COUNT REFERENCE BANDS',styles['caption']),table,Spacer(1,6)]));continue
 if p.startswith('## '):
  refs=p=='## REFERENCES'
  if refs:story.append(FrameBreak())
  story.append(Paragraph(html.escape(p[3:]),styles['h']));continue
 if p.startswith('### '):story.append(Paragraph(html.escape(p[4:]),styles['sub']));continue
 if p.startswith('C = [35.75'):
  story.append(Paragraph('C = [35.75(B05/B04) - 19.30]<super>1.124</super> &nbsp; (1)',styles['body']));continue
 if p.startswith('FAI = B08'):
  story.append(Paragraph('FAI = B08 - [B04 + (B11 - B04)k] &nbsp; (2)<br/>k = (842 - 665)/(1610 - 665)',styles['body']));continue
 if p.startswith('D = round'):
  story.append(Paragraph('D = round{exp[max(0, (z<sub>1</sub> + ... + z<sub>5</sub>)/5)] - 1}. &nbsp; (3)',styles['body']));continue
 s=html.escape(normalize(p).replace('`','')).replace('\n',' ')
 if p.startswith('Abstract'):s='<b>'+s+'</b>'
 elif p.startswith('Index Terms'):s='<i>'+s+'</i>'
 story.append(Paragraph(s,styles['ref'] if refs else styles['body']))
doc.build(story)
print(output)
