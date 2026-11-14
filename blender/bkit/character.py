"""Rigid, bone-parented Roblox-like R6 figures. Units are studs; front is -Y.

``hero = r6(shirt="#3476D5"); pose(hero, "wave")``. The six body parts
are separate rounded meshes. This is a presentation rig, not a Roblox avatar importer.
Rotation arguments are degrees, in each bone's local axes.
"""
from dataclasses import dataclass
import math
from pathlib import Path

import bpy
from mathutils import Matrix

from . import compat, materials, modelling
from ._util import link, select


@dataclass
class Character:
    rig: object
    parts: dict
    mouth: object
    objects: list

    def pose(self, name="idle", **rotations):
        return pose(self, name, **rotations)

    def reset(self):
        return reset(self)


POSES = {
    "idle": {"left_arm": (0, 0, 5), "right_arm": (0, 0, -5)},
    "wave": {"right_arm": (0, -12, -90), "head": (0, -6, 0),
             "left_arm": (0, 0, 8)},
    "run": {"left_arm": (48, 0, 8), "right_arm": (-48, 0, -8),
            "left_leg": (-38, 0, 0), "right_leg": (38, 0, 0), "torso": (-8, 0, 0)},
    "cheer": {"left_arm": (0, 0, 90), "right_arm": (0, 0, -90), "head": (-10, 0, 0)},
}


def bone_parent(obj, rig, bone):
    """Rigid-parent an object to a bone without changing its world transform."""
    bpy.context.view_layer.update()
    world = obj.matrix_world.copy()
    obj.parent = rig
    obj.parent_type = "BONE"
    obj.parent_bone = bone
    obj.matrix_parent_inverse = Matrix.Identity(4)
    bpy.context.view_layer.update()
    obj.matrix_world = world
    bpy.context.view_layer.update()
    return obj


def _image_face(image, name):
    if not isinstance(image, bpy.types.Image):
        image = bpy.data.images.load(str(Path(image).expanduser()), check_existing=True)
    mesh = bpy.data.meshes.new(name + "Face")
    # Counter-clockwise from the front: the surface normal points toward -Y.
    mesh.from_pydata([(-.6, -.563, 4.05), (.6, -.563, 4.05),
                      (.6, -.563, 4.95), (-.6, -.563, 4.95)], [], [(0, 1, 2, 3)])
    uv = mesh.uv_layers.new(name="UVMap")
    for loop, value in zip(uv.data, ((0, 0), (1, 0), (1, 1), (0, 1))):
        loop.uv = value
    obj = link(bpy.data.objects.new(name + "Face", mesh))
    mat = materials.principled(name + "Face", "#FFFFFF", reuse=False, roughness=.65)
    tree = mat.node_tree
    tex = tree.nodes.new("ShaderNodeTexImage")
    tex.image = image
    shader = materials.bsdf(mat)
    tree.links.new(tex.outputs["Color"], shader.inputs["Base Color"])
    tree.links.new(tex.outputs["Alpha"], shader.inputs["Alpha"])
    compat.set_blend_transparent(mat)
    mesh.materials.append(mat)
    obj["bkit_face_image"] = True
    return obj


def r6(name="Character", location=(0, 0, 0), skin="#F5CD79", shirt="#377AC8",
       pants="#34445C", face="simple", face_color="#20232A", scale=1.0):
    """Build a grounded five-stud character; return Character(rig, parts, mouth, objects).

    ``face``: 'simple' (shape eyes + animatable mouth), None/False (blank),
    a bpy Image, or a path to an RGBA face image. Shirt colours torso and arms;
    pants colours the legs. ``scale`` uniformly scales the whole figure about its feet.
    ``parts`` keys and bone names: head, torso, left_arm/right_arm, left_leg/right_leg.
    """
    if scale <= 0:
        raise ValueError("scale must be positive")
    arm = bpy.data.armatures.new(name + "Rig")
    rig = link(bpy.data.objects.new(name + "Rig", arm))
    select([rig])
    bpy.ops.object.mode_set(mode="EDIT")
    specs = [("root", (0, 0, 0), (0, 0, .5), None),
             ("torso", (0, 0, 2), (0, 0, 4), "root"),
             ("head", (0, 0, 4), (0, 0, 5), "torso"),
             ("left_arm", (-1, 0, 3.8), (-1, 0, 1.8), "torso"),
             ("right_arm", (1, 0, 3.8), (1, 0, 1.8), "torso"),
             ("left_leg", (-.5, 0, 2), (-.5, 0, 0), "root"),
             ("right_leg", (.5, 0, 2), (.5, 0, 0), "root")]
    for bone_name, head, tail, parent in specs:
        bone = arm.edit_bones.new(bone_name)
        bone.head, bone.tail = head, tail
        if parent:
            bone.parent = arm.edit_bones[parent]
    bpy.ops.object.mode_set(mode="OBJECT")
    rig.show_in_front = True
    for bone in rig.pose.bones:
        bone.rotation_mode = "XYZ"
    parts = {}
    body = [("head", (1.35, 1.1, 1), (0, 0, 4.5), skin),
            ("torso", (2, 1, 2), (0, 0, 3), shirt),
            ("left_arm", (1, 1, 2), (-1.5, 0, 3), shirt),
            ("right_arm", (1, 1, 2), (1.5, 0, 3), shirt),
            ("left_leg", (1, 1, 2), (-.5, 0, 1), pants),
            ("right_leg", (1, 1, 2), (.5, 0, 1), pants)]
    for part_name, size, position, color in body:
        part = modelling.rounded_box(size, radius=.075, location=position,
                                    mat=color, name=name + "_" + part_name)
        bone_parent(part, rig, part_name)
        parts[part_name] = part
    objects, mouth = [rig, *parts.values()], None
    if isinstance(face, str) and face == "simple":
        for side in (-1, 1):
            eye = modelling.sphere(.055, segments=16, rings=8,
                    location=(side * .23, -.563, 4.62), mat=face_color,
                    name=name + "_eye", scale=(1, .25, 1.35))
            objects.append(bone_parent(eye, rig, "head"))
        mouth = modelling.sphere(.14, segments=24, rings=12,
                location=(0, -.566, 4.31), mat=face_color, name=name + "_mouth",
                scale=(1, .13, .22))
        mouth["bkit_closed_scale"] = list(mouth.scale)
        objects.append(bone_parent(mouth, rig, "head"))
    elif face is not None and face is not False:
        objects.append(bone_parent(_image_face(face, name), rig, "head"))
    rig.location = location
    rig.scale = (scale,) * 3
    bpy.context.view_layer.update()
    return Character(rig, parts, mouth, objects)


def reset(character):
    """Reset bone transforms to rest; does not clear animation or move the rig object."""
    rig = getattr(character, "rig", character)
    for bone in rig.pose.bones:
        bone.matrix_basis = Matrix.Identity(4)
    bpy.context.view_layer.update()
    return character


def pose(character, name="idle", rotations=None, **overrides):
    """Reset and apply a named pose or a dict of bone Euler rotations in degrees.

    ``pose(hero, 'wave', head=(0, 10, 0))``; ``pose(hero, {'right_arm': (0, 0, 90)})``.
    """
    if isinstance(name, dict):
        values = dict(name)
    else:
        if name not in POSES:
            raise ValueError(f"unknown pose {name!r}; choose {', '.join(POSES)}")
        values = dict(POSES[name])
    values.update(rotations or {})
    values.update(overrides)
    rig = getattr(character, "rig", character)
    for bone_name in values:
        if bone_name not in rig.pose.bones:
            raise ValueError(f"unknown bone {bone_name!r}")
    reset(character)
    for bone_name, angles in values.items():
        bone = rig.pose.bones[bone_name]
        bone.rotation_mode = "XYZ"
        bone.rotation_euler = tuple(math.radians(a) for a in angles)
    bpy.context.view_layer.update()
    return character


blocky_character = r6
