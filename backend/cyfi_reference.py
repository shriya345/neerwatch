"""Display-only experimental count references; never operational health categories."""
import math
from numbers import Real
SOURCE_URL='https://www.epa.gov/habs/world-health-organization-who-1999-guideline-values-cyanobacteria-freshwater'
CURRENT_WHO_URL='https://www.who.int/publications/i/item/9789240031302'
EXPLANATION=('Historical WHO-derived recreational reference values, adapted for this experimental display. '
             'The 10,000,000 split is a project display extension, not a cutoff stated on the cited EPA page. '
             'Colours indicate count bands only, not validated public-health safety or Karnataka legal limits. '
             'Cell counts do not establish cyanotoxin concentrations.')
BANDS=[
 {'id':'lower','label':'Lower count band','range':'0 ≤ count < 20,000 cells/mL','color':'#166534','background':'#dcfce7'},
 {'id':'moderate','label':'Moderate count band','range':'20,000 ≤ count < 100,000 cells/mL','color':'#854d0e','background':'#fef9c3'},
 {'id':'high','label':'High count band','range':'100,000 ≤ count ≤ 10,000,000 cells/mL','color':'#991b1b','background':'#fee2e2'},
 {'id':'very_high','label':'Very high count band','range':'count > 10,000,000 cells/mL','color':'#ffffff','background':'#7f1d1d'}]
def reference_band(value,status='complete'):
 """Only completed, finite, nonnegative numeric estimates receive a band."""
 if status!='complete' or isinstance(value,bool) or not isinstance(value,Real) or not math.isfinite(value) or value<0:
  return {'id':'not_assessed','label':'Not assessed','assessed':False,'color':'#475569','background':'#f1f5f9','range':None}
 index=0 if value<20000 else 1 if value<100000 else 2 if value<=10000000 else 3
 return {**BANDS[index],'assessed':True}
