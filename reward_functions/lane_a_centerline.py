"""
[Lane A] Centerline baseline - the simple, reliable candidate.

Goal: a clean lap, every lap. Simplest possible reward, so it is the fastest
lane to converge and the least likely to surprise on the physical car.

NOTE (2026-08-19): scoring changed to the AVERAGE of two models' times, so this
is no longer an "insurance" model that can afford to be slow -- a slow time now
drags the average down instead of being discarded. Its cap was raised 2.0 -> 2.2
to keep it a genuine contender.
Speed is controlled entirely by the action space, NOT by the reward, so the
policy only has to learn one thing: stay on the track.

TRACK: A to Z Speedway (`reInvent2019_wide`, 16.64 m x 107 cm). The markers
below are fractions of params['track_width'], so they rescale to the wider
track automatically -- no coordinates to update.

Action space (discrete, 10 actions, max 2.2 m/s):
    -25/1.5  -15/1.8  -10/2.0  -5/2.2  0/2.2
      5/2.2   10/2.0   15/1.8  25/1.5  0/1.8
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
    if speed > 1.8 and steer > 20:
        reward *= 0.7

    return float(reward)
