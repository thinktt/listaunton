import bpy,json
p=bpy.context.preferences.addons['cycles'].preferences
print('device types',p.get_device_types(bpy.context))
for typ in ['OPTIX','CUDA','HIP','ONEAPI']:
 try:
  p.compute_device_type=typ;p.get_devices();print(typ,[(d.name,d.type) for d in p.devices])
 except Exception as e:print(typ,str(e))
