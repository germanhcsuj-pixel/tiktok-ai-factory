"""Procedural orbit scene. Run with Blender's bundled Python, not system Python."""
import argparse
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector

p = argparse.ArgumentParser()
p.add_argument('--profile', choices=['test', 'final'], default='test')
p.add_argument('--engine', choices=['CYCLES', 'BLENDER_WORKBENCH'], default='CYCLES')
p.add_argument('--seed', type=int, default=0)
p.add_argument('--output', default='render-output')
p.add_argument('--probe', action='store_true')
a = p.parse_args(sys.argv[sys.argv.index('--') + 1:])
c = json.loads(Path(__file__).with_name('config.json').read_text())[a.profile]
out = Path(a.output).resolve()
(out / 'frames').mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
s = bpy.context.scene
s.render.engine = a.engine
if a.engine == 'CYCLES':
    s.cycles.device = 'CPU'
    s.cycles.samples = c['samples']
    s.cycles.use_denoising = True
s.render.resolution_x, s.render.resolution_y = c['width'], c['height']
s.render.resolution_percentage = 100
s.render.fps = c['fps']
s.frame_start, s.frame_end = 1, c['fps'] * c['seconds']
s.render.image_settings.file_format = 'PNG'
s.render.filepath = str(out / 'frames' / 'frame_')
s.world = bpy.data.worlds.new('World')
s.world.use_nodes = True
s.world.node_tree.nodes['Background'].inputs[0].default_value = (0.04, 0.06, 0.12, 1)
s.world.node_tree.nodes['Background'].inputs[1].default_value = 0.35

def material(name, color, metal=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    node = m.node_tree.nodes['Principled BSDF']
    node.inputs['Base Color'].default_value = (*color, 1)
    node.inputs['Metallic'].default_value = metal
    node.inputs['Roughness'].default_value = 0.28
    return m

gold = material('Gold', (1, 0.32, 0.045), 0.65)
blue = material('Blue', (0.035, 0.3, 0.8), 0.35)
floor = material('Stage', (0.035, 0.045, 0.08))
bpy.ops.mesh.primitive_plane_add(size=200)
bpy.context.object.data.materials.append(floor)
bpy.ops.mesh.primitive_torus_add(major_radius=1.05, minor_radius=0.22, location=(0, 0, 2))
ring = bpy.context.object
ring.data.materials.append(gold)
for f, angle in [(1, 0), (s.frame_end, 2 * math.pi)]:
    ring.rotation_euler = (0.5 + angle, 0.3, angle)
    ring.keyframe_insert(data_path='rotation_euler', frame=f)
for i in range(5):
    t = i * 2 * math.pi / 5 + a.seed % 360 * math.pi / 180
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=0.28,
                                      location=(1.65 * math.cos(t), 1.65 * math.sin(t), 1.6))
    obj = bpy.context.object
    obj.data.materials.append(blue)
    for f, z in [(1, 1.6), (s.frame_end // 2, 2.6), (s.frame_end, 1.6)]:
        obj.location.z = z + 0.15 * i
        obj.keyframe_insert(data_path='location', frame=f)
    for poly in obj.data.polygons:
        poly.use_smooth = True
for loc, energy, color in [((3, -4, 6), 1000, (1, 0.75, 0.5)),
                           ((-4, 1, 5), 1400, (0.3, 0.55, 1)),
                           ((0, 4, 6), 1200, (1, 1, 1))]:
    bpy.ops.object.light_add(type='AREA', location=loc)
    light = bpy.context.object
    light.data.energy, light.data.color, light.data.shape, light.data.size = energy, color, 'DISK', 5
    light.rotation_euler = (Vector((0, 0, 2)) - light.location).to_track_quat('-Z', 'Y').to_euler()
bpy.ops.object.camera_add()
cam = bpy.context.object
s.camera = cam
cam.data.lens = 45
for f, loc in [(1, (6, -9, 5)), (s.frame_end, (8, -7, 4.5))]:
    cam.location = loc
    cam.rotation_euler = (Vector((0, 0, 2)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam.keyframe_insert(data_path='location', frame=f)
    cam.keyframe_insert(data_path='rotation_euler', frame=f)
s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(out / 'scene.blend'))
(out / 'manifest.json').write_text(json.dumps(dict(c, engine=a.engine, seed=a.seed,
    blender=bpy.app.version_string, frames=s.frame_end), indent=2))
if a.probe:
    s.render.filepath = str(out / 'probe.png')
    bpy.ops.render.render(write_still=True)
else:
    bpy.ops.render.render(animation=True)
