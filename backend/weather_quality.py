"""Project sanity screening; original provider values are always retained.
Extreme rainfall is not declared false: it is excluded pending source review.
"""
import math

def screen_weather(row):
    row=dict(row);flags=[]
    for field,lo,hi in [('air_temperature_c',-60,60),('rainfall_mm',0,200),('wind_speed_ms',0,100)]:
        raw=row.get('provider_'+field,row.get(field))
        row['provider_'+field]=raw
        if raw is None:
            row[field]=None
        elif not isinstance(raw,(float,int)) or not math.isfinite(raw) or not lo<=raw<hi:
            row[field]=None;flags.append(field+'_requires_source_review')
        else:row[field]=raw
    row['quality_flags']=flags
    row['quality_screen']='Project sanity limits: -60 to <60 °C air, 0 to <200 mm/day rain, 0 to <100 m/s wind; not provider validation'
    return row
