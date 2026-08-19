"""
[Lane B] Follow the precomputed K1999 optimal racing line.

Hypothesis: the optimal trajectory is what makes the lap time.

The 71 coordinates below are the K1999 racing line for `reinvent_base`
(= the re:Invent 2018 track), taken verbatim from:
    github.com/cdthompson/deepracer-k1999-race-lines
    racelines/reinvent_base-400-4-2019-10-11-161903.py

The reward is a Gaussian on the distance from the car to the nearest point on
that line, normalised by track width, plus a heading-alignment term.

IMPORTANT: there is deliberately NO centerline reward here. The racing line
leaves the centerline on purpose (In-Out-In), so a centerline term would fight
this one and the policy would not converge.

TUNING: the `-6.0` coefficient is how strictly the car must hug the line.
    - car clings to the line and falls off  -> soften to -4.0
    - car wanders off the line              -> tighten to -8.0

CAP must match the action space maximum speed:
    B-p2-v2 max 2.2  |  B-p2-v1 max 2.4  |  B-p2-v3 max 2.6

Action space (discrete, 10 actions):
    -24/1.3  -16/1.6  -10/1.9  -5/2.1  0/CAP
      5/2.1   10/1.9   16/1.6  24/1.3  0/1.7
"""
import math

RACE_LINE = [
    [2.88738855, 0.72646774], [3.16759122, 0.70478649], [3.45517317, 0.69217863],
    [3.75325158, 0.68581005], [4.07281434, 0.68360819], [4.50000223, 0.68376092],
    [4.54999507, 0.68377879], [5.11738115, 0.69080411], [5.44798256, 0.71123220],
    [5.71126558, 0.74223470], [5.94137211, 0.78496462], [6.14912710, 0.84078035],
    [6.33675893, 0.91066736], [6.50351669, 0.99483994], [6.64762588, 1.09336367],
    [6.76714849, 1.20640158], [6.85790417, 1.33508669], [6.92193762, 1.47646609],
    [6.96026824, 1.62797346], [6.96689958, 1.78880720], [6.92976742, 1.95515434],
    [6.85379617, 2.11910271], [6.72693273, 2.26841633], [6.56582731, 2.39790650],
    [6.38075512, 2.50632652], [6.18037171, 2.59602650], [5.97126499, 2.67207187],
    [5.75829177, 2.74110301], [5.55841177, 2.81013238], [5.36004947, 2.88360578],
    [5.16333131, 2.96218803], [4.96844903, 3.04682634], [4.77552032, 3.13832543],
    [4.58462440, 3.23745280], [4.39562481, 3.34419701], [4.20825035, 3.45789343],
    [4.02216522, 3.57740375], [3.83712807, 3.70184192], [3.68186141, 3.80970389],
    [3.52529227, 3.91179837], [3.36674073, 4.00606413], [3.20532486, 4.09041474],
    [3.04012520, 4.16335643], [2.87024421, 4.22393077], [2.69486335, 4.27162279],
    [2.51319321, 4.30602365], [2.32452568, 4.32672382], [2.12696309, 4.33080298],
    [1.91810508, 4.31381212], [1.69471913, 4.26740868], [1.45416273, 4.17400849],
    [1.21119005, 4.00653223], [1.01922953, 3.74402202], [0.92220549, 3.42050544],
    [0.88926604, 3.10443889], [0.89600747, 2.82076036], [0.92404943, 2.56281185],
    [0.96605253, 2.32460305], [1.01802833, 2.11228544], [1.08079017, 1.91512981],
    [1.15513698, 1.73107571], [1.24162317, 1.56014807], [1.34112998, 1.40323884],
    [1.45472589, 1.26109320], [1.58653095, 1.13641183], [1.74472608, 1.03228688],
    [1.92655529, 0.94305481], [2.13282228, 0.86779425], [2.36411252, 0.80679887],
    [2.61751276, 0.75992145],
]


def reward_function(params):
    if params['is_offtrack'] or not params['all_wheels_on_track']:
        return 1e-3

    x = params['x']
    y = params['y']
    tw = params['track_width']

    dmin = 1e9
    for px, py in RACE_LINE:
        d = math.hypot(x - px, y - py)
        if d < dmin:
            dmin = d

    # distance-to-racing-line reward, normalised by track width
    reward = math.exp(-6.0 * (dmin / tw) ** 2)

    # heading alignment with the upcoming track direction
    wps = params['waypoints']
    n = len(wps)
    p0 = wps[params['closest_waypoints'][0]]
    p1 = wps[(params['closest_waypoints'][1] + 1) % n]
    track_dir = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
    diff = abs(track_dir - params['heading'])
    if diff > 180:
        diff = 360 - diff

    if diff <= 10:
        reward *= 1.2
    elif diff > 25:
        reward *= 0.6

    # anti-wobble
    if params['speed'] > 1.8 and abs(params['steering_angle']) > 15:
        reward *= 0.7

    return float(max(reward, 1e-3))
