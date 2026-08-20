"""
[Lane B] Follow the computed K1999 optimal racing line.

Hypothesis: the optimal trajectory is what makes the lap time.

TRACK: A to Z Speedway  (world name `reInvent2019_wide`, 16.64 m x 107 cm)
       Confirmed by measuring the physical mat. Note the measurement came out
       99-101 cm, not 107 -- that is the distance between the INNER edges of
       the white boundary lines (each line is roughly 3 cm). Either way it
       rules out re:Invent 2018 at 76 cm.

The 110 coordinates below were computed for THIS track: curvature
equalisation (the K1999 method) over the 110 centreline waypoints from
aws-deepracer-community/deepracer-log-guru, 1500 sweeps.

WIDTH AND MARGIN.  The line is consumed inside the reward function during
SIMULATION, where params['track_width'] is 1.067 m, so it is computed against
the simulator's half-width of 0.5335 m. The clearance margin is 0.18 m rather
than 0.15: 0.15 m for the car itself plus 0.03 m to absorb the physical mat
measuring about 6 cm narrower than spec. Result: the line stays 0.18 m from the
white line in the simulator and still 0.147 m clear even if the real mat is
only 100 cm wide.

    metric                centreline   this line
    length                  16.635 m    15.409 m   (-7.4 percent)
    min corner radius         0.61 m      0.79 m   (+30 percent)
    lateral room used              -     all of the 0.353 m corridor

An earlier version of this file ran only 100 sweeps and used just a third of
the available width -- barely different from the centreline, so it did not
actually test this lane's hypothesis. More sweeps turned out to be strictly
better here: the minimum radius dips around 400 sweeps and then recovers
past 800.

>>> DO NOT reuse these coordinates on re:Invent 2018. <<<
They are absolute track coordinates. On a different track the reward would be
paid for hugging a line that is off the asphalt.

TUNING: the -6.0 coefficient is how strictly the car must hug the line.
    - car clings to the line and falls off  -> soften to -4.0
    - car wanders off the line              -> tighten to -8.0
"""
import math

# K1999 racing line for A to Z Speedway (reInvent2019_wide), 1500 sweeps
RACE_LINE = [
    [2.561213, 1.094393], [2.712540, 1.059865], [2.863863, 1.029669],
    [3.015185, 1.002878], [3.166505, 0.978655], [3.317826, 0.956253],
    [3.469147, 0.935030], [3.620466, 0.914455], [3.771785, 0.894127],
    [3.923105, 0.873793], [4.074424, 0.853358], [4.225743, 0.832908],
    [4.377063, 0.812713], [4.528382, 0.793233], [4.679700, 0.775126],
    [4.831018, 0.759234], [4.982334, 0.746574], [5.133648, 0.738323],
    [5.284961, 0.735806], [5.436270, 0.740487], [5.587574, 0.753989],
    [5.738873, 0.778152], [5.890172, 0.815154], [6.041456, 0.867757],
    [6.195616, 0.941398], [6.347702, 1.040114], [6.476079, 1.152041],
    [6.576242, 1.267659], [6.651921, 1.383247], [6.706746, 1.496405],
    [6.743955, 1.605763], [6.766250, 1.710725], [6.775739, 1.811200],
    [6.773938, 1.907392], [6.761807, 1.999602], [6.739818, 2.088083],
    [6.708022, 2.172906], [6.666807, 2.254320], [6.616337, 2.332922],
    [6.556079, 2.409509], [6.484699, 2.484981], [6.399878, 2.560278],
    [6.296831, 2.637115], [6.164317, 2.719149], [6.014128, 2.795707],
    [5.862243, 2.860306], [5.710448, 2.915686], [5.558708, 2.964888],
    [5.406997, 3.010578], [5.255294, 3.055250], [5.107117, 3.100255],
    [4.980735, 3.141589], [4.878440, 3.178371], [4.782764, 3.216641],
    [4.689918, 3.258582], [4.598114, 3.305278], [4.504597, 3.357703],
    [4.395634, 3.424232], [4.269104, 3.507677], [4.140192, 3.598010],
    [4.013725, 3.690098], [3.888193, 3.782992], [3.762342, 3.875619],
    [3.634891, 3.966943], [3.504547, 4.055908], [3.369967, 4.141415],
    [3.235774, 4.218948], [3.117150, 4.280238], [3.011050, 4.328806],
    [2.904037, 4.371481], [2.782630, 4.411970], [2.638782, 4.448856],
    [2.486760, 4.474623], [2.335052, 4.486586], [2.183736, 4.484448],
    [2.032851, 4.467675], [1.882420, 4.435388], [1.732486, 4.386203],
    [1.589500, 4.321303], [1.477165, 4.255870], [1.396184, 4.199360],
    [1.325816, 4.142790], [1.260653, 4.083181], [1.196889, 4.016939],
    [1.131324, 3.938965], [1.060810, 3.840927], [0.982056, 3.707011],
    [0.907937, 3.541838], [0.855071, 3.375654], [0.822054, 3.213876],
    [0.805973, 3.055607], [0.805054, 2.900646], [0.818150, 2.748700],
    [0.844592, 2.599615], [0.884073, 2.453334], [0.936601, 2.309858],
    [1.002489, 2.169253], [1.082378, 2.031657], [1.177305, 1.897294],
    [1.288829, 1.766497], [1.418393, 1.640541], [1.547176, 1.536093],
    [1.644326, 1.468247], [1.723844, 1.418635], [1.797581, 1.376782],
    [1.872692, 1.337746], [1.970862, 1.291463], [2.107351, 1.234736],
    [2.258609, 1.180639], [2.409897, 1.134284],]


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
