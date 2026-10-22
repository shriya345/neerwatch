"""Strict NASA SeaBASS CAML ingestion. Never guesses abundance conversion.
Supplied severity categories are retained independently of inconsistent units.
No competition split is fabricated; geographic partitions are created later.
"""
import argparse,hashlib,io,json,shutil
from pathlib import Path
import numpy as np,pandas as pd
from backend.config import DATA,write_json
from pipeline.features import density_to_severity
SOURCE='https://seabass.gsfc.nasa.gov/archive/NASA_HEADQUARTERS/SGupta/CAML/CAML_2013_2021/archive'
FILE_URL='https://oceandata.sci.gsfc.nasa.gov/ob/getfile/0c233b5a95_CAML_cyanobacteria_abundance_20211229_R1.sb'

def parse_seabass(path):
    raw=Path(path).read_bytes();text=raw.decode('utf-8-sig');lines=text.splitlines();header={};comments=[];end=None
    if not lines or lines[0].strip().lower()!='/begin_header':raise ValueError('Missing SeaBASS begin_header.')
    for i,line in enumerate(lines[1:],1):
        if line.strip().lower()=='/end_header':end=i;break
        if line.startswith('!'):comments.append(line[1:].strip())
        elif line.startswith('/') and '=' in line:
            k,v=line[1:].split('=',1);header[k.strip().lower()]=v.strip()
    if end is None:raise ValueError('Missing SeaBASS end_header.')
    if header.get('delimiter')!='comma':raise ValueError('Expected documented comma delimiter.')
    columns=header['fields'].split(',');units=header['units'].split(',')
    if len(columns)!=len(units):raise ValueError('Field and unit counts disagree.')
    if len(columns)!=len(set(columns)):raise ValueError('Duplicate field name.')
    unit_map=dict(zip(columns,units));required={'uid','data_provider','region','lat','lon','date','time','abun','severity','distance_to_water_m'}
    if not required.issubset(columns):raise ValueError('CAML schema missing: '+str(required-set(columns)))
    for k,expected in [('lat','degrees'),('lon','degrees'),('date','yyyymmdd'),('time','hh:mm:ss'),('severity','none'),('distance_to_water_m','m')]:
        if unit_map[k]!=expected:raise ValueError(f'Unexpected {k} unit: {unit_map[k]}')
    if unit_map['abun'] not in ['cells/L','cells/mL']:raise ValueError('Unsupported declared abundance unit; review source.')
    body='\n'.join(l for l in lines[end+1:] if l.strip() and not l.startswith('!'))
    # Strict column counts prevent accidental parsing of truncated or malformed rows.
    import csv
    if any(len(row)!=len(columns) for row in csv.reader(io.StringIO(body))):raise ValueError('Malformed data row.')
    frame=pd.read_csv(io.StringIO(body),names=columns,dtype={'uid':'str','date':'str','time':'str'},na_values=[header['missing'],'NA'],keep_default_na=False)
    if frame.uid.duplicated().any() or not frame.uid.str.fullmatch('[A-Za-z0-9_-]{1,80}').all():raise ValueError('Invalid or duplicate UIDs.')
    for col in ['lat','lon','abun','severity','distance_to_water_m']:frame[col]=pd.to_numeric(frame[col],errors='raise')
    if not frame.severity.isin([1,2,3,4,5]).all():raise ValueError('Missing/invalid supplied severity category.')
    if not frame.lat.between(-90,90).all() or not frame.lon.between(-180,180).all():raise ValueError('Missing/invalid sample coordinate.')
    if not np.isfinite(frame.abun).all() or (frame.abun<0).any():raise ValueError('Invalid/missing abundance: review rather than impute.')
    stamp=pd.to_datetime(frame.date+' '+frame.time,format='%Y%m%d %H:%M:%S',utc=True,errors='raise')
    literal_density=frame.abun/(1000 if unit_map['abun']=='cells/L' else 1)
    derived=literal_density.map(density_to_severity)
    unit_audit={'declared_abundance_unit':unit_map['abun'],'physical_conversion_to_cells_per_ml':'.001 × abun' if unit_map['abun']=='cells/L' else 'abun','literal_conversion_agreement_count':int((derived==frame.severity).sum()),'literal_conversion_disagreement_count':int((derived!=frame.severity).sum()),'status':'consistent' if (derived==frame.severity).all() else 'unresolved_source_unit_inconsistency','decision':'Use supplied categorical severity only. Do not infer corrected abundance units, derive new labels, fit density regression or display numerical density.'}
    # Diagnostic arithmetic is evidence of inconsistency, NOT an accepted correction.
    unit_audit['diagnostic_abun_times_1000_agreement_count']=int(((frame.abun*1000).map(density_to_severity)==frame.severity).sum())
    frame['latitude']=frame.lat;frame['longitude']=frame.lon;frame['sample_time_utc']=stamp.dt.strftime('%Y-%m-%dT%H:%M:%SZ');frame['date']=stamp.dt.strftime('%Y-%m-%d');frame['source_dataset']='NASA SeaBASS CAML';frame['label_basis']='source-provided severity category; not rederived from abun';frame['source_url']=SOURCE
    # Do not create split or a supposedly corrected density column.
    audit={'source_url':SOURCE,'file_url':FILE_URL,'source_sha256':hashlib.sha256(raw).hexdigest(),'source_filename':Path(path).name,'rows':len(frame),'fields':columns,'units':unit_map,'header':header,'comments':comments,'missing_counts':{k:int(v) for k,v in frame[columns].isna().sum().items()},'severity_counts':{str(int(k)):int(v) for k,v in frame.severity.value_counts().sort_index().items()},'date_start':frame.date.min(),'date_end':frame.date.max(),'unique_locations':len(frame[['lat','lon']].drop_duplicates()),'duplicate_location_dates':int(frame.duplicated(['lat','lon','date']).sum()),'undocumented_missing_tokens':{'distance_to_water_m':'One literal NA token preserved as missing'},'competition_split_available':False,'abundance_audit':unit_audit,'time_note':'Original source time is retained. To avoid ambiguous/default sample times, satellite matches must precede the sample calendar date.'}
    return frame,audit

def ingest(path):
    frame,audit=parse_seabass(path);folder=DATA/'caml';folder.mkdir(exist_ok=True)
    dest=folder/'CAML_cyanobacteria_abundance_20211229_R1.sb'
    if Path(path).resolve()!=dest.resolve():shutil.copyfile(path,dest)
    frame.to_csv(folder/'labels.csv',index=False);write_json(folder/'audit.json',audit)
    print(json.dumps({k:audit[k] for k in ['rows','severity_counts','abundance_audit','competition_split_available']},indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('file');a=p.parse_args();ingest(a.file)
