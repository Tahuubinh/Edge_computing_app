from gym.envs.registration import register

register(
    id='offload-autoscale-v0',
    entry_point='algorithms.gym_offload_autoscale.envs:OffloadAutoscaleEnv',
)