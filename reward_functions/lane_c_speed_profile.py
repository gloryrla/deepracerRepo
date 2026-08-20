"""
[Lane C] Curvature lookahead speed profile.

Hypothesis: braking/acceleration TIMING matters more than the racing line.

TRACK: A to Z Speedway (`reInvent2019_wide`, 16.64 m x 107 cm).
Needs no coordinates -- everything is read from params['waypoints'] at runtime,
so this file stays valid if the track ever changes. Only the numbers below were
calibrated against A to Z's actual geometry.

--- CALIBRATION (measured on A to Z's 110 waypoints, mean spacing 0.150 m) ---

LOOKAHEAD.  The old k=4 was too short: it looked 2*k*0.150 = 1.20 m ahead,
which at 2.5 m/s is only 0.48 s of warning. Braking 2.5 -> 1.5 m/s at ~4 m/s^2
needs about 0.25 s and half a metre, so k=4 left almost no margin and the car
would enter corners hot. k=6 looks 1.80 m / 0.72 s ahead -- enough to brake
early and still accelerate out. Measured distribution of the `turn` metric:

        k   ahead    @2.5m/s   p50    p75    p90    max
        4   1.20 m    0.48 s   10.6   34.7   39.3   51.1
        6   1.80 m    0.72 s   20.9   43.5   59.0   67.8
        8   2.40 m    0.96 s   30.0   53.6   74.1   78.6

THRESHOLDS.  The old 5/12/25 boundaries were set by guesswork and were far too
low for this metric: at k=6 the MEDIAN turn is 20.9 degrees, so `turn < 5`
almost never fired and the car essentially never received the top-speed target.
The 15/35/52 boundaries below sit near the 40th/65th/85th percentiles, which
puts roughly 40% of the lap at full speed and 15% at the slow tier.

TUNING: change ONE value between runs.
    - enters corners hot / runs wide  -> k = 8 (brake earlier)
    - slows down far too early        -> k = 5
CAP must match the action space maximum speed:
    C-v2 max 2.4 -> targets 2.4 / 2.1 / 1.9 / 1.8
    C-v1 max 2.6 -> targets 2.6 / 2.2 / 2.0 / 1.9   (this file)
    C-v3 max 2.8 -> targets 2.8 / 2.4 / 2.1 / 1.9

SLOW TIER RAISED (2026-08-19).  The slowest target used to be 1.5 m/s, which is
well below what the geometry requires: the physical cornering limit is 2.18 m/s
on the racing line and about 1.9 m/s even on the centreline. The old value
trained the car to brake harder than necessary and capped its lap time.

Action space (discrete, 12 actions):
    -28/1.4  -20/1.6  -14/1.9  -8/2.2  -4/2.4  0/CAP
      4/2.4    8/2.2   14/1.9  20/1.6  28/1.4  0/2.0
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
    k = 6
    delta = math.degrees(ang(nx + k, nx + 2 * k) - ang(nx, nx + k))
    while delta > 180:
        delta -= 360
    while delta < -180:
        delta += 360
    turn = abs(delta)

    # curvature -> target speed  (first value must equal the action-space CAP)
    if turn < 15:
        target = 2.6
    elif turn < 35:
        target = 2.2
    elif turn < 52:
        target = 2.0
    else:
        target = 1.9

    # 1.0 when the speed matches the target exactly, decaying either side
    reward = math.exp(-1.2 * abs(speed - target))

    # keep it on track, but loosely - leave room for a racing line
    if params['distance_from_center'] > 0.42 * tw:
        reward *= 0.4

    # anti-wobble
    if speed > 1.8 and steer > 15:
        reward *= 0.7

    return float(max(reward, 1e-3))
