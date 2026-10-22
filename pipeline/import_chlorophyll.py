"""Import genuine published/field/satellite chlorophyll observations.
CSV columns: reservoir_id,observed_at,chlorophyll_a,unit,source,source_url,method,
quality_status,cyanobacteria_dominance_established,dominance_evidence_url
No generated records, unit guesses, or automatic index-to-concentration conversion.
"""
import argparse,json
from urllib.parse import urlparse
import pandas as pd
from backend.config import DATA,today
from backend.monitoring import reservoirs

def ingest(path):
    df=pd.read_csv(path,keep_default_na=False)
    required={'reservoir_id','observed_at','chlorophyll_a','unit','source','source_url','method','quality_status','cyanobacteria_dominance_established','dominance_evidence_url'}
    if not required.issubset(df):raise ValueError('Required columns: '+', '.join(sorted(required)))
    known={r['id'] for r in reservoirs()};stored={}
    for row in df.to_dict('records'):
        if row['reservoir_id'] not in known:raise ValueError('Unknown reservoir ID.')
        stamp=pd.Timestamp(row['observed_at'])
        if stamp.date()>today():raise ValueError('Future observation rejected.')
        value=float(row['chlorophyll_a'])
        if not 0<=value<10000:raise ValueError('Invalid concentration; preserve outliers for review rather than importing.')
        if row['unit'] not in ['µg/L','ug/L','mg/m3','mg/m³']:raise ValueError('Unit must be µg/L or equivalent mg/m³.')
        for key in ['source','method','source_url']:
            if not str(row[key]).strip():raise ValueError('Provenance required.')
        if urlparse(row['source_url']).scheme!='https':raise ValueError('HTTPS source URL required.')
        if row['quality_status']!='approved':raise ValueError('Only externally quality-approved chlorophyll observations can be imported.')
        dominance=str(row['cyanobacteria_dominance_established']).lower()=='true'
        if dominance and urlparse(row['dominance_evidence_url']).scheme!='https':raise ValueError('Dominance evidence URL required; chlorophyll alone is insufficient.')
        row.update(chlorophyll_a=value,unit='µg/L',observed_at=stamp.isoformat(),cyanobacteria_dominance_established=dominance)
        stored.setdefault(row['reservoir_id'],[]).append(row)
    for key,rows in stored.items():
        path=DATA/'observations'/f'{key}-chlorophyll.json'
        existing=json.loads(path.read_text()) if path.exists() else []
        dedup={(o['observed_at'],o['source'],o['method']):o for o in existing+rows}
        path.write_text(json.dumps(list(dedup.values()),indent=2,allow_nan=False))
    print(f'Imported {len(df)} documented observations.')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('csv');a=p.parse_args();ingest(a.csv)
