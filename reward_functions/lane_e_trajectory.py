"""
[Lane E] Match the full optimal trajectory: position AND speed.

Hypothesis: Lane B and Lane C are each half of the answer. B rewards being on
the optimal line but says nothing about how fast to be there; C rewards a speed
derived from local curvature at runtime, which is myopic -- it cannot know that
a corner two metres ahead means braking now. Encoding both together gives the
densest possible reward signal.

TRACK: A to Z Speedway (`reInvent2019_wide`, 16.64 m x 107 cm)

Each row below is (x, y, target_speed). The line is the K1999 curvature-
equalised racing line (1500 sweeps, 15.409 m, min radius 0.79 m). The speed at
each point is GLOBALLY optimised, not derived locally: it starts from the
cornering limit sqrt(a_lat / curvature) and is then propagated forwards and
backwards so that every point is reachable under acceleration and braking
limits. That is what lets the car brake *before* a corner it cannot yet see.

Assumptions baked into the speed column: a_lat 6.0 m/s2, a_long 2.0 m/s2,
cap 2.6 m/s. The resulting profile is remarkably flat -- median 2.60, minimum
2.18 -- because on a 107 cm track the racing line opens the corners enough to
carry near-top speed almost everywhere.

>>> RECALIBRATE AFTER THE DAY 2 PHYSICAL RUN. <<<
The speed column depends on the assumed grip. If the real car cannot hold these
speeds, regenerate with a lower a_lat rather than fighting it with the reward.

TUNING:
    ALPHA (position) - raise to hug the line harder, lower if it falls off
    BETA  (speed)    - raise to force the speed profile, lower if it will not
                       converge. Start with speed weighted more weakly than
                       position: getting on the line matters first.

Action space: use the narrow one derived from this trajectory (see
plans/atoz_design.md) -- the line never demands more than 11.8 degrees of
steering, so +/-20 with fine resolution near zero beats +/-28 with coarse steps.
"""
import math

ALPHA = 6.0      # position term
BETA  = 0.8      # speed term

# (x, y, optimal_speed) along the A to Z racing line
TRAJ = [
    (2.56121, 1.09439, 2.60), (2.71254, 1.05987, 2.60),
    (2.86386, 1.02967, 2.60), (3.01518, 1.00288, 2.60),
    (3.16650, 0.97866, 2.60), (3.31783, 0.95625, 2.60),
    (3.46915, 0.93503, 2.60), (3.62047, 0.91446, 2.60),
    (3.77178, 0.89413, 2.60), (3.92311, 0.87379, 2.60),
    (4.07442, 0.85336, 2.60), (4.22574, 0.83291, 2.60),
    (4.37706, 0.81271, 2.60), (4.52838, 0.79323, 2.60),
    (4.67970, 0.77513, 2.60), (4.83102, 0.75923, 2.60),
    (4.98233, 0.74657, 2.60), (5.13365, 0.73832, 2.60),
    (5.28496, 0.73581, 2.60), (5.43627, 0.74049, 2.60),
    (5.58757, 0.75399, 2.60), (5.73887, 0.77815, 2.60),
    (5.89017, 0.81515, 2.60), (6.04146, 0.86776, 2.60),
    (6.19562, 0.94140, 2.60), (6.34770, 1.04011, 2.60),
    (6.47608, 1.15204, 2.60), (6.57624, 1.26766, 2.55),
    (6.65192, 1.38325, 2.48), (6.70675, 1.49640, 2.42),
    (6.74395, 1.60576, 2.37), (6.76625, 1.71073, 2.33),
    (6.77574, 1.81120, 2.29), (6.77394, 1.90739, 2.25),
    (6.76181, 1.99960, 2.21), (6.73982, 2.08808, 2.18),
    (6.70802, 2.17291, 2.23), (6.66681, 2.25432, 2.31),
    (6.61634, 2.33292, 2.39), (6.55608, 2.40951, 2.47),
    (6.48470, 2.48498, 2.55), (6.39988, 2.56028, 2.60),
    (6.29683, 2.63712, 2.60), (6.16432, 2.71915, 2.60),
    (6.01413, 2.79571, 2.60), (5.86224, 2.86031, 2.60),
    (5.71045, 2.91569, 2.60), (5.55871, 2.96489, 2.60),
    (5.40700, 3.01058, 2.60), (5.25529, 3.05525, 2.60),
    (5.10712, 3.10026, 2.60), (4.98074, 3.14159, 2.60),
    (4.87844, 3.17837, 2.60), (4.78276, 3.21664, 2.60),
    (4.68992, 3.25858, 2.60), (4.59811, 3.30528, 2.60),
    (4.50460, 3.35770, 2.60), (4.39563, 3.42423, 2.60),
    (4.26910, 3.50768, 2.60), (4.14019, 3.59801, 2.60),
    (4.01372, 3.69010, 2.60), (3.88819, 3.78299, 2.60),
    (3.76234, 3.87562, 2.60), (3.63489, 3.96694, 2.60),
    (3.50455, 4.05591, 2.60), (3.36997, 4.14142, 2.60),
    (3.23577, 4.21895, 2.60), (3.11715, 4.28024, 2.60),
    (3.01105, 4.32881, 2.60), (2.90404, 4.37148, 2.60),
    (2.78263, 4.41197, 2.60), (2.63878, 4.44886, 2.60),
    (2.48676, 4.47462, 2.60), (2.33505, 4.48659, 2.60),
    (2.18374, 4.48445, 2.60), (2.03285, 4.46767, 2.60),
    (1.88242, 4.43539, 2.60), (1.73249, 4.38620, 2.60),
    (1.58950, 4.32130, 2.60), (1.47717, 4.25587, 2.60),
    (1.39618, 4.19936, 2.60), (1.32582, 4.14279, 2.60),
    (1.26065, 4.08318, 2.60), (1.19689, 4.01694, 2.60),
    (1.13132, 3.93897, 2.60), (1.06081, 3.84093, 2.60),
    (0.98206, 3.70701, 2.60), (0.90794, 3.54184, 2.60),
    (0.85507, 3.37565, 2.60), (0.82205, 3.21388, 2.60),
    (0.80597, 3.05561, 2.60), (0.80505, 2.90065, 2.60),
    (0.81815, 2.74870, 2.60), (0.84459, 2.59962, 2.60),
    (0.88407, 2.45333, 2.60), (0.93660, 2.30986, 2.60),
    (1.00249, 2.16925, 2.60), (1.08238, 2.03166, 2.60),
    (1.17731, 1.89729, 2.60), (1.28883, 1.76650, 2.60),
    (1.41839, 1.64054, 2.60), (1.54718, 1.53609, 2.60),
    (1.64433, 1.46825, 2.60), (1.72384, 1.41864, 2.60),
    (1.79758, 1.37678, 2.60), (1.87269, 1.33775, 2.60),
    (1.97086, 1.29146, 2.60), (2.10735, 1.23474, 2.60),
    (2.25861, 1.18064, 2.60), (2.40990, 1.13428, 2.60),]


def reward_function(params):
    if params['is_offtrack'] or not params['all_wheels_on_track']:
        return 1e-3

    x = params['x']
    y = params['y']
    tw = params['track_width']
    speed = params['speed']

    # nearest trajectory point, and the speed it wants there
    dmin = 1e9
    v_target = 2.0
    for px, py, pv in TRAJ:
        d = (x - px) * (x - px) + (y - py) * (y - py)
        if d < dmin:
            dmin = d
            v_target = pv
    dmin = math.sqrt(dmin)

    # position term x speed term
    reward = math.exp(-ALPHA * (dmin / tw) ** 2)         * math.exp(-BETA * abs(speed - v_target))

    # anti-wobble
    if speed > 1.8 and abs(params['steering_angle']) > 15:
        reward *= 0.7

    return float(max(reward, 1e-3))
