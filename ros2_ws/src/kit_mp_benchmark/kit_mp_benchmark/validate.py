"""Validity checks for a planned trajectory.

A trajectory only counts for the competition if ALL of these pass:
  * collision-free at every (densified) waypoint against the competition scene,
  * reaches the goal within tolerance,
  * respects the LOCKED FR3 position / velocity / acceleration / jerk limits.

The scorer supplies the MoveItPy robot_model and planning scene so the collision
check uses exactly the geometry the robot will face.
"""
import os

import numpy as np
import yaml
from ament_index_python.packages import get_package_share_directory
from moveit.core.robot_state import RobotState


def load_locked_limits():
    path = os.path.join(
        get_package_share_directory("kit_mp_benchmark"),
        "config", "fr3_joint_limits_locked.yaml",
    )
    with open(path, "r") as f:
        return yaml.safe_load(f)


def execution_time(traj_msg) -> float:
    """Total trajectory duration in seconds (the competition metric)."""
    pts = traj_msg.joint_trajectory.points
    if not pts:
        return float("inf")
    t = pts[-1].time_from_start
    return t.sec + t.nanosec * 1e-9


def _seconds(duration):
    return duration.sec + duration.nanosec * 1e-9


def check_limits(traj_msg, limits) -> dict:
    """Check position/velocity/acceleration/jerk against the locked limits.

    FAIL CLOSED: if the trajectory carries no velocity or acceleration data we
    cannot prove it is within limits, so we mark it a violation rather than a
    silent pass. This is a real-robot safety gate: libfranka aborts trajectories
    that exceed velocity/acceleration/jerk limits, so an unverifiable trajectory
    must NOT be cleared for hardware.
    """
    jt = traj_msg.joint_trajectory
    names = list(jt.joint_names)
    ratio = limits.get("tolerance_ratio", 1.02)
    pos_lim = limits["position_limits"]
    jlim = limits["joints"]

    violations = []
    have_vel = any(pt.velocities for pt in jt.points)
    have_acc = any(pt.accelerations for pt in jt.points)
    if not have_vel:
        violations.append("FAIL-CLOSED: no velocity data in trajectory")
    if not have_acc:
        violations.append("FAIL-CLOSED: no acceleration data (cannot verify jerk)")

    prev_acc, prev_t = None, None
    for k, pt in enumerate(jt.points):
        t = _seconds(pt.time_from_start)
        for i, name in enumerate(names):
            p = pt.positions[i] if pt.positions else 0.0
            lo, hi = pos_lim[name]
            if not (lo - 1e-3 <= p <= hi + 1e-3):
                violations.append(f"pos {name}={p:.3f} outside [{lo},{hi}] @pt{k}")
            if pt.velocities:
                v = abs(pt.velocities[i])
                if v > jlim[name]["max_velocity"] * ratio:
                    violations.append(f"vel {name}={v:.3f} @pt{k}")
            if pt.accelerations:
                a = abs(pt.accelerations[i])
                if a > jlim[name]["max_acceleration"] * ratio:
                    violations.append(f"acc {name}={a:.3f} @pt{k}")
        # jerk from finite-difference of acceleration (valid because the pipeline
        # applies Ruckig jerk-limited smoothing, so acceleration is continuous)
        if prev_acc is not None and pt.accelerations and prev_t is not None:
            dt = t - prev_t
            if dt > 1e-6:
                for i, name in enumerate(names):
                    jrk = abs(pt.accelerations[i] - prev_acc[i]) / dt
                    if jrk > jlim[name]["max_jerk"] * ratio:
                        violations.append(f"jerk {name}={jrk:.1f} @pt{k}")
        if pt.accelerations:
            prev_acc, prev_t = list(pt.accelerations), t

    return {
        "ok": len(violations) == 0,
        "violations": violations[:20],
        "velocity_data": have_vel,
        "acceleration_data": have_acc,
    }


def _densify(points, max_step=0.02):
    """Linear-interpolate joint waypoints so no joint moves > max_step between checks."""
    dense = []
    for a, b in zip(points[:-1], points[1:]):
        pa, pb = np.array(a.positions), np.array(b.positions)
        steps = max(1, int(np.ceil(np.max(np.abs(pb - pa)) / max_step)))
        for s in range(steps):
            dense.append(pa + (pb - pa) * (s / steps))
    dense.append(np.array(points[-1].positions))
    return dense


def check_collision(traj_msg, scene, robot_model, group, max_step=0.02):
    """Return (ok, first_colliding_index). Densifies between waypoints."""
    states = _densify(traj_msg.joint_trajectory.points, max_step)
    rs = RobotState(robot_model)
    for idx, q in enumerate(states):
        rs.set_joint_group_positions(group, list(q))
        rs.update()
        if scene.is_state_colliding(robot_state=rs, joint_model_group_name=group):
            return False, idx
    return True, -1


def _quat_angle(q1, q2):
    d = abs(float(np.dot(q1, q2)))
    d = min(1.0, d)
    return 2.0 * np.arccos(d)


def check_goal(traj_msg, task, robot_model) -> dict:
    """Goal-reached check: joint distance or end-effector pose distance."""
    final = traj_msg.joint_trajectory.points[-1].positions
    if task.is_pose_goal:
        rs = RobotState(robot_model)
        rs.set_joint_group_positions(task.group, list(final))
        rs.update()
        tf = np.asarray(rs.get_global_link_transform(task.tip_link))
        pos = tf[:3, 3]
        goal = np.array(task.goal_pose)
        perr = float(np.linalg.norm(pos - goal[:3]))
        # orientation from rotation matrix -> quaternion
        R = tf[:3, :3]
        qw = np.sqrt(max(0.0, 1 + R[0, 0] + R[1, 1] + R[2, 2])) / 2
        qx = (R[2, 1] - R[1, 2]) / (4 * qw) if qw > 1e-6 else 0.0
        qy = (R[0, 2] - R[2, 0]) / (4 * qw) if qw > 1e-6 else 0.0
        qz = (R[1, 0] - R[0, 1]) / (4 * qw) if qw > 1e-6 else 0.0
        oerr = _quat_angle(np.array([qx, qy, qz, qw]), goal[3:])
        ok = perr <= task.position_tolerance and oerr <= task.orientation_tolerance
        return {"ok": ok, "position_error": perr, "orientation_error": oerr}
    else:
        err = float(np.max(np.abs(np.array(final) - np.array(task.goal_joints))))
        return {"ok": err <= task.joint_tolerance, "joint_error": err}
