from pathlib import Path
import json
from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response,FileResponse
from fastapi.staticfiles import StaticFiles
from backend.config import ROOT,DATA,MODEL,today
from backend.chlorophyll_review import review
from backend.monitoring import reservoirs,summary,model_status
from backend.reports import report
app=FastAPI(title='Karnataka Reservoir Algal Bloom Monitoring',version='1.0.0')
app.add_middleware(CORSMiddleware,allow_origins=['http://127.0.0.1:5180','http://localhost:5180'],allow_methods=['GET','POST'],allow_headers=['*'])
@app.get('/api/health')
def health():return {'status':'online','synthetic_data':False}
@app.get('/api/reservoirs')
def list_reservoirs():
    items=[]
    for reservoir in reservoirs():
        path=DATA/'observations'/f"{reservoir['id']}-chlorophyll.json"
        rows=json.loads(path.read_text()) if path.exists() else []
        rows=[r for r in rows if r['observed_at'][:10]<=today().isoformat()]
        from backend.active import monitoring
        items.append({**reservoir,'chlorophyll_review':review(rows),'monitoring':monitoring(reservoir['id'])})
    return {'items':items}
@app.get('/api/chlorophyll-review.csv')
def chlorophyll_csv():
    import csv
    from io import StringIO
    stream=StringIO();writer=csv.writer(stream);writer.writerow(['Reservoir','Earlier acquisition','Earlier ug/L','Sentinel-2 acquisition','Latest ug/L','Change (%)','EPA category','Trend','Method','Source URL','District or region','Absolute change (ug/L)','RGB URL','Chlorophyll map URL'])
    for item in list_reservoirs()['items']:
        m=item['monitoring'];r=m['latest'];p=m['previous'];c=m['change']
        writer.writerow([item['name'],p['observed_at'] if p else '',p['chlorophyll_a'] if p else '',r['observed_at'] if r else '',m['chlorophyll_a'],c['percent'] if c else '',m['classification']['name'] if m['classification'] else 'Data unavailable',m['trend'],r['method'] if r else '',r['source_url'] if r else '',item.get('district') or item.get('region') or item.get('location') or 'Karnataka',c['absolute'] if c else '',f"/api/reservoirs/{item['id']}/sentinel2/rgb",f"/api/reservoirs/{item['id']}/sentinel2/chlorophyll"])
    return Response(stream.getvalue(),media_type='text/csv',headers={'Content-Disposition':'attachment; filename="sentinel2-chlorophyll.csv"'})
@app.post('/api/reservoirs/{identifier}/process-sentinel2',status_code=202)
def process_sentinel2(identifier:str,force:bool=False):
    if not any(r['id']==identifier for r in reservoirs()):raise HTTPException(404,'Unknown reservoir')
    from pipeline.sentinel2_chlorophyll import start
    return start(identifier,force=force)
@app.get('/api/reservoirs/{identifier}/processing')
def processing(identifier:str):
    if not any(r['id']==identifier for r in reservoirs()):raise HTTPException(404,'Unknown reservoir')
    from pipeline.sentinel2_chlorophyll import get_status
    return get_status(identifier)
@app.get('/api/reservoirs/{identifier}/sentinel2/{kind}')
def sentinel2_asset(identifier:str,kind:str,scene_id:str|None=None):
    from backend.active import monitoring
    detail(identifier)
    state=monitoring(identifier);latest=state['latest']
    if scene_id is not None:latest=next((r for r in state['history'] if r['item_id']==scene_id),None)
    keys={'rgb':'rgb_file','chlorophyll':'chlorophyll_map_file','raster':'chlorophyll_raster_file'}
    if kind not in keys or not latest or not latest.get(keys[kind]):raise HTTPException(404,'This Sentinel-2 output is unavailable')
    path=DATA/'sentinel2'/identifier/Path(latest[keys[kind]]).name
    if not path.exists():raise HTTPException(404,'Cached output unavailable')
    return FileResponse(path,media_type='image/tiff' if kind=='raster' else 'image/png')
@app.get('/api/model')
def model():return model_status()
@app.get('/api/model/test-predictions.csv')
def test_predictions():
    path=MODEL/'test_predictions.csv'
    if not path.exists():raise HTTPException(404,'Genuine held-out predictions are not yet available.')
    return FileResponse(path,media_type='text/csv',filename='caml-held-out-predictions.csv')
@app.get('/api/model/confusion/{kind}')
def confusion(kind:str):
    if kind not in ['mlp','random_forest']:raise HTTPException(404,'Unknown evaluation.')
    path=MODEL/f'{kind}_confusion.png'
    if not path.exists():raise HTTPException(404,'Genuine evaluation is not yet available.')
    return FileResponse(path,media_type='image/png')
@app.get('/api/reservoirs/{identifier}')
def detail(identifier:str):
    try:return summary(identifier)
    except KeyError:raise HTTPException(404,'Unknown Karnataka reservoir.')
@app.get('/api/reservoirs/{identifier}/boundary')
def boundary(identifier:str):
    detail(identifier);path=DATA/'boundaries'/f'{identifier}.geojson'
    if not path.exists():raise HTTPException(404,'Mapped reservoir boundary is not yet available.')
    return json.loads(path.read_text())
@app.get('/api/reservoirs/{identifier}/image')
def image(identifier:str):
    data=detail(identifier);latest=data['latest']
    if not latest or not latest.get('image_filename'):raise HTTPException(404,'No quality-approved satellite image available.')
    path=DATA/'observations'/Path(latest['image_filename']).name
    if not path.exists():raise HTTPException(404,'Archived image unavailable.')
    return FileResponse(path,media_type='image/png')
@app.get('/api/reservoirs/{identifier}/report.pdf')
def pdf(identifier:str):
    data=detail(identifier)
    return Response(report(data),media_type='application/pdf',headers={'Content-Disposition':f'attachment; filename="{identifier}-monitoring-report.pdf"'})
# One production server can serve the built React app and API.
build=ROOT/'frontend/dist'
if build.exists():app.mount('/',StaticFiles(directory=build,html=True),name='dashboard')
