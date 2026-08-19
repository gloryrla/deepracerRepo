"""
[Lane A] Centerline baseline - the insurance model.

Goal: 100% completion rate. Nothing else.
Speed is controlled entirely by the action space, NOT by the reward, so the
policy only has to learn one thing: stay on the track.

Action space (discrete, 10 actions, max 2.0 m/s):
    -25/1.4  -15/1.6  -10/1.8  -5/2.0  0/2.0
      5/2.0   10/1.8   15/1.6  25/1.4  0/1.6

Used by model: A-p1-v1  (45 min)
"""


def reward_function(params):
    if params['is_offtrack'] or not params['all_wheels_on_track']:
        return 1e-3

    tw = params['track_width']
    d = params['distance_from_center']
    speed = params['speed']
    steer = abs(params['steering_angle'])

    reward = 1.0

    # proximity to the centerline
    if d <= 0.10 * tw:
        reward *= 1.3
    elif d <= 0.25 * tw:
        reward *= 1.0
    elif d <= 0.40 * tw:
        reward *= 0.5
    else:
        reward *= 0.15

    # discourage hard steering at speed
    if speed > 1.6 and steer > 20:
        reward *= 0.7

    return float(reward)
