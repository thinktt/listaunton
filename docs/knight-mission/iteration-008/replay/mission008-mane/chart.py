"""Recover the native Catmull-Clark station/section grid from the accepted, applied mesh."""
from collections import deque
from pathlib import Path
import sys,numpy as np,bpy
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent
def mesh_chart(mesh):
    neighbors=[[] for _ in mesh.vertices]
    for ed in mesh.edges:
        a,b=ed.vertices;neighbors[a].append(b);neighbors[b].append(a)
    def field(seeds):
        dis=np.full(len(neighbors),-1,int);queue=deque(seeds);dis[list(seeds)]=0
        while queue:
            a=queue.popleft()
            for b in neighbors[a]:
                if dis[b]<0:dis[b]=dis[a]+1;queue.append(b)
        return dis
    def between(a,b):
        came={a:None};queue=deque([a])
        while queue and b not in came:
            i=queue.popleft()
            for j in neighbors[i]:
                if j in came:continue
                came[j]=i;queue.append(j)
        path=[b]
        while path[-1]!=a:path.append(came[path[-1]])
        assert len(path)==5,(a,b,path)
        return path[::-1][:-1]
    def ring(station):
        return [v for j in range(64) for v in between(station*64+j,station*64+(j+1)%64)]
    top=ring(0);end=ring(12)
    da=field(top);db=field(end)
    # Adjacent native cage vertices are four edges apart after two rounds of subdivision.
    area=(da+db==48)
    print('tube area',sum(area),flush=True)
    chart=[top]
    for k in range(1,49):
        rest=[]
        for vid in chart[-1]:
            nxt=[j for j in neighbors[vid] if area[j] and da[j]==k]
            assert len(nxt)==1,(k,vid,nxt)
            rest.append(nxt[0])
        chart.append(rest)
    grid=np.array(chart)
    assert np.array_equal(grid[::4,::4],np.arange(832).reshape(13,64))
    assert len(np.unique(grid))==grid.size
    ca=~area&(da<db);cb=~area&(db<da)
    return grid,np.where(ca)[0],np.where(cb)[0]
if __name__=='__main__':
    bpy.ops.wm.open_mainfile(filepath=str(D/'parent.blend'),load_ui=False)
    mesh=bpy.context.scene.objects['Knight | swept rounded mane'].data
    a,b,c=mesh_chart(mesh);np.savez(D/'ring-chart.npz',grid=a,front=b,back=c);print(a.shape,len(b),len(c))

