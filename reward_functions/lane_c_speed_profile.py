"""
[Lane C] Curvature lookahead speed profile.

Hypothesis: braking/acceleration TIMING matters more than the racing line.

Reads the upcoming waypoints, measures how much the track direction changes
over the next two segments, and derives a target speed from that. The reward
is highest when the car's actual speed matches the target - so the car learns
to slow down BEFORE a corner and open up on the straights.

Needs no external data: everything comes from params['waypoints'] at runtime.

TUNING: `k` is how far ahead the car looks.
    - exits the track late into a corner  -> raise k to 5 or 6 (brake earlier)
    - slows down far too early            -> lower k to 3
    Change ONLY this value between runs.

CAP must match the action space maximum speed:
    C-p2-v2  max 2.4  ->  targets 2.4 / 2.1 / 1.8 / 1.4
    C-p2-v1  max 2.6  ->  targets 2.6 / 2.2 / 1.8 / 1.4
    C-p2-v3  max 2.8  ->  targets 2.8 / 2.3 / 1.8 / 1.4

Action space (discrete, 12 actions):
    -28/1.3  -20/1.5  -14/1.8  -8/2.1  -4/2.4  0/CAP
      4/2.4    8/2.1   14/1.8  20/1.5  28/1.3  0/1.9
"""
import math


def reward_function(params):
    if params['is_offtrack'] or not params['all_wheels_on_track']:
        return 1e-3

    wps = params['waypoints']
    n = len(wps)
    nx = params['closest_waypoints'][1]
    speed = params['speed']
    steer = abs(params['steering_angle'])
    tw = params['track_width']

    def ang(i, j):
        a = wps[i % n]
        b = wps[j % n]
        return math.atan2(b[1] - a[1], b[0] - a[0])

    # heading change over the next two segments = how sharp the corner ahead is
    k = 4
    delta = math.degrees(ang(nx + k, nx + 2 * k) - ang(nx, nx + k))
    while delta > 180:
        delta -= 360
    while delta < -180:
        delta += 360
    turn = abs(delta)

    # curvature -> target speed  (set the first value to the action-space CAP)
    if turn < 5:
        target = 2.6
    elif turn < 12:
        target = 2.2
    elif turn < 25:
        target = 1.8
    else:
        target = 1.4

    # 1.0 when the speed matches the target exactly, decaying either side
    reward = math.exp(-1.2 * abs(speed - target))

    # keep it on track, but loosely - leave room for a racing line
    if params['distance_from_center'] > 0.42 * tw:
        reward *= 0.4

    # anti-wobble
    if speed > 1.8 and steer > 15:
        reward *= 0.7

    return float(max(reward, 1e-3))
