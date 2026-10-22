"""Primary Sentinel-2 monitoring; no Sentinel-3 substitution."""
import json
from backend.config import DATA
from backend.epa import classify

def monitoring(identifier):
 root=DATA/'sentinel2'/identifier;path=root/'latest.json';latest=json.loads(path.read_text()) if path.exists() else None
 hp=root/'history.json';history=json.loads(hp.read_text()) if hp.exists() else []
 history=sorted([r for r in history if r.get('chlorophyll_a') is not None],key=lambda r:r['observed_at'])
 from backend.readiness import compatible
 previous=next((r for r in reversed(history) if latest and r['observed_at'][:10]<latest['observed_at'][:10] and compatible(r,latest)),None)
 value=latest.get('chlorophyll_a') if latest else None;change=None
 if value is not None and previous and previous['chlorophyll_a']>0:
  delta=value-previous['chlorophyll_a'];change={'absolute':delta,'percent':100*delta/previous['chlorophyll_a'],'start':previous['observed_at'],'end':latest['observed_at'],'previous_concentration':previous['chlorophyll_a'],'current_concentration':value}
 return {'latest':latest,'chlorophyll_a':value,'previous':previous,'history':history,'change':change,'classification':classify(value),'trend':('Increasing' if change['absolute']>0 else 'Decreasing' if change['absolute']<0 else 'Unchanged') if change else 'No comparable observation','status':'available' if value is not None else 'Chlorophyll estimate unavailable' if latest else 'Data unavailable','source':'Sentinel-2 image-derived screening estimate'}
