"""New QC implementation informed by Nasios' band-statistics methodology.
No upstream code is copied. All statistics use valid water pixels only.
"""
import numpy as np
from scipy.ndimage import binary_erosion, binary_dilation
BANDS = ['B02','B03','B04','B05','B08','B11']
FEATURE_NAMES = [f'{b}_{s}' for b in BANDS for s in ['mean','median','std']] + ['ndci','ndwi','fai']
MIN_PIXELS = 25
MIN_COVERAGE = .10

def extract_features(bands, scl, polygon_mask, resolution=60):
    """At 60 m, erode one water pixel and dilate clouds one pixel.
    Reflectances must already have STAC/native scale and offset applied.
    SCL 6 is water; 3/8/9/10 are shadow/cloud/cirrus. Polygon is required.
    """
    shape = scl.shape
    if polygon_mask.shape != shape or any(v.shape != shape for v in bands.values()):
        raise ValueError('Bands, SCL and polygon must share one grid.')
    polygon = polygon_mask.astype(bool)
    water = polygon & (scl == 6)
    interior = binary_erosion(water, iterations=max(1, int(np.ceil(60/resolution))))
    cloud = binary_dilation(np.isin(scl,[3,8,9,10]),iterations=max(1,int(np.ceil(60/resolution))))
    valid = interior & ~cloud
    for b in BANDS:
        a=bands[b]
        valid &= np.isfinite(a) & (a>0) & (a<=1)
    count=int(valid.sum()); denominator=int(polygon.sum())
    coverage=count/denominator if denominator else 0
    quality={'valid_pixels':count,'polygon_pixels':denominator,'valid_fraction':coverage,'resolution_m':resolution,'shoreline_buffer_m':60,'cloud_buffer_m':60,'minimum_valid_pixels':MIN_PIXELS,'minimum_valid_fraction':MIN_COVERAGE,'screening_basis':'Project quality screening; not provider validation'}
    if count<MIN_PIXELS or coverage<MIN_COVERAGE:
        return {'status':'insufficient_data','quality':quality,'reason':'Too few cloud-free interior water pixels after polygon, shoreline and reflectance checks.','features':None}
    features={}
    for b in BANDS:
        a=bands[b][valid];features.update({f'{b}_mean':float(a.mean()),f'{b}_median':float(np.median(a)),f'{b}_std':float(a.std())})
    red=bands['B04'][valid]; edge=bands['B05'][valid]; green=bands['B03'][valid]; nir=bands['B08'][valid]; swir=bands['B11'][valid]
    features.update(ndci=float(np.median((edge-red)/(edge+red))),ndwi=float(np.median((green-nir)/(green+nir))),fai=float(np.median(nir-(red+(swir-red)*(.842-.665)/(1.610-.665)))))
    return {'status':'available','quality':quality,'features':features,'reason':None}

def density_to_severity(density):
    if not np.isfinite(density) or density < 0:
        raise ValueError('Density must be a finite nonnegative field measurement.')
    return int(np.searchsorted([20000,100000,1000000,10000000],density,side='right')+1)
