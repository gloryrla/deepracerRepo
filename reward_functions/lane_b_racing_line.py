"""
[Lane B] Follow the computed K1999 optimal racing line.

Hypothesis: the optimal trajectory is what makes the lap time.

TRACK: A to Z Speedway  (world name `reInvent2019_wide`, 16.64 m x 107 cm)
       Confirmed 2026-08-19 by measuring the physical track: white-edge to
       white-edge was over 1 m, which rules out re:Invent 2018 (76 cm).

The 110 coordinates below were computed for THIS track by curvature
equalisation (the K1999 method) over the 110 centreline waypoints from
aws-deepracer-community/deepracer-log-guru, run for 100 sweeps with a 0.15 m
car-centre clearance from the white line. Result: 16.277 m line (centreline is
16.635 m) with a minimum corner radius of 0.78 m, up from the centreline's
0.61 m -- a wider, more forgiving apex, which is what the averaged-time
scoring rule rewards.

>>> DO NOT reuse these coordinates on re:Invent 2018. <<<
They are absolute track coordinates. On a different track the reward would be
paid for hugging a line that is off the asphalt.

TUNING: the -6.0 coefficient is how strictly the car must hug the line.
    - car clings to the line and falls off  -> soften to -4.0
    - car wanders off the line              -> tighten to -8.0
"""
import math

# K1999 racing line for A to Z Speedway (reInvent2019_wide)
RACE_LINE = [
    [2.561243, 1.029817], [2.712558, 1.023782], [2.863866, 1.022275],
    [3.015176, 1.023935], [3.166485, 1.027735], [3.317795, 1.032928],
    [3.469103, 1.038975], [3.620411, 1.045448], [3.771719, 1.051958],
    [3.923028, 1.058087], [4.074336, 1.063362], [4.225645, 1.067269],
    [4.376956, 1.069297], [4.528267, 1.069007], [4.679579, 1.066111],
    [4.830892, 1.060551], [4.982207, 1.052559], [5.133521, 1.042703],
    [5.284837, 1.031908], [5.436152, 1.021455], [5.587466, 1.012952],
    [5.738779, 1.008295], [5.890090, 1.009625], [6.041396, 1.019302],
    [6.193246, 1.040047], [6.343182, 1.074386], [6.485067, 1.123014],
    [6.617511, 1.186759], [6.739375, 1.266559], [6.848376, 1.362822],
    [6.941399, 1.475077], [7.014907, 1.601705], [7.065440, 1.739791],
    [7.090165, 1.885171], [7.087397, 2.032720], [7.056971, 2.176843],
    [7.000372, 2.312114], [6.920577, 2.433919], [6.821596, 2.538992],
    [6.707809, 2.625695], [6.583224, 2.693979], [6.450835, 2.745059],
    [6.311866, 2.780987], [6.164974, 2.804083], [6.013945, 2.816030],
    [5.862592, 2.819773], [5.711283, 2.818896], [5.559983, 2.816950],
    [5.408663, 2.817393], [5.257293, 2.823542], [5.106101, 2.838519],
    [4.958329, 2.864608], [4.818226, 2.902451], [4.685081, 2.952711],
    [4.558971, 3.015487], [4.440119, 3.090273], [4.328122, 3.176288],
    [4.220138, 3.274361], [4.115731, 3.382806], [4.015882, 3.496663],
    [3.918739, 3.612683], [3.821485, 3.728620], [3.721544, 3.842366],
    [3.616720, 3.952132], [3.505271, 4.056498], [3.385901, 4.154405],
    [3.261523, 4.242537], [3.143757, 4.314526], [3.032120, 4.373919],
    [2.916284, 4.427784], [2.785222, 4.480481], [2.636500, 4.530711],
    [2.483933, 4.572166], [2.331635, 4.603223], [2.179682, 4.623131],
    [2.028089, 4.630554], [1.876917, 4.623567], [1.726241, 4.599572],
    [1.574535, 4.554357], [1.428672, 4.485301], [1.304602, 4.399424],
    [1.203886, 4.302305], [1.124110, 4.196969], [1.062796, 4.085279],
    [1.017518, 3.967759], [0.986043, 3.842951], [0.966632, 3.704743],
    [0.959586, 3.552924], [0.963672, 3.399043], [0.975314, 3.246783],
    [0.991402, 3.095469], [1.009685, 2.944632], [1.028851, 2.793987],
    [1.048576, 2.643459], [1.069497, 2.493189], [1.093105, 2.343497],
    [1.121557, 2.194845], [1.157468, 2.047797], [1.203730, 1.902974],
    [1.263481, 1.761047], [1.340314, 1.622724], [1.433337, 1.495515],
    [1.529371, 1.394176], [1.626073, 1.313680], [1.726470, 1.247100],
    [1.834521, 1.190229], [1.960967, 1.138670], [2.107306, 1.094657],
    [2.258606, 1.062944], [2.409922, 1.042149],
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
