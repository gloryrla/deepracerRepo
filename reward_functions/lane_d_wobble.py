"""
[Lane D] Real-car robustness - suppress steering oscillation (wobble).

Hypothesis: the fastest model in simulation is not the fastest on the physical
car. Real servos have latency and inertia, so a policy that flicks the steering
back and forth loses tyre grip and spins, even though it looks fine in the sim.

Two defences:
  1. the action space caps steering at +/-20 degrees (instead of 30)
  2. the reward penalises the RATE OF CHANGE of the steering angle

If Lane B and Lane C fall apart on the physical track on Day 2 afternoon, this
is the only remaining candidate - so do not delete it just because its
simulated lap time is slower.

CAVEAT on the global: the reward function has no memory of the previous step,
so the previous steering angle is kept in a module-level dict. This is a common
community technique and works because the module stays loaded, but with several
rollout workers the values can interleave. If training converges strangely,
delete the `rate` block and keep only the absolute-steering penalty - weaker,
but safe.

Action space (discrete, 8 actions, max 2.0 m/s, steering limited to +/-20):
    -20/1.2  -12/1.5  -6/1.8  0/2.0
      6/1.8   12/1.5  20/1.2  0/1.4

Used by model: D-p2-v1  (60 min)
"""
import math

# remembers the previous step's steering angle (for the steering-rate penalty)
PREV = {'steer': 0.0}


def reward_function(params):
    steer = params['steering_angle']

    # reset at the start of each episode
    if params['steps'] <= 1:
        PREV['steer'] = steer

    if params['is_offtrack'] or not params['all_wheels_on_track']:
        PREV['steer'] = steer
        return 1e-3

    tw = params['track_width']
    d = params['distance_from_center']
    speed = params['speed']

    # smooth centerline reward
    reward = math.exp(-4.0 * (d / tw) ** 2)

    # steering rate penalty - the core of this lane
    rate = abs(steer - PREV['steer'])
    if rate > 15:
        reward *= 0.5
    elif rate > 8:
        reward *= 0.8

    # high-speed oversteer penalty
    if speed > 1.7 and abs(steer) > 15:
        reward *= 0.7

    PREV['steer'] = steer
    return float(max(reward, 1e-3))
