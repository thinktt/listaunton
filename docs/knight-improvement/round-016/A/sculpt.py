"""Reshape the double-shouldered crest and its bilateral return into the forehead."""
from pathlib import Path
import json,sys,hashlib,math
import bpy,numpy as np
from mathutils import Vector,Matrix
sys.dont_write_bytecode=True;D=Path(__file__).resolve().parent;R=D.parents[2];sys.path[:0]=[str(D),str(R/'scripts/knight')]
from mission_scene import configure_render,render,save_model,use_side_camera,world_vertices,sha
from lower_carving_fit import rest_coords
from mission_pose import posed
from chart import mesh_chart
PARENT='e865a0c635e99bb07a5262a48499140dc34b0e61c757d1e362913fa1c12aef6a';ATLAS='f6e6b26fad1baf22bbf7dd0eb0427cb61b9064245af6acbd268d31068502f4c8'
def ease(x):
 t=np.clip(x,0,1);return t*t*(3-2*t)
def g(x,w):return np.exp(-(x/w)**2)
def pose(s):
 p=json.loads(s['knight_mission_pose']);return [p[k] for k in ['dx','dy','twist_degrees']]
def load(n):
 bpy.ops.wm.open_mainfile(filepath=str(D/(n+'.blend')),load_ui=False);return bpy.context.scene
def carve(s):
 ob=s.objects['Knight | swept rounded mane'];p=pose(s)
 h=np.load(D/'ring-chart.npz');grid=h['grid'];cap=h['front'];old=rest_coords(world_vertices(ob),p);new=old.copy()
 wax=ob.data.attributes['Knight varnish coverage'];var=np.empty(len(old),np.float32);wax.data.foreach_get('value',var);before=var.copy()
 jac=[]
 for i,idx in enumerate(grid[:22]):
  station=i/4;wt=1-ease((station-2.79)/.84);row=old[idx];q=row.copy()
  # Roll the short front return around both sides of the native forehead. Its buried tip keeps the original closed topology.
  front=g(station,.86);widen=.19*front+.22*g(station-.55,.53)
  q[:,1]*=1+widen
  q[:,0]+=.027*g(station,.86)
  q[:,2]+=-.028*g(station,.41)+.010*g(station-.67,.51)
  # Medial apex to base provides the physical outward direction in this transverse section.
  outward=row[128,[0,2]]-row[0,[0,2]];outward/=np.linalg.norm(outward)
  for side in [-1,1]:
   ids=np.array([(128+side*k)%256 for k in range(0,129)]);j=np.arange(129)/4
   orig=q[ids].copy();sect=orig.copy();center=sect[0].copy();y=np.abs(sect[:,1])
   sign=np.sign(sect[28,1]);r=(sect[:,[0,2]]-center[[0,2]])@outward
   width=(.013+.003*g(station-1,.71));w=y[28]-.011*g(station-1.5,1.9)
   inner=w-width/2;outer=w+width/2;yn=y.copy();rr=r.copy()
   # A single convex parabola reaches the bevel. A separately added ridge would cause a second reflection.
   yn[:25]=inner*y[:25]/max(.01,y[24]);yn[24:33]=np.linspace(inner,outer,9)
   yn[33:]+= (outer-y[32])*(1-ease((j[33:]-8)/5))
   drop=.22+.036*g(station-1.08,.76);rr[:25]=-drop*yn[:25]**2/inner
   d=yn[24:33]-inner;initial=2*drop
   span=max(.008,yn[56]-outer);exit_slope=.84
   for _ in range(3):
    ra=-drop*inner-.5*(initial+exit_slope)*width
    av=(ra-r[56])/span
    exit_slope=min(.90,max(initial+.06,.78*av))
   rr[24:33]=-drop*inner-initial*d-.5*(exit_slope-initial)*d*d/width
   # Use physical lateral distance, rather than unevenly spaced control index.
   # Match the deeper parent tangent while keeping curvature one-signed across the visible underface.
   ra,rb=rr[32],r[56];avg=(ra-rb)/span;tail=max(avg+.10,-(r[57]-r[55])/max(.0005,yn[57]-yn[55]))
   power=np.clip((tail-exit_slope)/max(.018,avg-exit_slope),1.3,12.)
   t=np.clip((yn[32:57]-outer)/span,0,1)
   rr[32:57]=ra-span*(exit_slope*t+(avg-exit_slope)*t**power)
   sect[:,1]=sign*yn
   sect[:,[0,2]]+=(rr-r)[:,None]*outward
   # The two extremes share their vertex between the two section traversals.
   sect[[0,-1],1]=q[ids[[0,-1]],1];q[ids]=orig+ease(station/.65)*(sect-orig)
   bevel=g(j-7,1.20);upper=g(j-3.9,2.25);f=g(station-1.25,.78)
   lower=wt*ease((j-8.05)/1.6)*ease((16.0-j)/3.3)
   var[idx[ids]]+=lower*.65*(.11-var[idx[ids]])
   mix=wt*np.maximum(.88*bevel,.70*f*upper);target=.68+.17*f
   var[idx[ids]]+=mix*(target-var[idx[ids]])
  new[idx]=row+wt*(q-row)
  jac.append([round(station,2),round(float(np.max(abs(q[:,1]))),4),round(float(np.max(q[:,2])),4)])
 # The terminal is a closed radial fan behind the forehead. A single spatial map preserves
 # the thin cap while continuing the shoulder into the wood at its sides.
 hold=ease((old[:,0]-.006)/.126)*ease((old[:,2]-4.62)/.15)
 tip=old.copy();tip[:,1]*=1.11;tip[:,0]+=.009;tip[:,2]-=.014+.035*(old[:,0]-.15)
 new+=hold[:,None]*(tip-new)
 delta=posed(new,*p)-posed(old,*p);xyz=np.empty((len(old),3),np.float32);ob.data.vertices.foreach_get('co',xyz.ravel());xyz+=delta@np.linalg.inv(np.array(ob.matrix_world)[:3,:3]).T;ob.data.vertices.foreach_set('co',xyz.ravel());wax.data.foreach_set('value',var);ob.data.update();bpy.context.view_layer.update()
 dist=np.linalg.norm(delta,axis=1)
 info={'maximum_displacement_before_seating':float(dist.max()),'changed_vertices':int((dist>1e-6).sum()),'lower_station_5_25_onward_displacement':float(dist[grid[21:]].max()),'wax_changed_vertices':int((abs(var-before)>1e-6).sum()),'station_width_max_and_height':jac,'forehead_return':forehead(s)}
 return info
def forehead(s):
 # Continue the terminal arris where the mane naturally goes beneath the forehead, on both sides of the solid skull.
 ob=s.objects['Knight | continuous horse head and neck'];p=pose(s);old=rest_coords(world_vertices(ob),p);new=old.copy()
 x,y,z=old.T;ids=np.flatnonzero((x>-.08)&(x<.40)&(abs(y)<.405)&(z>4.83))
 end=np.linspace(0,np.pi*.5,120)
 a=np.r_[np.linspace(-.13,.069,50,endpoint=False),.069+.212*np.sin(end),np.full(27,.281)]
 b=np.r_[np.linspace(.115,.134,50,endpoint=False),.134+.113*(1-np.cos(end)),np.linspace(.250,.315,27)]
 ax,ay=np.gradient(a),np.gradient(b);le=np.hypot(ax,ay);nx,ny=-ay/le,ax/le
 dx=x[ids,None]-a;dy=abs(y[ids,None])-b;closest=np.argmin(dx*dx+dy*dy,axis=1)
 dist=dx[np.arange(len(ids)),closest]*nx[closest]+dy[np.arange(len(ids)),closest]*ny[closest]
 length=ease((closest-28)/40)*ease((len(a)-1-closest)/30)
 side=ease((z[ids]-4.83)/.14)*ease((abs(y[ids])-.055)/.065)
 delta=side*length*(.018*g(dist+.026,.061)-.014*g(dist-.018,.047))
 new[ids,2]+=delta
 wax=ob.data.attributes['Knight varnish coverage'];amount=np.empty(len(old),np.float32);wax.data.foreach_get('value',amount)
 sheen=side*length*.78*g(dist+.004,.024);amount[ids]+=sheen*(.59-amount[ids]);wax.data.foreach_set('value',amount)
 v=np.empty((len(old),3),np.float32);ob.data.vertices.foreach_get('co',v.ravel());delta=posed(new,*p)-posed(old,*p)
 v+=delta@np.linalg.inv(np.array(ob.matrix_world)[:3,:3]).T;ob.data.vertices.foreach_set('co',v.ravel());ob.data.update();bpy.context.view_layer.update()
 return {'changed_vertices':int((np.linalg.norm(delta,axis=1)>1e-6).sum()),'max_shift':float(np.linalg.norm(delta,axis=1).max())}
def light_normals(s):
 ob=s.objects['Knight | swept rounded mane'];m=ob.data;grid=np.load(D/'ring-chart.npz')['grid']
 world=world_vertices(ob);norm=np.empty((len(m.vertices),3),np.float32);m.vertices.foreach_get('normal',norm.ravel())
 norm=norm@np.linalg.inv(np.array(ob.matrix_world)[:3,:3]);norm/=np.linalg.norm(norm,axis=1)[:,None]
 view=np.array(s.camera.matrix_world)[:3,2]
 def reflections(idx):
  n=norm[idx];return world[idx],2*(n@view)[:,None]*n-view
 return grid,reflections
def physical_card(ob,xyz,ray,distance,width,energy,color,extension):
 n=np.median(ray,axis=0);n/=np.linalg.norm(n);p=xyz.mean(0)+distance*n
 ts=((p-xyz)@n)/(ray@n);hot=xyz+ray*ts[:,None];mid=hot.mean(0)
 _,_,vh=np.linalg.svd(hot-mid);ax=vh[0]-n*(vh[0]@n);ax/=np.linalg.norm(ax);ay=np.cross(n,ax)
 along=(hot-mid)@ax;lo,hi=along.min(),along.max();mid+=(lo+hi)*.5*ax
 ob.location=mid;ob.rotation_euler=Matrix(np.column_stack((ax,ay,n))).to_euler()
 ob.data.shape='ELLIPSE';ob.data.size=max(.25,(hi-lo)*(1+extension));ob.data.size_y=width
 ob.data.energy=energy;ob.data.color=color;ob.data.spread=math.radians(120)
 return {'position':list(ob.location),'size':[ob.data.size,width],'watts':energy,'color':list(color)}
def lights(s):
 grid,ref=light_normals(s);rear=s.objects['Walnut | poll rear oval'];a,b=ref(grid[6:15,154]);main=physical_card(rear,a,b,1.55,.060,54.,(1.,.54,.25),.12)
 data=bpy.data.lights.new('Warm front shoulder bounce','AREA');front=bpy.data.objects.new('Walnut | shaped front shoulder bounce',data);s.collection.objects.link(front)
 front.light_linking.receiver_collection=rear.light_linking.receiver_collection
 a,b=ref(grid[2:6,151]);secondary=physical_card(front,a,b,1.06,.082,8.2,(1.,.70,.39),.23)
 bpy.context.view_layer.update()
 return {'rear_oval':main,'front_bounce':secondary,'linked_collection':rear.light_linking.receiver_collection.name}
def crop(s,box):
 x,y,a,b=box;w=s.render.resolution_x;h=s.render.resolution_y;s.render.use_border=s.render.use_crop_to_border=True
 s.render.border_min_x=(x+.1)/w;s.render.border_max_x=(a+.1)/w;s.render.border_min_y=(h-b+.1)/h;s.render.border_max_y=(h-y+.1)/h
def clay(s):
 from diagnostic_views import clay_studio
 clay_studio(s,10.3)
def preview():
 for n in (['trial'] if (D/'parent-clay-side.png').exists() else ['parent','trial']):
  for k in ['wood','clay']:
   s=load('parent')
   if n!='parent':
    carve(s)
    if k=='wood':lights(s)
   if k=='clay':clay(s)
   configure_render(s,36);crop(s,(240,270,530,431));render(s,D/f'{n}-{k}-fixed.png')
   use_side_camera(s);crop(s,(220,90,780,325));render(s,D/f'{n}-{k}-side.png')
def build():
 s=load('parent');before=sha(D/'parent.blend');assert before==PARENT
 pic=s.objects['Knight | swept rounded mane'].active_material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].links[0].from_node.image;assert hashlib.sha256(bytes(pic.packed_file.data)).hexdigest()==sha(D/'pigment.png')==ATLAS
 parts=carve(s);studio=lights(s);config={'parent_sha256':before,'packed_atlas_sha256':ATLAS,'geometry':parts,'studio':studio,'pose':pose(s)}
 s['knight_improvement_016_A']=json.dumps(config)
 configure_render(s,144);save_model(s,D/'inspection.blend');config['model_sha256']=sha(D/'inspection.blend')
 (D/'parameters.json').write_text(json.dumps(config,indent=2)+'\n');print(config)
if __name__=='__main__':
 if sys.argv[-1]=='preview':preview()
 else:build()
