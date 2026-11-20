"""Prove pigment completion leaves geometry, live lighting and relief intact."""
from pathlib import Path
import argparse,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT
from check_base_light_checkpoint import snapshot,digest
import bpy
from render_regions import controls

def local_relief():
    return {o.name:digest([v.value for v in o.data.attributes['Lower flare relief mask'].data]) for o in controls(bpy.context.scene)}

def main(before,after,output):
    a,oldlights,_=snapshot(before);old_relief=local_relief()
    b,newlights,receivers=snapshot(after);assert old_relief==local_relief(), 'Local varnish relief mask changed'
    assert oldlights==newlights,'Lights or receiver routing changed'
    for name,original in a['objects'].items():
        current=b['objects'][name]
        for key in ['positions','faces','matrix','subdivision']:assert original[key]==current[key],(name,key)
        for key in ['uv','attributes']:
            for field,value in original[key].items():assert value==current[key][field],(name,key,field)
        old=original['material'];new=current['material']
        for node,values in old['nodes'].items():assert values==new['nodes'][node],(name,node)
        def retained(links):
            return sorted(row for row in links if row[0] in old['nodes'] and row[2] in old['nodes'] and not (row[2]=='Principled BSDF' and row[3]=='Base Color'))
        assert retained(old['links'])==retained(new['links']), 'Existing relief/finish graph changed'
    for key in ['camera','color_management','world','light_paths']:assert a[key]==b[key],key
    report=dict(before=before,after=after,editable_geometry_exact=True,all_original_uvs_and_attributes_exact=True,live_lights_and_routing_exact=True,camera_world_and_color_management_exact=True,original_finish_and_relief_graph_exact=True,pigment_before_sha256=a['pigment_packed_sha256'],pigment_after_sha256=b['pigment_packed_sha256'],render_receivers=receivers)
    (ROOT/output).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('KING_HIDDEN_PIGMENT_SCOPE_PASS')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('before');p.add_argument('after');p.add_argument('output');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(a.before,a.after,a.output)
