import os
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
REGISTRY = Path(os.environ.get('NEERWATCH_REGISTRY',str(DATA/'reservoirs.json')))
MODEL = ROOT / 'models'
def today():
    return datetime.now(ZoneInfo('Asia/Kolkata')).date()
CYANO_SOURCE = 'Source: Field-measured cyanobacteria labels — DrivenData Tick Tick Bloom.'
CHL_SOURCE = 'Source: WHO/EPA published monitoring guidance; applicable when cyanobacteria dominance is established.'
LABEL_URL = 'https://www.drivendata.org/competitions/143/tick-tick-bloom/page/650/'
WHO_URL = 'https://www.epa.gov/habs/world-health-organization-who-1999-guideline-values-cyanobacteria-freshwater'
THRESHOLDS = [{'class':i+1,'range':s,'source':CYANO_SOURCE,'source_url':LABEL_URL} for i,s in enumerate(['<20,000','20,000 – <100,000','100,000 – <1,000,000','1,000,000 – <10,000,000','≥10,000,000'])]
# Historical WHO guidance summarized by EPA; not present-day Karnataka health rules.
CHL_THRESHOLDS = [{'value':10,'unit':'µg/L','label':'WHO historical lower guidance level (1999/2003)','source':CHL_SOURCE,'source_url':WHO_URL},{'value':50,'unit':'µg/L','label':'WHO historical higher guidance level (1999/2003)','source':CHL_SOURCE,'source_url':WHO_URL}]

def write_json(path, data):
    import json, os, tempfile
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix=path.name,dir=path.parent)
    try:
        with os.fdopen(fd,"w") as stream:json.dump(data,stream,indent=2,allow_nan=False)
        os.replace(name,path)
    finally:
        if os.path.exists(name):os.unlink(name)
