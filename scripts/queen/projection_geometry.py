"""Feature-preserving physical deformation shared by fitting and Blender export."""
import math
import numpy as np
GROUPS=['foot','socket','collars','crown','egg']
REPRESENTATIVE=np.array([1.037,.544,.60,.62,.17])
def ring_weights(info):
 n=info['ringCount'];w=np.zeros((n,5));fi=info['finialFirstRing'];body=info['bodyRingCount']
 for i in range(n):
  if i<=18:w[i,0]=1
  elif i<=27:t=(i-18)/10;w[i,0]=1-t;w[i,1]=t
  elif i<=38:w[i,1]=1
  elif i<=49:t=(i-38)/12;w[i,1]=1-t;w[i,2]=t
  elif i<=83:w[i,2]=1
  elif i<=body+2:t=(i-83)/(body+3-83);w[i,2]=1-t;w[i,3]=t
  elif i<=fi-2:w[i,3]=1
  elif i<=fi+2:t=(i-(fi-2))/5;w[i,3]=1-t;w[i,4]=t
  else:w[i,4]=1
 assert np.allclose(w.sum(1),1);return w
def deform(points,info,angle,params):
 p=np.asarray(points,dtype=float).copy();p[:,2]-=info['floor']
 c0=math.cos(math.radians(info['elevation']));q0=math.sin(math.radians(info['elevation']));c=math.cos(math.radians(angle));q=math.sin(math.radians(angle))
 w=np.repeat(ring_weights(info),info['ringSegments'],axis=0);dy=np.asarray(params[:5]);dr=np.asarray(params[5:])
 p[:,:2]*=(1+w@dr)[:,None]
 shifts=(q-q0)*(REPRESENTATIVE-info['baseRadius'])+dy/info['scale']+q*REPRESENTATIVE*dr
 p[:,2]=(p[:,2]*c0+w@shifts)/c
 yfloor=info['y0']-info['scale']*c0*info['floor']+info['scale']*(q0-q)*info['baseRadius']
 return p,yfloor
