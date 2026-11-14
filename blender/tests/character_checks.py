"""Blender-only character and animation contracts; call run(output_directory)."""
import math
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def _lowest(objects):
    """Lowest evaluated mesh vertex, including rounded geometry and parent transforms."""
    bpy.context.view_layer.update()
    graph = bpy.context.evaluated_depsgraph_get()
    return min((obj.evaluated_get(graph).matrix_world @ vertex.co).z
               for obj in objects for vertex in obj.evaluated_get(graph).data.vertices)


def _surface_tree(obj, graph):
    evaluated = obj.evaluated_get(graph)
    return BVHTree.FromPolygons(
        [evaluated.matrix_world @ vertex.co for vertex in evaluated.data.vertices],
        [tuple(face.vertices) for face in evaluated.data.polygons])


def run(out):
    import bkit
    from bkit import compat
    assert hasattr(bkit, "character"), "bkit.character is required"
    assert hasattr(bkit, "animation"), "bkit.animation is required"
    character, animation = bkit.character, bkit.animation
    hero = character.r6(name="ContractHero", shirt="#3762CC", pants="#202638")
    bpy.context.view_layer.update()
    assert hero.rig.type == "ARMATURE"
    assert hero.rig.location.length < 1e-6, "rig origin must be the grounded root"
    assert set(hero.parts) == {"head", "torso", "left_arm", "right_arm", "left_leg", "right_leg"}
    assert hero.mouth in hero.objects and hero.rig in hero.objects
    for name, obj in hero.parts.items():
        assert obj.parent == hero.rig and obj.parent_type == "BONE"
        assert obj.parent_bone == name
    low, high = bkit._util.bounds(list(hero.parts.values()))
    assert abs(low.z) < 1e-5 and abs(high.z - 5) < 1e-5, (low, high)
    assert abs(hero.parts["head"].matrix_world.translation.z - 4.5) < 1e-5
    head_low, head_high = bkit._util.bounds(hero.parts["head"])
    assert abs(head_high.x - head_low.x - 1.35) < 1e-5
    assert abs(head_high.y - head_low.y - 1.1) < 1e-5
    for side, sign in (("left_arm", -1), ("right_arm", 1)):
        pivot = hero.rig.data.bones[side].head_local
        assert (pivot - Vector((sign, 0, 3.8))).length < 1e-5
    original = hero.parts["right_arm"].matrix_world.copy()
    character.pose(hero, "wave")
    bpy.context.view_layer.update()
    assert (hero.parts["right_arm"].matrix_world.translation - original.translation).length > 0.1
    character.reset(hero)
    bpy.context.view_layer.update()
    assert (hero.parts["right_arm"].matrix_world.translation - original.translation).length < 1e-5
    for name in ("idle", "wave", "run", "cheer"):
        character.pose(hero, name)
        graph = bpy.context.evaluated_depsgraph_get()
        head_tree = _surface_tree(hero.parts["head"], graph)
        for side in ("left_arm", "right_arm"):
            arm_tree = _surface_tree(hero.parts[side], graph)
            assert not head_tree.overlap(arm_tree), ("head and arm intersect", name, side)
            shoulder = hero.rig.matrix_world @ hero.rig.pose.bones[side].head
            for part in (side, "torso"):
                mesh = hero.parts[part].evaluated_get(graph)
                local_point = mesh.matrix_world.inverted() @ shoulder
                found, nearest, _, _ = mesh.closest_point_on_mesh(local_point)
                assert found and (mesh.matrix_world @ nearest - shoulder).length < .015, (
                    "shoulder contact", name, side, part)
    character.reset(hero)
    animation.walk(hero, start=1, end=25)
    curves = compat.fcurves(hero.rig)
    assert curves and any(c.data_path.startswith("pose.bones") for c in curves)
    assert any(m.type == "CYCLES" for c in curves for m in c.modifiers)
    for curve in curves:
        assert abs(curve.evaluate(1) - curve.evaluate(25)) < 1e-5, curve.data_path
    for frame in range(1, 26):
        bpy.context.scene.frame_set(frame)
        foot_z = _lowest([hero.parts["left_leg"], hero.parts["right_leg"]])
        assert -.015 <= foot_z <= .06, ("walk feet must stay near ground", frame, foot_z)
    hero.rig.animation_data_clear()
    animation.idle(hero, start=30, end=78)
    assert compat.fcurves(hero.rig)
    animation.talk(hero, start=80, end=104)
    animation.mouth_flap(hero, [(0, 0), (0.25, 1), (0.5, 0)], start=110, fps=24)
    mouth_curves = compat.fcurves(hero.mouth)
    assert mouth_curves
    bpy.context.scene.frame_set(116)
    open_scale = hero.mouth.scale.z
    bpy.context.scene.frame_set(110)
    assert open_scale > hero.mouth.scale.z * 2
    animation.key_location(hero.rig, 130, (0, 0, 0), easing="anticipation")
    animation.key_location(hero.rig, 140, (1, 0, 0), easing="overshoot")
    assert any(p.interpolation == "BACK" for c in compat.fcurves(hero.rig) for p in c.keyframe_points)
    animation.squash_stretch(hero.rig, start=145, end=160, amount=0.25)
    bpy.context.scene.frame_set(145)
    assert all(abs(v - 1) < 1e-5 for v in hero.rig.scale)
    camera_data = bpy.data.cameras.new("ContractCamera")
    camera = bpy.data.objects.new("ContractCamera", camera_data)
    bpy.context.scene.collection.objects.link(camera)
    animation.orbit(camera, (0, 0, 2.5), radius=10, start=1, end=25)
    assert len(compat.fcurves(camera)) == 6
    animation.dolly(camera, (0, -10, 4), (0, -6, 3), start=30, end=50, target=(0, 0, 2.5))
    animation.push_in(camera, (0, 0, 2.5), start=60, end=80, amount=0.2)
    image = bpy.data.images.new("FaceRGBA", width=4, height=4, alpha=True)
    textured = character.r6(name="TexturedHero", face=image, location=(7, 0, 0))
    assert textured.mouth is None
    face = next(o for o in textured.objects if o.get("bkit_face_image"))
    assert face.data.uv_layers.active is not None
    assert any(n.type == "TEX_IMAGE" and n.image == image for n in face.data.materials[0].node_tree.nodes)
    Path(out).mkdir(parents=True, exist_ok=True)
    return {"character_animation": "passed", "bones": len(hero.rig.data.bones), "meshes": len(hero.parts)}
