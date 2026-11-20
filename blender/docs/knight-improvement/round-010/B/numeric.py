from pathlib import Path
import json
import numpy as np
D=Path(__file__).resolve().parent
data=json.loads((D/'parent-cage.json').read_bytes())
for name in ['near swept ear','far swept ear']:
    a=np.array(data[name]['points']).reshape(7,64,3)
    print(name,np.round(a[2,[0,4,8,12,16,20,24,28,32,36,40,44,48,52,56,60]],3))
for h in data['glints']:
    if h['part'].endswith('far swept ear'):
        a=np.array(data['far swept ear']['points'])
        p=np.array(h['xyz'])
        idx=np.argmin(np.linalg.norm(a-p,axis=1))
        print('hit',h['xy'],idx//64,idx%64,round(data['far swept ear']['finish'][idx],3))
rows=np.array(data['swept rounded mane']['points']).reshape(13,64,3)
for i,row in enumerate(rows[:7]):
    print('ring',i,'centers',np.round(row[[0,32]],3),'rail',np.round(row[25],3),
          'opposite residual',np.max(abs(row[1:32]-row[-1:-32:-1]*[1,-1,1])))
