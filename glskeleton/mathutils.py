"""numpy-based matrix utilities that replace PyGLM.

Conventions:
- All matrices are 4x4 row-major ``np.ndarray`` (float32).
- Pass them to OpenGL with ``transpose=GL_TRUE``.
- Rotation helpers take angles in **radians** (matching ``glm.rotate`` / ``glm.rotateY``).
- ``perspective`` takes the field of view in **degrees** (matching ``glm.perspective``;
  it converts to radians internally).
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

Vec3 = Sequence[float]
Mat4 = np.ndarray  # shape (4, 4), dtype float32


def identity() -> Mat4:
    """Return the 4x4 identity matrix."""
    return np.eye(4, dtype=np.float32)


def translation(x: float, y: float, z: float) -> Mat4:
    """Translation matrix. Equivalent to ``glm.translate(glm.mat4(1.0), glm.vec3(x, y, z))``."""
    mat = np.eye(4, dtype=np.float32)
    mat[:3, 3] = (x, y, z)
    return mat


def scaling(x: float, y: float, z: float) -> Mat4:
    """Scaling matrix."""
    mat = np.eye(4, dtype=np.float32)
    mat[0, 0] = x
    mat[1, 1] = y
    mat[2, 2] = z
    return mat


def rotation(angle_rad: float, axis: Vec3) -> Mat4:
    """Rotation matrix around an arbitrary axis. ``angle_rad`` is in radians.

    Equivalent to ``glm.rotate(angle, axis)``.
    """
    axis_arr = np.asarray(axis, dtype=np.float32)
    norm = float(np.linalg.norm(axis_arr))
    if norm == 0.0:
        return identity()
    axis_arr = axis_arr / norm

    c, s = float(np.cos(angle_rad)), float(np.sin(angle_rad))
    x, y, z = float(axis_arr[0]), float(axis_arr[1]), float(axis_arr[2])

    mat = np.eye(4, dtype=np.float32)
    mat[:3, :3] = np.array(
        [
            [c + x * x * (1 - c), x * y * (1 - c) - z * s, x * z * (1 - c) + y * s],
            [y * x * (1 - c) + z * s, c + y * y * (1 - c), y * z * (1 - c) - x * s],
            [z * x * (1 - c) - y * s, z * y * (1 - c) + x * s, c + z * z * (1 - c)],
        ],
        dtype=np.float32,
    )
    return mat


def rotation_x(angle_rad: float) -> Mat4:
    """Rotation matrix around the X axis. ``angle_rad`` is in radians."""
    return rotation(angle_rad, (1.0, 0.0, 0.0))


def rotation_y(angle_rad: float) -> Mat4:
    """Rotation matrix around the Y axis. ``angle_rad`` is in radians."""
    return rotation(angle_rad, (0.0, 1.0, 0.0))


def rotation_z(angle_rad: float) -> Mat4:
    """Rotation matrix around the Z axis. ``angle_rad`` is in radians."""
    return rotation(angle_rad, (0.0, 0.0, 1.0))


def rotate_vector(v: Vec3, angle_rad: float, axis: Vec3) -> np.ndarray:
    """Rotate a 3D vector around an arbitrary axis (Rodrigues' formula).

    ``angle_rad`` is in radians.
    """
    axis_arr = np.asarray(axis, dtype=np.float32)
    norm = float(np.linalg.norm(axis_arr))
    if norm == 0.0:
        return np.asarray(v, dtype=np.float32)
    axis_arr = axis_arr / norm

    v_arr = np.asarray(v, dtype=np.float32)
    c, s = float(np.cos(angle_rad)), float(np.sin(angle_rad))
    return (
        v_arr * c
        + np.cross(axis_arr, v_arr) * s
        + axis_arr * float(np.dot(axis_arr, v_arr)) * (1 - c)
    )


def rotate_y_vector(v: Vec3, angle_rad: float) -> np.ndarray:
    """Rotate a 3D vector around the Y axis. Equivalent to ``glm.rotateY(v, angle)``."""
    return rotate_vector(v, angle_rad, (0.0, 1.0, 0.0))


def perspective(fov_deg: float, aspect: float, near: float, far: float) -> Mat4:
    """Perspective projection matrix.

    ``fov_deg`` is in degrees. Equivalent to
    ``glm.perspective(glm.radians(fov_deg), aspect, near, far)``.
    """
    f = 1.0 / float(np.tan(np.radians(fov_deg) / 2.0))
    mat = np.zeros((4, 4), dtype=np.float32)
    mat[0, 0] = f / aspect
    mat[1, 1] = f
    mat[2, 2] = (far + near) / (near - far)
    mat[2, 3] = (2.0 * far * near) / (near - far)
    mat[3, 2] = -1.0
    return mat


def look_at(eye: Vec3, center: Vec3, up: Vec3) -> Mat4:
    """View matrix. Equivalent to ``glm.lookAt(eye, center, up)``."""
    eye_arr = np.asarray(eye, dtype=np.float32)
    center_arr = np.asarray(center, dtype=np.float32)
    up_arr = np.asarray(up, dtype=np.float32)

    f = center_arr - eye_arr
    f = f / float(np.linalg.norm(f))
    s = np.cross(f, up_arr)
    s = s / float(np.linalg.norm(s))
    u = np.cross(s, f)

    mat = np.eye(4, dtype=np.float32)
    mat[0, :3] = s
    mat[1, :3] = u
    mat[2, :3] = -f
    mat[0, 3] = -float(np.dot(s, eye_arr))
    mat[1, 3] = -float(np.dot(u, eye_arr))
    mat[2, 3] = float(np.dot(f, eye_arr))
    return mat
