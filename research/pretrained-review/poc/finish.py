from pathlib import Path
import time,tarfile,shutil,subprocess,os,json,hashlib
base=Path(__file__).resolve().parent
archive=base/'land_cover_map.tar.gz'
for _ in range(120):
 if archive.exists() and archive.stat().st_size==2299585370: break
 time.sleep(5)
else: raise TimeoutError('Ancillary download not complete; preserve partial file')
name='C3S-LC-L4-LCCS-Map-300m-P1Y-2020-v2.1.1.nc'
if not (base/name).exists():
 with tarfile.open(archive,'r|gz') as t:
  for member in t:
   if Path(member.name).name==name and member.isfile():
    tmp=base/(name+'.partial')
    with t.extractfile(member) as src,open(tmp,'wb') as dst:shutil.copyfileobj(src,dst,1024*1024)
    tmp.rename(base/name);print('Exact ancillary file extracted',flush=True);break
assert (base/name).exists()
env=dict(os.environ);env['DYLD_LIBRARY_PATH']=str(base.parent/'omp');env['OMP_NUM_THREADS']='1';env['OPENBLAS_NUM_THREADS']='1'
subprocess.run([str(base.parent/'venv/bin/python'),str(base/'run.py')],env=env,check=True)
