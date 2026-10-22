"""Historical review of comparable chlorophyll estimates, separate from health claims."""
from datetime import date
from backend.config import today,WHO_URL,CHL_SOURCE

def review(chlorophyll):
    rows=sorted(chlorophyll,key=lambda r:r['observed_at'])
    if not rows:
        return {'status':'Cannot determine','required':None,'reason':'No documented chlorophyll concentration is available for this reservoir.','comparison':None,'trend_required':None,'who':{'status':'Cannot compare','source_url':WHO_URL,'source_caption':CHL_SOURCE}}
    current=rows[-1]
    previous=next((r for r in reversed(rows[:-1]) if r['source']==current['source'] and r['method']==current['method'] and r.get('unit')==current.get('unit') and r['observed_at']<current['observed_at']),None)
    change=current['chlorophyll_a']-previous['chlorophyll_a'] if previous else None
    percent=100*change/previous['chlorophyll_a'] if previous and previous['chlorophyll_a']>0 else None
    concentration=current['chlorophyll_a'];dominance=current.get('cyanobacteria_dominance_established') is True
    level=50 if concentration>=50 else 10 if concentration>=10 else None
    who={'framework':'Historical WHO recreational-water guidance (1999/2003), summarized by EPA','source_url':WHO_URL,'source_caption':CHL_SOURCE,'lower_ug_l':10,'higher_ug_l':50,'dominance_established':dominance,'trigger_level_ug_l':level,'applicable':dominance,'status':('At or above higher reference' if level==50 else 'At or above lower reference' if level==10 else 'Below lower reference'),'interpretation':('Dominance is documented; review the applicable historical guidance.' if dominance else 'Numeric comparison only. Confirm cyanobacteria dominance before applying WHO cyanobacteria guidance. This is not a water-safety clearance.')}
    required=True if level is not None or (change is not None and change>0) else False if previous else None
    status='Required' if required is True else 'Not required' if required is False else 'Cannot determine'
    reason=('Concentration meets a historical WHO reference value; review the satellite estimate and applicable guidance.' if level is not None and not dominance else 'Concentration meets the applicable historical WHO guidance level.' if level is not None else 'Chlorophyll-a increased; review the change and obtain a follow-up observation.' if change is not None and change>0 else 'No increase between the latest comparable estimates; the latest value is below the lower historical reference.' if previous else 'The latest value is below the historical lower reference, but a comparable earlier concentration is needed to assess change.')
    return {'status':status,'required':required,'reason':reason,'as_of':current['observed_at'],'age_days':(today()-date.fromisoformat(current['observed_at'][:10])).days,'scope':'Historical observation review; not a current safety assessment','trend_required':change>0 if change is not None else None,'trend_rule':'User-requested change review: flag a positive change. WHO does not define this percentage-change rule.','who':who,'comparison':{'previous':previous,'current':current,'absolute_ug_l':change,'percent':percent,'direction':'Increasing' if change is not None and change>0 else 'Decreasing' if change is not None and change<0 else 'Unchanged' if change==0 else 'Unknown'}}
