"""Frame-based keyframing, camera moves and procedural animation.

Angles are degrees in convenience helpers. ``key`` accepts Blender-native values.
``start``/``end`` are inclusive frames. ``mouth_flap`` alone takes seconds.
All curve access uses compat.fcurves, including Blender 5.x slotted actions.
"""
import math

import bpy
from mathutils import Vector

from . import compat
from ._util import look_at, spherical

_EASING = {
    "linear": ("LINEAR", "AUTO"), "constant": ("CONSTANT", "AUTO"),
    "smooth": ("BEZIER", "AUTO"), "bezier": ("BEZIER", "AUTO"),
    "ease_in": ("QUAD", "EASE_IN"), "ease_out": ("QUAD", "EASE_OUT"),
    "ease_in_out": ("QUAD", "EASE_IN_OUT"),
    "overshoot": ("BACK", "EASE_OUT"), "anticipation": ("BACK", "EASE_IN"),
}


def easing(obj, kind="smooth", frame=None, data_path=None):
    """Set interpolation on active-action keys, optionally one frame/property.

    'overshoot' is a BACK ease-out; 'anticipation' is a BACK ease-in.
    Segment interpolation belongs to its starting key, as in Blender's editor.
    """
    if kind not in _EASING:
        raise ValueError(f"unknown easing {kind!r}; choose {', '.join(_EASING)}")
    interpolation, direction = _EASING[kind]
    owner = getattr(obj, "id_data", obj)
    for curve in compat.fcurves(owner):
        if data_path is not None and curve.data_path != data_path:
            continue
        for point in curve.keyframe_points:
            if frame is not None and abs(point.co.x - frame) > 1e-4:
                continue
            point.interpolation = interpolation
            point.easing = direction
            if interpolation == "BEZIER":
                point.handle_left_type = point.handle_right_type = "AUTO_CLAMPED"
            if interpolation == "BACK":
                point.back = 1.70158
        curve.update()
    return obj


def key(obj, data_path, frame, value=None, easing="smooth", index=-1):
    """Set an RNA property and insert a key. Works for objects and pose bones.

    ``key(bone, 'rotation_euler', 12, (0, .5, 0))`` uses radians.
    Nested paths may be keyed when the property already has its desired value.
    """
    if value is not None:
        if index < 0:
            setattr(obj, data_path, value)
        else:
            getattr(obj, data_path)[index] = value
    obj.keyframe_insert(data_path=data_path, frame=frame, index=index)
    path = obj.path_from_id(data_path) if hasattr(obj, "path_from_id") else data_path
    globals()["easing"](obj, easing, frame=frame, data_path=path)
    return obj


def key_location(obj, frame, value, easing="smooth"):
    return key(obj, "location", frame, value, easing)


def key_rotation(obj, frame, degrees, easing="smooth"):
    obj.rotation_mode = "XYZ"
    return key(obj, "rotation_euler", frame, tuple(math.radians(v) for v in degrees), easing)


def key_scale(obj, frame, value, easing="smooth"):
    if isinstance(value, (float, int)):
        value = (value,) * 3
    return key(obj, "scale", frame, value, easing)


def key_pose(character, frame, easing="smooth"):
    """Key all pose-bone locations, rotations and scales at their current values."""
    rig = getattr(character, "rig", character)
    for bone in rig.pose.bones:
        for path in ("location", "rotation_euler", "scale"):
            key(bone, path, frame, easing=easing)
    return character


def _range(start, end):
    if end <= start:
        raise ValueError("end must be greater than start")


def _cycles(obj, paths=None):
    for curve in compat.fcurves(obj):
        if paths is None or curve.data_path in paths:
            if not any(mod.type == "CYCLES" for mod in curve.modifiers):
                curve.modifiers.new("CYCLES")


def squash_stretch(obj, start=1, end=16, amount=.2, easing="smooth"):
    """Anticipation, stretch and settle about the object's origin; approximate volume conserved.

    A character rig has its origin at its feet, so scaling keeps it grounded.
    amount must be between 0 and 1; the object's current scale is the rest scale.
    """
    _range(start, end)
    if not 0 <= amount < 1:
        raise ValueError("amount must be in [0, 1)")
    obj = getattr(obj, "rig", obj)
    rest = tuple(obj.scale)
    for t, height in ((0, 1), (.25, 1 - amount), (.55, 1 + amount), (1, 1)):
        width = 1 / math.sqrt(height)
        key_scale(obj, start + (end - start) * t,
                  (rest[0] * width, rest[1] * width, rest[2] * height), easing)
    return obj


def _target(target):
    bpy.context.view_layer.update()
    if hasattr(target, "matrix_world"):
        return target.matrix_world.translation.copy()
    return Vector(target)


def orbit(camera, target=(0, 0, 0), radius=10, start=1, end=121,
          azimuth=(0, 360), elevation=15, steps=32, easing="linear"):
    """Orbit a camera around a fixed target; key location and continuous Euler orientation.

    Azimuth zero is in front (-Y); positive angles move toward +X. Parentless
    cameras are expected. ``azimuth`` may be an angle pair or total degrees.
    """
    _range(start, end)
    if radius <= 0 or steps < 2:
        raise ValueError("radius must be positive and steps at least 2")
    center = _target(target)
    if isinstance(azimuth, (float, int)):
        azimuth = (0, azimuth)
    previous = None
    camera.rotation_mode = "XYZ"
    for i in range(steps + 1):
        t = i / steps
        frame = start + (end - start) * t
        camera.location = spherical(center, radius, azimuth[0] + (azimuth[1] - azimuth[0]) * t, elevation)
        look_at(camera, center)
        if previous is not None:
            camera.rotation_euler.make_compatible(previous)
        previous = camera.rotation_euler.copy()
        key(camera, "location", frame, easing=easing)
        key(camera, "rotation_euler", frame, easing=easing)
    return camera


def dolly(camera, from_location, to_location, start=1, end=48, target=None, easing="smooth"):
    """Move a camera between two positions, optionally keeping a target in view."""
    _range(start, end)
    camera.rotation_mode = "XYZ"
    center = _target(target) if target is not None else None
    previous = None
    # Several target-facing keys maintain the sight line throughout a lateral move.
    steps = 16 if center is not None else 1
    a, b = Vector(from_location), Vector(to_location)
    for i in range(steps + 1):
        t = i / steps
        frame = start + (end - start) * t
        key_location(camera, frame, a.lerp(b, t), easing)
        if center is not None:
            look_at(camera, center)
            if previous is not None:
                camera.rotation_euler.make_compatible(previous)
            previous = camera.rotation_euler.copy()
            key(camera, "rotation_euler", frame, easing=easing)
    return camera


def push_in(camera, target=(0, 0, 0), start=1, end=48, amount=.25, easing="smooth"):
    """Move ``amount`` of the current distance toward a fixed target (0 < amount < 1)."""
    if not 0 < amount < 1:
        raise ValueError("amount must be between 0 and 1")
    center = _target(target)
    beginning = camera.location.copy()
    return dolly(camera, beginning, beginning.lerp(center, amount), start, end, center, easing)


def walk(character, start=1, end=25, stride=32, arm_swing=24, bounce=.025, steps=24, loop=True):
    """In-place one-cycle R6 walk; stride/arm_swing degrees, bounce studs.

    Leg/arm swings alternate. Evaluated rounded feet set the root height at
    each sample, then add a gentle bounce; the last frame matches the first.
    CYCLES modifiers repeat the keyed bones. Translate the rig separately for travel.
    """
    _range(start, end)
    if steps < 4:
        raise ValueError("steps must be at least 4")
    if bounce < 0:
        raise ValueError("bounce must be nonnegative")
    from .character import reset
    rig = getattr(character, "rig", character)
    reset(character)
    scene = bpy.context.scene
    previous_frame = scene.frame_current + scene.frame_subframe
    paths = set()
    for i in range(steps + 1):
        t = i / steps
        phase = math.tau * t
        frame = start + (end - start) * t
        for name, amplitude, sign in (("left_leg", stride, 1), ("right_leg", stride, -1),
                                     ("left_arm", arm_swing, -1), ("right_arm", arm_swing, 1)):
            bone = rig.pose.bones[name]
            key_rotation(bone, frame, (amplitude * sign * math.sin(phase), 0, 0))
            paths.add(bone.path_from_id("rotation_euler"))
        root = rig.pose.bones["root"]
        # Evaluate at this sample's actual time. Merely assigning future
        # keys leaves the dependency graph at the scene's previous frame.
        whole_frame = math.floor(frame)
        scene.frame_set(whole_frame, subframe=frame - whole_frame)
        # Measure the actual rounded mesh, not its empty enclosing corners.
        current_height = root.location.y
        bpy.context.view_layer.update()
        graph = bpy.context.evaluated_depsgraph_get()
        parts = getattr(character, "parts", None)
        legs = ([parts["left_leg"], parts["right_leg"]] if parts is not None else
                [obj for obj in rig.children if obj.type == "MESH" and
                 obj.parent_type == "BONE" and obj.parent_bone in ("left_leg", "right_leg")])
        if not legs:
            raise ValueError("walk requires rigid bone-parented left_leg/right_leg meshes")
        lowest = math.inf
        for leg in legs:
            evaluated = leg.evaluated_get(graph)
            for vertex in evaluated.data.vertices:
                lowest = min(lowest, (evaluated.matrix_world @ vertex.co).z)
        # Root local Y is world Z for this rig. Account for object scale when
        # expressing the world-space contact correction in root-local units.
        vertical = (rig.matrix_world.to_3x3() @ root.bone.matrix_local.to_3x3() @ Vector((0, 1, 0))).z
        if vertical <= 1e-8:
            raise ValueError("walk requires an upright rig with positive vertical scale")
        ground = rig.matrix_world.translation.z
        height = current_height + (ground - lowest) / vertical + bounce * (1 - math.cos(phase * 2)) / 2
        key(root, "location", frame, (0, height, 0))
        paths.add(root.path_from_id("location"))
    if loop:
        _cycles(rig, paths)
    whole_frame = math.floor(previous_frame)
    scene.frame_set(whole_frame, subframe=previous_frame - whole_frame)
    return character


def idle(character, start=1, end=97, amount=2, steps=16, loop=True):
    """Gentle breathing, head drift and relaxed arms. amount is degrees of head sway."""
    _range(start, end)
    if steps < 4:
        raise ValueError("steps must be at least 4")
    from .character import reset
    rig = getattr(character, "rig", character)
    reset(character)
    paths = set()
    for i in range(steps + 1):
        phase = math.tau * i / steps
        frame = start + (end - start) * i / steps
        head = rig.pose.bones["head"]
        key_rotation(head, frame, (amount * .5 * math.sin(phase), amount * math.sin(phase), 0))
        paths.add(head.path_from_id("rotation_euler"))
        torso = rig.pose.bones["torso"]
        key(torso, "scale", frame, (1, 1 + .008 * math.sin(phase), 1))
        paths.add(torso.path_from_id("scale"))
        for side, sign in (("left_arm", -1), ("right_arm", 1)):
            bone = rig.pose.bones[side]
            key_rotation(bone, frame, (math.sin(phase) * amount, 0, sign * -4))
            paths.add(bone.path_from_id("rotation_euler"))
    if loop:
        _cycles(rig, paths)
    return character


def talk(character, start=1, end=49, amount=12, beats=3):
    """Key alternating small presenting arm gestures and nods; mouth is keyed separately."""
    _range(start, end)
    if beats < 1:
        raise ValueError("beats must be at least one")
    rig = getattr(character, "rig", character)
    for i in range(beats * 2 + 1):
        frame = start + (end - start) * i / (beats * 2)
        active = i % 2
        for side, sign in (("left_arm", -1), ("right_arm", 1)):
            key_rotation(rig.pose.bones[side], frame,
                         (-amount * active, 0, -sign * (5 + amount * active)))
        key_rotation(rig.pose.bones["head"], frame, (-amount * .25 * active, 0, 0))
    return character


def mouth_flap(character, samples, start=1, fps=None, strength=3.5, easing="linear"):
    """Animate a shape mouth from ``[(seconds, openness_0_to_1), ...]``.

    Uses the scene's effective FPS when omitted. Image faces have no shape mouth.
    Values outside 0..1 and non-increasing timestamps are rejected.
    """
    mouth = getattr(character, "mouth", character)
    if mouth is None:
        raise ValueError("mouth_flap requires a character with face='simple'")
    scene = bpy.context.scene
    fps = fps if fps is not None else scene.render.fps / scene.render.fps_base
    if fps <= 0 or strength < 0:
        raise ValueError("fps must be positive and strength non-negative")
    samples = list(samples)
    previous = -math.inf
    for seconds, openness in samples:
        if seconds < 0 or seconds <= previous or not 0 <= openness <= 1:
            raise ValueError("samples need increasing nonnegative seconds and openness in [0, 1]")
        previous = seconds
    rest = tuple(mouth.get("bkit_closed_scale", tuple(mouth.scale)))
    for seconds, openness in samples:
        key_scale(mouth, start + seconds * fps,
                  (rest[0] * (1 - .15 * openness), rest[1], rest[2] * (1 + strength * openness)), easing)
    return character


set_easing = easing
location = key_location
rotation = key_rotation
scale = key_scale
