from copy import deepcopy
from shapely.geometry import box,mapping
from pipeline.mosaic import observations

def scene(identifier,geom,time='2026-10-12T05:17:39Z',orbit=62):
 return {'id':identifier,'geometry':mapping(geom),'properties':{'datetime':time,'platform':'Sentinel-2B','sat:relative_orbit':orbit,'s2:processing_baseline':'05.13','s2:mgrs_tile':identifier}}
def test_complementary_tiles_form_one_same_acquisition():
 g=mapping(box(0,0,2,1));a=scene('A',box(0,0,1.2,1));b=scene('B',box(.8,0,2,1))
 rows=observations([a,b],g);assert len(rows)==1 and len(rows[0]['_mosaic_items'])==2
 assert rows[0]['_mosaic_time_difference_seconds']==0
 assert rows[0]['id'].startswith('MOSAIC_')
def test_no_temporal_or_orbit_mixing():
 g=mapping(box(0,0,2,1));a=scene('A',box(0,0,1,1))
 for b in [scene('B',box(1,0,2,1),time='2026-10-13T05:17:39Z'),scene('B',box(1,0,2,1),orbit=19),scene('B',box(1,0,2,1),time='2026-10-12T05:28:39Z')]:
  assert all('_mosaic_items' not in row for row in observations([a,b],g))
def test_complete_single_scene_preserved():
 a=scene('A',box(0,0,2,1));assert observations([a],mapping(box(0,0,2,1)))==[a]
