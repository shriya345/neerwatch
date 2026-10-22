from io import BytesIO
from pathlib import Path
import reportlab
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,KeepTogether,PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from backend.config import today

FONT=next((p for p in [Path('/System/Library/Fonts/Supplemental/Arial.ttf'),Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),Path(reportlab.__file__).parent/'fonts/Vera.ttf'] if p.exists()),Path('missing-font'))
if FONT.exists():
    pdfmetrics.registerFont(TTFont('ReportFont',str(FONT)))
    FONT_NAME='ReportFont'
else:FONT_NAME='Helvetica'

def report(data):
    stream=BytesIO();styles=getSampleStyleSheet()
    for s in styles.byName.values():s.fontName=FONT_NAME
    styles.add(ParagraphStyle(name='Caption',fontName=FONT_NAME,fontSize=7,leading=10,textColor=colors.HexColor('#617874')))
    styles['BodyText'].fontSize=9.5
    styles['BodyText'].leading=13
    styles['BodyText'].allowWidows=0
    styles['BodyText'].allowOrphans=0
    doc=SimpleDocTemplate(stream,pagesize=(595,842),rightMargin=42,leftMargin=42,topMargin=42,bottomMargin=42,title=data['reservoir']['name']+' reservoir monitoring report')
    def p(text,style='BodyText'):return Paragraph(escape(str(text)),styles[style])
    from backend.active import monitoring
    from backend.epa import CATEGORIES, SOURCE
    active=monitoring(data['reservoir']['id']);latest=active['latest']
    flow=[p('NEERWATCH','Title'),p(data['reservoir']['full_name'],'Heading1'),p(f'Generated {today().isoformat()} · satellite monitoring report'),Spacer(1,15)]
    flow.extend([p('Chlorophyll-a Concentration Classification — US EPA Reference','Heading2'),p('Satellite-derived screening estimate; trophic categories are not water-safety or toxicity determinations.')])
    facts=[['Observation','Result']]
    for label,row in [('Earlier comparable acquisition',active['previous']),('Latest processed acquisition',latest)]:
        value=row.get('chlorophyll_a') if row else None
        facts.append([label,f"{row['observed_at']}: {value:.2f} µg/L" if value is not None else 'Data unavailable'])
    category=active['classification'];change=active['change']
    facts.extend([['EPA trophic category',category['name'] if category else 'Unavailable'],['Concentration change',f"{change['percent']:+.2f}%" if change else 'No comparable observation'],['Trend',active['trend']]])
    table=Table([[p(x) for x in row] for row in facts],colWidths=[175,336]);table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8f2ee')),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),9)]));flow.extend([table,Spacer(1,12)])
    flow.append(p('EPA trophic reference: ≤2 oligotrophic; >2–7 mesotrophic; >7–30 eutrophic; >30 hypereutrophic (µg/L).'))
    flow.append(p('Source: US EPA National Lakes Assessment. '+SOURCE,'Caption'))
    flow.extend([p('Method and limitations','Heading2'),p('Satellite-derived chlorophyll-a estimates have not yet been validated against Karnataka field measurements.'),p('Gilerson red/red-edge equation applied to Sentinel-2 L2A Sen2Cor surface reflectance as an experimental approximation to water-leaving reflectance. ACOLITE aquatic atmospheric correction has not been performed. Values outside the project screening range of 1–100 µg/L are excluded. No field accuracy score is claimed.')])
    if latest:
        flow.extend([p('Acquisition: '+latest['observed_at']),p('Scene: '+latest['item_id'],'Caption'),p('Method: '+latest['method'],'Caption')])
        root=Path(__file__).resolve().parents[1]/'data'/'sentinel2'/data['reservoir']['id']
        for key,label in [('rgb_file','True-colour image'),('chlorophyll_map_file','Chlorophyll-a map from the same acquisition')]:
            file=latest.get(key)
            if file and (root/Path(file).name).exists():
                flow.append(KeepTogether([p(label,'Heading2'),Image(str(root/Path(file).name),width=430,height=260,kind='proportional')]))
    flow.extend([p('Dated Sentinel-2 estimates','Heading2')])
    for row in active['history'][-12:]:flow.append(p(f"{row['observed_at']} — {row['chlorophyll_a']:.2f} µg/L",'Caption'))
    if not active['history']:flow.append(p('Data unavailable. No Sentinel-3 value has been substituted.'))
    def footer(c,doc):
        c.setFont(FONT_NAME,8);c.setFillColor(colors.HexColor('#617874'));c.drawString(42,25,'Satellite screening - estimates are not field measurements');c.drawRightString(553,25,str(doc.page))
    doc.build(flow,onFirstPage=footer,onLaterPages=footer)
    return stream.getvalue()
