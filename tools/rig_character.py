#!/usr/bin/env python3
"""Reduce a raw generated character mesh, give it the shared skeleton and clips, export one GLB.

Runs with Blender's Python module (pip install bpy) or inside Blender:

  python3 tools/rig_character.py art/raw/player.glb assets/player.glb --tris 15000
  (keep --tris at 15000 or more: generated meshes fall apart well below that)
  blender -b -P tools/rig_character.py -- art/raw/player.glb assets/player.glb --tris 15000

The skeleton and animation clips come from art/rig/ual_rig.glb (Quaternius
Universal Animation Library skeleton, CC0). Its rest pose is a T-pose, so a
T-pose mesh only has to be scaled onto it:

  1. join the mesh parts, weld seams, reduce to the triangle budget;
  2. stand the mesh on the ground, facing the same way as the skeleton, lift
     drooping arms level (images rarely give a perfect T-pose), and scale it so
     its shoulders sit at the skeleton's shoulder height;
  3. move the skeleton's shoulder joints out to the mesh's shoulders and slide the arm
     bones in or out so the fingertips meet the mesh's;
  4. skin the mesh, either by copying weights from the reference body that
     ships with the skeleton (default, works on any mesh) or with Blender's
     automatic weights (--auto-weights);
  (--no-lift skips the arm levelling in step 2, for arms that are bent rather than drooping)
  5. make the hands rigid (finger weights go to the hand bone; --fingers keeps them);
  6. export mesh + skeleton + every clip as one GLB.
"""
import math, os, sys
import bpy
import bmesh  # must come after bpy
from mathutils import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RIG = os.path.join(ROOT, 'art', 'rig', 'ual_rig.glb')
ARM_BONES = ('clavicle', 'upperarm', 'lowerarm', 'hand', 'thumb', 'index', 'middle', 'ring', 'pinky')


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
    opts = {'tris': 15000, 'auto': '--auto-weights' in a, 'fingers': '--fingers' in a,
            'no_lift': '--no-lift' in a, 'tex': 1024}
    pos = []
    i = 0
    while i < len(a):
        if a[i] in ('--tris', '--tex'):
            opts[a[i][2:]] = int(a[i + 1]); i += 2
        elif a[i].startswith('--'):
            i += 1
        else:
            pos.append(a[i]); i += 1
    if len(pos) != 2:
        sys.exit(__doc__)
    return pos[0], pos[1], opts


def only(objs, active=None):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = active or objs[0]


def import_glb(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    return [o for o in bpy.data.objects if o not in before]


def world_verts(obj):
    return [obj.matrix_world @ v.co for v in obj.data.vertices]


def prepare_mesh(path, tris):
    parts = [o for o in import_glb(path) if o.type == 'MESH']
    only(parts)
    if len(parts) > 1:
        bpy.ops.object.join()
    mesh = bpy.context.view_layer.objects.active
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    for o in list(bpy.data.objects):
        if o.type == 'EMPTY':
            bpy.data.objects.remove(o)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    # Weld the seams, then split every edge shared by more than two faces. Generated meshes
    # have layers that touch (an apron on a body); welded, those edges stop the reduction
    # from working and the mesh comes out as shards.
    bm = bmesh.new()
    bm.from_mesh(mesh.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.split_edges(bm, edges=[e for e in bm.edges if len(e.link_faces) > 2])
    bm.to_mesh(mesh.data)
    bm.free()
    mesh.data.calc_loop_triangles()
    n = len(mesh.data.loop_triangles)
    if n > tris:
        mod = mesh.modifiers.new('reduce', 'DECIMATE')
        mod.ratio = tris / n
        bpy.ops.object.modifier_apply(modifier=mod.name)
    mesh.data.calc_loop_triangles()
    print(f'mesh: {n} -> {len(mesh.data.loop_triangles)} triangles')
    return mesh


def fit_mesh_to_rig(mesh, arm, allow_lift=True):
    """Ground and centre the mesh, lift drooping arms level, and scale it so the
    shoulders sit at the skeleton's shoulder height."""
    vs = world_verts(mesh)
    zmin = min(v.z for v in vs)
    xs = sorted(v.x for v in vs)
    xmid = (xs[0] + xs[-1]) / 2
    ymid = sorted(v.y for v in vs)[len(vs) // 2]
    half = (xs[-1] - xs[0]) / 2
    height = max(v.z for v in vs) - zmin
    pts = [[abs(v.x - xmid), v.y - ymid, v.z - zmin, 1 if v.x >= xmid else -1] for v in vs]

    # Fit a straight line through the arms: slices of the outer half of the span, upper body only.
    bins = {}
    for ax, _, z, _ in pts:
        if 0.5 * half < ax < 0.92 * half and z > 0.5 * height:
            bins.setdefault(int(ax / half * 20), []).append((ax, z))
    cs = [(sum(p[0] for p in b) / len(b), sum(p[1] for p in b) / len(b)) for b in bins.values()]
    mx, mz = sum(c[0] for c in cs) / len(cs), sum(c[1] for c in cs) / len(cs)
    slope = sum((c[0] - mx) * (c[1] - mz) for c in cs) / sum((c[0] - mx) ** 2 for c in cs)
    base = mz - slope * mx
    bones = arm.data.bones
    sh = arm.matrix_world @ bones['upperarm_l'].head_local
    ratio = sh.x / sh.z                      # how far out the shoulder joint is, per unit of its height
    pz = base / (1 - ratio * slope)          # shoulder height on the mesh, where the arm line meets it
    px = ratio * pz
    lift = -math.atan(slope)
    if abs(lift) > math.radians(4) and allow_lift:
        for p in pts:
            dx, dz = p[0] - px, p[2] - pz
            if dx <= 0 or dz < slope * dx - 0.1 * height:   # not part of an arm
                continue
            t = min(1.0, dx / (0.06 * height))
            a = lift * t * t * (3 - 2 * t)
            p[0] = px + dx * math.cos(a) - dz * math.sin(a)
            p[2] = pz + dx * math.sin(a) + dz * math.cos(a)
        print(f'arms: lifted {math.degrees(lift):.0f} degrees to level')
    s = sh.z / pz
    # Where the arm leaves the body: the widest point of the chest, just under the armpits.
    chest = sorted(p[0] for p in pts if pz - 0.22 * height < p[2] < pz - 0.12 * height)
    shoulder_x = chest[int(len(chest) * 0.98)] * s if chest else sh.x
    shoulder_x = min(max(shoulder_x, 0.8 * sh.x), 2.2 * sh.x)
    spine_y = (arm.matrix_world @ bones['spine_02'].head_local).y
    for v, p in zip(mesh.data.vertices, pts):
        v.co = Vector((p[3] * p[0] * s, p[1] * s + spine_y, p[2] * s))
    mesh.data.update()
    vs = world_verts(mesh)
    print(f'fit: scale {s:.3f}, height {max(v.z for v in vs):.2f} m, half span {max(abs(v.x) for v in vs):.2f} m, '
          f'shoulder at {shoulder_x:.2f} m (skeleton {sh.x:.2f})')
    return max(abs(v.x) for v in vs), shoulder_x


def fit_arms(arm, mesh_tip_x, mesh_shoulder_x):
    """Move the shoulder joints out to the mesh's shoulders, then stretch or shrink both
    arm chains so the fingertips reach the mesh's fingertips. Returns what was done so the
    reference body can be reshaped the same way."""
    only([arm])
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm.data.edit_bones
    shoulder = eb['upperarm_l'].head.x
    tip = max(b.tail.x for b in eb if b.name.startswith('middle'))
    k = (mesh_tip_x - mesh_shoulder_x) / (tip - shoulder)
    for b in eb:
        if b.name.startswith('clavicle'):
            b.tail.x = (1 if b.tail.x >= 0 else -1) * mesh_shoulder_x
        elif b.name.startswith(ARM_BONES):
            for p in (b.head, b.tail):
                sign = 1 if p.x >= 0 else -1
                p.x = sign * (mesh_shoulder_x + (abs(p.x) - shoulder) * k)
    bpy.ops.object.mode_set(mode='OBJECT')
    print(f'arms: shoulders moved {mesh_shoulder_x - shoulder:+.2f} m, bone chain scaled by {k:.2f}')
    return shoulder, mesh_shoulder_x, k


def stretch_reference(ref_meshes, shoulder, mesh_shoulder_x, k):
    """Reshape the reference body the same way (wider or narrower torso, longer or shorter
    arms) so its weights still line up with the mesh."""
    for o in ref_meshes:
        inv = o.matrix_world.inverted()
        for v in o.data.vertices:
            w = o.matrix_world @ v.co
            ax = abs(w.x)
            ax = mesh_shoulder_x + (ax - shoulder) * k if ax > shoulder else ax * mesh_shoulder_x / shoulder
            w.x = ax if w.x >= 0 else -ax
            v.co = inv @ w
        o.data.update()


def skin(mesh, arm, ref_meshes, auto):
    only([mesh, arm], arm)
    if auto:
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
        if any(v.groups for v in mesh.data.vertices):
            print('skin: automatic weights')
            return
        print('skin: automatic weights failed, copying from the reference body')
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        only([mesh, arm], arm)
    bpy.ops.object.parent_set(type='ARMATURE_NAME')  # empty groups, one per bone
    body = max(ref_meshes, key=lambda o: len(o.data.vertices))
    mod = mesh.modifiers.new('weights', 'DATA_TRANSFER')
    mod.object = body
    mod.use_vert_data = True
    mod.data_types_verts = {'VGROUP_WEIGHTS'}
    mod.vert_mapping = 'POLYINTERP_NEAREST'
    mod.layers_vgroup_select_src = 'ALL'
    mod.layers_vgroup_select_dst = 'NAME'
    only([mesh])
    bpy.ops.object.datalayout_transfer(modifier=mod.name)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.ops.object.vertex_group_limit_total(group_select_mode='ALL', limit=4)
    bpy.ops.object.vertex_group_normalize_all(group_select_mode='ALL', lock_active=False)
    print('skin: weights copied from the reference body')


def rigid_hands(mesh):
    """Move every finger weight onto the hand bone. Generated hands rarely match the
    skeleton's finger layout, and a stiff hand looks far better than crumpled fingers."""
    for side in ('l', 'r'):
        names = [g.name for g in mesh.vertex_groups
                 if g.name.endswith('_' + side) and g.name.startswith(ARM_BONES[4:])]
        fingers = {mesh.vertex_groups[n].index for n in names}
        add = {v.index: sum(g.weight for g in v.groups if g.group in fingers) for v in mesh.data.vertices}
        hand = mesh.vertex_groups[f'hand_{side}']
        for vi, w in add.items():
            if w > 0:
                hand.add([vi], w, 'ADD')
        for n in names:  # look up by name each time: removing a group renumbers the rest
            mesh.vertex_groups.remove(mesh.vertex_groups[n])


def shrink_textures(size):
    for img in bpy.data.images:
        if img.size[0] > size:
            img.scale(size, size)


def main():
    src, dst, opts = args()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    rig_objs = import_glb(RIG)
    arm = next(o for o in rig_objs if o.type == 'ARMATURE')
    ref_meshes = [o for o in rig_objs if o.type == 'MESH' and o.find_armature() == arm]
    arm.data.pose_position = 'REST'  # the import leaves a clip playing; fit and skin against the T-pose
    bpy.context.view_layer.update()
    mesh = prepare_mesh(os.path.abspath(src), opts['tris'])
    mesh.name = os.path.splitext(os.path.basename(dst))[0]
    tip, shoulder_x = fit_mesh_to_rig(mesh, arm, not opts['no_lift'])
    stretch_reference(ref_meshes, *fit_arms(arm, tip, shoulder_x))
    skin(mesh, arm, ref_meshes, opts['auto'])
    if not opts['fingers']:
        rigid_hands(mesh)
    for o in rig_objs:
        if o.type == 'MESH':
            bpy.data.objects.remove(o)
    shrink_textures(opts['tex'])
    arm.data.pose_position = 'POSE'
    only([mesh, arm], arm)
    os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=os.path.abspath(dst), export_format='GLB', use_selection=True,
                              export_animations=True, export_animation_mode='ACTIONS',
                              export_image_format='JPEG', export_jpeg_quality=85, export_yup=True)
    print(f'saved {dst} ({os.path.getsize(dst) // 1024} KB, {len(bpy.data.actions)} clips)')


if __name__ == '__main__':
    main()
