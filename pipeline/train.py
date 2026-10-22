"""Five-class MLP and Random Forest on identical geographic holdouts.
Train on genuine supplied CAML categories or validated DrivenData labels with acquired satellite features.
"""
import argparse, copy, hashlib, json
from datetime import datetime,timezone
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import torch
from torch import nn
from sklearn.cluster import KMeans
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
from backend.config import DATA, MODEL
from pipeline.features import FEATURE_NAMES, density_to_severity

class SeverityMLP(nn.Module):
    def __init__(self,n_inputs,dropout=.2):
        super().__init__()
        self.layers=nn.Sequential(nn.Linear(n_inputs,64),nn.ReLU(),nn.Dropout(dropout),nn.Linear(64,32),nn.ReLU(),nn.Dropout(dropout),nn.Linear(32,5))
    def forward(self,x):return self.layers(x)


def read_labels(raw=DATA/'raw'):
    caml=DATA/'caml/labels.csv'
    if raw==DATA/'raw' and caml.exists():
        frame=pd.read_csv(caml)
        if frame.uid.duplicated().any() or not frame.severity.isin([1,2,3,4,5]).all():raise ValueError('Invalid CAML supplied labels.')
        frame['date']=pd.to_datetime(frame.date,utc=True)
        return frame
    files=[raw/'train_labels.csv',raw/'metadata.csv']
    missing=[str(x) for x in files if not x.exists()]
    if missing:raise ValueError('Genuine DrivenData data required. Download after login: '+', '.join(missing))
    labels=pd.read_csv(files[0]);meta=pd.read_csv(files[1])
    for frame,required in [(labels,{'uid','severity','density'}),(meta,{'uid','latitude','longitude','date','split'})]:
        if not required.issubset(frame):raise ValueError('Missing required columns: '+str(required-set(frame.columns)))
        if frame.uid.duplicated().any():raise ValueError('Duplicate uid in input.')
    if not labels.uid.astype(str).str.fullmatch(r'[A-Za-z0-9_-]{1,80}').all():raise ValueError('Unexpected sample UID format.')
    if len(labels)==0:raise ValueError('No field labels supplied.')
    valid=labels.density.map(density_to_severity)
    if not (valid==labels.severity).all():raise ValueError('Density and severity disagree with official boundaries.')
    merged=labels.merge(meta,on='uid',validate='one_to_one')
    if len(merged)!=len(labels) or not (merged.split=='train').all():raise ValueError('Every label must join a train metadata row.')
    merged['date']=pd.to_datetime(merged.date,utc=True)
    if not np.isfinite(merged[['latitude','longitude']].to_numpy()).all():raise ValueError('Nonfinite coordinates.')
    if not merged.latitude.between(-90,90).all() or not merged.longitude.between(-180,180).all():raise ValueError('Invalid coordinates.')
    return merged


def aligned_training(raw=DATA/'raw',features_path=DATA/'training_features.csv'):
    labels=read_labels(raw)
    if not features_path.exists():raise ValueError('No acquired features. Run python -m pipeline.prepare first.')
    features=pd.read_csv(features_path)
    needed={'uid','observed_at','feature_latitude','feature_longitude','source_url','quality_status',*FEATURE_NAMES}
    if not needed.issubset(features):raise ValueError('Feature schema incomplete: '+str(needed-set(features.columns)))
    if features.uid.duplicated().any():raise ValueError('Duplicate feature uid.')
    frame=labels.merge(features,on='uid',validate='one_to_one',suffixes=('_label',''))
    acquired=pd.to_datetime(frame.observed_at,utc=True)
    # Label dates are dates only: allow imagery on the same calendar date.
    age=(frame.date-acquired.dt.floor('D')).dt.days
    if not age.between(1 if 'source_dataset' in frame.columns else 0,10).all():raise ValueError('Temporal leakage or imagery outside 10-day historical window.')
    if not (np.isclose(frame.latitude,frame.feature_latitude,atol=1e-6,rtol=0)&np.isclose(frame.longitude,frame.feature_longitude,atol=1e-6,rtol=0)).all():raise ValueError('Feature coordinates do not match field sample.')
    if not (frame.quality_status=='available').all() or frame.source_url.isna().any():raise ValueError('Unverified feature provenance or quality.')
    if not np.isfinite(frame[FEATURE_NAMES].to_numpy()).all():raise ValueError('Nonfinite features; missing observations are not imputed.')
    return frame


def geographical_split(frame):
    locations=frame[['latitude','longitude']].drop_duplicates()
    if len(frame)<100 or len(locations)<10:raise ValueError('At least 100 valid samples and 10 unique locations required for meaningful grouped evaluation.')
    # Coarse geographic clusters group neighboring sampling points together.
    clusters=KMeans(n_clusters=min(20,len(locations)),random_state=42,n_init=10).fit(locations)
    groups=clusters.predict(frame[['latitude','longitude']])
    trainval,test=next(GroupShuffleSplit(n_splits=1,test_size=.2,random_state=42).split(frame,groups=groups))
    # Choose a development-only validation partition for class coverage and size.
    # The geographic test partition above is fixed and never used in this choice.
    best=None
    for a,b in GroupShuffleSplit(n_splits=256,test_size=.25,random_state=43).split(frame.iloc[trainval],groups=groups[trainval]):
        candidate_train,candidate_val=trainval[a],trainval[b]
        counts=[np.bincount(frame.iloc[ix].severity.to_numpy(dtype=int),minlength=6)[1:] for ix in [candidate_train,candidate_val]]
        if min(c.min() for c in counts)<2:continue
        score=abs(len(candidate_val)-.25*len(trainval))
        if best is None or score<best[0]:best=(score,candidate_train,candidate_val)
    if best is None:raise ValueError('No geographic validation partition covers all five classes with two samples each. Acquire more matched field samples.')
    _,train,val=best
    for left,right in [(train,val),(train,test),(val,test)]:assert not set(groups[left])&set(groups[right])
    if set(frame.iloc[train].severity)!={1,2,3,4,5}:raise ValueError('Training split lacks one or more classes. Acquire more field-matched samples.')
    return train,val,test,groups


def metrics(y,pred):
    return {'accuracy':float(accuracy_score(y,pred)),'macro_f1':float(f1_score(y,pred,labels=[1,2,3,4,5],average='macro',zero_division=0)),'per_class':classification_report(y,pred,labels=[1,2,3,4,5],output_dict=True,zero_division=0),'confusion_matrix':confusion_matrix(y,pred,labels=[1,2,3,4,5]).tolist()}


def fit_mlp(x,y,train,val,lr,dropout,epochs):
    torch.manual_seed(42)
    model=SeverityMLP(x.shape[1],dropout)
    counts=np.bincount(y[train]-1,minlength=5)
    weights=torch.tensor(len(train)/(5*counts),dtype=torch.float32)
    loss_fn=nn.CrossEntropyLoss(weight=weights)
    optimizer=torch.optim.AdamW(model.parameters(),lr=lr,weight_decay=1e-4)
    scheduler=torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer,mode='max',factor=.5,patience=5)
    inputs=torch.tensor(x,dtype=torch.float32);targets=torch.tensor(y-1,dtype=torch.long)
    best=-1;stale=0;saved=None;history=[]
    for epoch in range(epochs):
        model.train();order=torch.tensor(train)[torch.randperm(len(train))]
        for batch in order.split(128):
            optimizer.zero_grad();loss=loss_fn(model(inputs[batch]),targets[batch]);loss.backward();optimizer.step()
        model.eval()
        with torch.no_grad():pred=model(inputs[val]).argmax(1).numpy()+1
        score=f1_score(y[val],pred,labels=[1,2,3,4,5],average='macro',zero_division=0)
        history.append({'epoch':epoch+1,'validation_macro_f1':float(score)})
        scheduler.step(score)
        if score>best+1e-5:best=score;saved=copy.deepcopy(model.state_dict());stale=0
        else:stale+=1
        if stale>=15:break
    model.load_state_dict(saved)
    return model,best,history


def train(epochs=150):
    torch.set_num_threads(2);np.random.seed(42)
    frame=aligned_training();tr,va,te,groups=geographical_split(frame)
    scaler=StandardScaler().fit(frame.iloc[tr][FEATURE_NAMES]);x=scaler.transform(frame[FEATURE_NAMES]);y=frame.severity.to_numpy(dtype=int)
    candidates=[];best_model=None;best_score=-1;best_config=None
    for lr in [.001,.0003]:
        for dropout in [.15,.3]:
            model,score,history=fit_mlp(x,y,tr,va,lr,dropout,epochs)
            config={'learning_rate':lr,'dropout':dropout,'validation_macro_f1':score,'history':history};candidates.append(config)
            if score>best_score:best_score=score;best_model=model;best_config=config
    forest=RandomForestClassifier(n_estimators=300,max_depth=16,min_samples_leaf=2,class_weight='balanced',n_jobs=-1,random_state=42)
    forest.fit(x[tr],y[tr])
    best_model.eval()
    with torch.no_grad():pred=best_model(torch.tensor(x[te],dtype=torch.float32)).argmax(1).numpy()+1
    result={'trained_at':datetime.now(timezone.utc).isoformat(),'status':'trained','task':'same-date severity classification','forecast_horizon_days':0,'training_origin':'United States field-measured cyanobacteria samples','karnataka_field_validated':False,'evaluation':'Held-out geographic clusters of field-labelled US observations; not Karnataka validation','samples':len(frame),'train_count':len(tr),'validation_count':len(va),'test_count':len(te),'mlp':metrics(y[te],pred),'random_forest':metrics(y[te],forest.predict(x[te])),'selected_config':best_config,'candidates':candidates,'feature_names':FEATURE_NAMES,'label_mapping':{str(i):i for i in range(1,6)},'quality_pipeline':'sentinel2-scl-water-60m-v1','source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ([DATA/'caml/CAML_cyanobacteria_abundance_20211229_R1.sb',DATA/'caml/labels.csv',DATA/'training_features.csv'] if (DATA/'caml/labels.csv').exists() else [DATA/'raw/train_labels.csv',DATA/'raw/metadata.csv',DATA/'training_features.csv'])}}
    if (DATA/'caml/audit.json').exists():
        audit=json.loads((DATA/'caml/audit.json').read_text())
        result.update(training_source='NASA SeaBASS CAML',dataset_doi='10.5067/SeaBASS/CAML/DATA001',label_basis='Dataset-supplied severity; no labels derived from abundance',abundance_unit_audit=audit['abundance_audit'],original_competition_split_used=False,split_method='New geographic cluster-disjoint train/validation/test split; seed 42/43')
        selection=DATA/'caml/acquisition_selection.json'
        if selection.exists():result['acquisition_selection']=json.loads(selection.read_text())
    result['partition_class_counts']={name:{str(c):int((y[ix]==c).sum()) for c in range(1,6)} for name,ix in [('train',tr),('validation',va),('test',te)]}
    result['evaluation_quality']='Exploratory acquisition pilot; sample sizes and source unit inconsistency preclude operational validation.'
    result['operational_use_supported']=False
    MODEL.mkdir(exist_ok=True)
    torch.save({'state_dict':best_model.state_dict(),'n_inputs':len(FEATURE_NAMES),'dropout':best_config['dropout']},MODEL/'severity_mlp.pt')
    joblib.dump(scaler,MODEL/'scaler.joblib');joblib.dump(forest,MODEL/'random_forest.joblib')
    (MODEL/'metadata.json').write_text(json.dumps(result,indent=2,allow_nan=False))
    pd.DataFrame({'uid':frame.iloc[te].uid.to_numpy(),'supplied_severity':y[te],'mlp_prediction':pred,'random_forest_prediction':forest.predict(x[te])}).to_csv(MODEL/'test_predictions.csv',index=False)
    split=[]
    for name,indices in [('train',tr),('validation',va),('test',te)]:
        for i in indices:split.append({'uid':frame.iloc[i].uid,'partition':name,'geographic_group':int(groups[i])})
    pd.DataFrame(split).to_csv(MODEL/'split_manifest.csv',index=False)
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    for name in ['mlp','random_forest']:
        fig,ax=plt.subplots(figsize=(5,4));cm=np.array(result[name]['confusion_matrix']);im=ax.imshow(cm,cmap='Blues');ax.set(xlabel='Predicted severity',ylabel='Source-provided severity',xticks=range(5),yticks=range(5),xticklabels=range(1,6),yticklabels=range(1,6),title='Neural network' if name=='mlp' else 'Random Forest')
        for i in range(5):
            for j in range(5):ax.text(j,i,str(cm[i,j]),ha='center',va='center')
        fig.colorbar(im,ax=ax);fig.tight_layout();fig.savefig(MODEL/f'{name}_confusion.png',dpi=160);plt.close(fig)
    print(json.dumps({k:result[k] for k in ['train_count','validation_count','test_count','mlp','random_forest']},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--epochs',type=int,default=150);args=p.parse_args()
    try:train(args.epochs)
    except ValueError as e:raise SystemExit(str(e))
