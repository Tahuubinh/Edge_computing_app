import gym
import math
import numpy as np
from typing import List
from gym import spaces
from gym.utils import seeding
from scipy.optimize import minimize_scalar


class OffloadAutoscaleEnv(gym.Env):
    # define state space, action space, and other environment parameters
    def __init__(
            self, p_coeff: float, timeslot_duration: float, max_number_of_server: int,
            server_service_rate: int, d_sta: int, coef_dyn: int,
            server_power_consumption: int, batery_capacity: int,
            lamda_high: int, lamda_low: int, h_high: float, h_low: float,
            back_up_cost_coef: float, normalized_unit_depreciation_cost: float,
            time_steps_per_episode: int) -> None:
        # environment parameters from III.SYSTEM MODEL
        # duration of each time-slot
        self.timeslot_duration = timeslot_duration  # hours, ~15min
        # A.Workload model
        # maximum number of activated edge server M
        self.max_number_of_server = max_number_of_server
        # B.Delay cost model
        # server service rate κ
        self.server_service_rate = server_service_rate  # units/sec
        # C.Power model
        # note: d = d_op + d_com, where
        #       (1) d_op = d_sta + d_dyn :the power demand by the base station
        #       (1a) d_sta: static power consumption by the base station
        #       (1b) d_dyn: dynamic power consumption by the base station
        #       (2) d_com = d_com = μ * α + server_power_consumption * m (formula & coefficient α not specified in the paper, our own proposal)
        #                                                                (α = server_power_consumption/lamda_low)
        self.d = 0
        # (1)d_op
        self.d_op = 0
        # (1a)d_sta
        self.d_sta = d_sta
        # (1b)d_dyn = coef_dyn * λ (this is not specified in the power model, but our own proposal)
        self.coef_dyn = coef_dyn
        # (2)d_com
        self.d_com = 0
        self.m = 0
        self.mu = 0
        # harvested green energy
        self.g = 0
        # server power consumption (this is from VII.A.Simulation Setup, not mentioned in III.SYSTEM MODEL)
        self.server_power_consumption = server_power_consumption
        # D.Battery model
        # batery capacity B
        self.batery_capacity = batery_capacity  # Wh

        # set the value range for state space parameters (λ, b, h, e)
        # λ
        self.lamda_high = lamda_high  # units/second
        self.lamda_low = lamda_low
        # b
        self.b_high = self.batery_capacity / self.timeslot_duration  # W (b_high = battery capacity B in the paper,but here it can be changed from energy to power (Wh-->W) as stated in III.C.Power Model)
        self.b_low = 0
        # h
        self.h_high = h_high  # s/unit
        self.h_low = h_low
        # e
        self.e_low = 0
        self.e_high = 2
        self.time = 0  # between 0 & 23.75, the time in the day (in unit: hour), used to build transition funtion for e

        # define state space & action space:
        r_high = np.array([
            self.lamda_high,
            self.b_high,
            self.h_high,
            self.e_high])
        r_low = np.array([
            self.lamda_low,
            self.b_low,
            self.h_low,
            self.e_low])
        self.observation_space = spaces.Box(low=r_low, high=r_high)
        self.action_space = spaces.Box(low=0.0, high=1.0, shape=(1,), dtype=np.float32)
        # note, the action space is normalized to the [0,1] range, will need to be mapped back to the correct action space later via the de_state variable in the cal() function

        # initalize state
        self.state = [0, 0, 0, 0]

        # cost coefficient of backup power supply ϕ
        self.back_up_cost_coef = back_up_cost_coef
        # normalized unit depreciation cost ω
        self.normalized_unit_depreciation_cost = normalized_unit_depreciation_cost

        # coefficent to show the priority of enery cost vs. time delay cost in the reward function
        self.priority_coefficent = p_coeff

        # environment parameters to track the timesteps in training the agent
        self.time_steps_per_episode = time_steps_per_episode
        self.episode = 0
        self.time_step = 0

        # elements of the cost function
        self.reward_time = 0
        self.reward_bak = 0
        self.reward_bat = 0

    # not used, can be ignored
    def seed(self, seed: int = None) -> List[int]:
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    # Transition functions
    # transition function of λ
    def get_lambda(self):
        return np.random.uniform(self.lamda_low, self.lamda_high)

    # transition function of b
    def get_b(self) -> float:
        b = self.state[1]
        # print('\t', end = '')
        if self.d_op > b:
            # print('unused batery')
            return b + self.g
        else:
            if self.g >= self.d:
                # print('recharge batery')
                return np.minimum(self.b_high, b + self.g - self.d)
            else:
                # print('discharge batery')
                return b + self.g - self.d

    # transition function of h
    def get_h(self):
        return np.random.uniform(self.h_low, self.h_high)

    # transition function of e
    def get_e(self) -> int:
        if self.time >= 9 and self.time < 15:
            return 2
        if self.time < 6 or self.time >= 18:
            return 0
        return 1

    # transition function of time
    def get_time(self) -> None:
        self.time += self.timeslot_duration
        if self.time >= 24:
            self.time -= 24

    # calculate g from e
    def get_g(self):
        e = self.state[3]
        if e == 0:
            return np.random.exponential(60) + 100
        if e == 1:
            return np.random.normal(520, 130)
        return np.random.normal(800, 95)

    # elements of computing power demend d
    # d_op
    def get_dop(self) -> int:
        return self.d_sta + self.coef_dyn * self.state[0]

    # d_com
    def get_dcom(self, m: int, mu: int) -> float:
        normalized_min_cov = self.lamda_low
        return self.server_power_consumption * m + self.server_power_consumption / normalized_min_cov * mu

    # calculate m(t), μ(t) from a(t) (calculate the number of active servers & the local workload from the  normalized action in the range [0,1])
    def cal(self, action) -> List[int]:
        lamda, b, h, _ = self.state
        d_op = self.get_dop()
        if b <= d_op + self.server_power_consumption:  # if remaining baterry <= d_op + power consumption of 1 server, the only valid action is [0, 0]
            return [0, 0]
        else:  # if remaining baterry > d_op, d_op + power consumption of 1 server
            low_bound = self.server_power_consumption  # the lower bound for action space
            high_bound = np.minimum(b - d_op, self.get_dcom(self.max_number_of_server, lamda))  # the upper bound for action space
            de_action = low_bound + action * (high_bound - low_bound)  # map the action from the range [0, 1] range to the actual range
            # print('deaction ', de_action)
            return self.get_m_mu(de_action)

    # calculate m(t), μ(t) from de_a(t) (calculate the number of active servers & the local workload from the actual action - the computing power demand)
    # note: following (8) from paper: m, μ = argmin(c_delay) such that d_com(m, μ) = de_a, where
    #                               d_com = μ * α + server_power_consumption * m (formula & coefficient α not specified in the paper, our own proposal)
    #                                                                            (α = server_power_consumption/lamda_low)
    #                               c_delay = μ / (m * κ - μ) + (λ(t) - μ(t))h(t) + 0
    def get_m_mu(self, de_action) -> List[int]:
        lamd, _, h, _ = self.state
        opt_val = math.inf
        ans = [-1, -1]
        # loop through all possible (m, μ) based on m
        for m in range(1, self.max_number_of_server + 1):
            normalized_min_cov = self.lamda_low
            mu = (de_action - self.server_power_consumption * m) * normalized_min_cov / self.server_power_consumption
            valid = self.check_constraints(m, mu)
            if valid:  # if the pair (m, μ) is valid, compare the current c_delay to the best c_delay, and update the answer
                if self.cost_function(m, mu, h, lamd) < opt_val:
                    ans = [m, mu]
                    opt_val = self.cost_function(m, mu, h, lamd)
        return ans

    def cost_function(self, m: int, mu: int, h, lamda) -> float:  # calculate the delay cost based on m, μ, h, λ
        return self.cost_delay_local_function(m, mu) + self.cost_delay_cloud_function(mu, h, lamda)

    def cost_delay_local_function(self, m, mu) -> float:
        if m == 0 and mu == 0:
            return 0
        return mu / (m * self.server_service_rate - mu)

    def cost_delay_cloud_function(self, mu, h, lamda) -> float:
        return (lamda - mu) * h

    def check_constraints(self, m: int, mu: int) -> bool:  # check (m, μ) pair
        if mu > self.state[0] or mu < 0:
            return False  # if local workload is more than total workload or local workload is negative: invalid (m, μ) pair
        if isinstance(self.mu, complex):
            return False  # not needed
        if m * self.server_service_rate <= mu:
            return False  # if local workload is more than the service capability that the activated edge servers are able to provide: invalid (m, μ) pair
        return True

    # reward function
    # note: cost = cost_delay + c_bak + c_bat, where
    #       (1) cost_delay = d_sta + d_dyn :the total delay cost
    #       (2) c_bak: the backup power supply cost
    #       (3) c_bat: the battery depreciation cost
    def reward_func(self, action) -> float:
        lamda, b, h, _ = self.state
        cost_delay_wireless = 0
        # calculate m(t) & μ(t) from a(t)
        self.m, self.mu = self.cal(action)
        # (1) cost_delay
        cost_delay = self.cost_function(self.m, self.mu, h, lamda) + cost_delay_wireless
        # (2)(3) c_bat & c_bak
        if self.d_op > b:  # use backup power
            cost_batery = 0
            cost_bak = self.back_up_cost_coef * self.d_op
        else:  # use battery
            cost_batery = self.normalized_unit_depreciation_cost * np.maximum(self.d - self.g, 0)
            cost_bak = 0
        # scale the elements of cost based on priority coefficient
        cost_bak = cost_bak * self.priority_coefficent
        cost_batery = cost_batery * self.priority_coefficent
        cost_delay = cost_delay * (1 - self.priority_coefficent)
        # total cost
        self.reward_bak = cost_bak
        self.reward_bat = cost_batery
        self.reward_time = cost_delay
        cost = cost_delay + cost_batery + cost_bak
        return cost

    # implement a state transition, returns [next state, reward, done, info(not used)]
    # note: reward here is 1/cost from the paper
    def step(self, action):
        done = False
        action = float(action)

        self.get_time()  # transition to new time
        self.time_step += 1
        self.g = self.get_g()  # get the harvested green energy

        self.d_op = self.get_dop()  # not needed, only used to print intermediate results
        self.m, self.mu = self.cal(action)  # not needed, only used to print intermediate results
        self.d_com = self.get_dcom(self.m, self.mu)  # not needed, only used to print intermediate results
        self.d = self.d_op + self.d_com  # not needed, only used to print intermediate results
        # calculate reward
        reward = self.reward_func(action)
        # transition to new state
        lambda_t = self.get_lambda()
        b_t = self.get_b()
        h_t = self.get_h()
        e_t = self.get_e()
        self.state = np.array([lambda_t, b_t, h_t, e_t])

        if self.time_step >= self.time_steps_per_episode:
            done = True
            self.episode += 1
        return self.state, 1 / reward, done, {}

    # reset enviroment to starting state
    def reset(self):
        self.state = np.array([self.lamda_low, self.b_high, self.h_low, self.e_low])
        self.time = 0
        self.time_step = 0
        return self.state

    # display intermediate results
    def render(self):
        return self.reward_time, self.reward_bak, self.reward_bat

    # Fixed power agent: (not part of the environment)
    # find the corresponding image of the fixed power action in the mapping to the [0, 1] range
    def fixed_action_cal(self, fixed_action) -> float:
        lamda, b, h, _ = self.state
        d_op = self.get_dop()
        low_bound = self.server_power_consumption
        high_bound = np.minimum(b - d_op, self.get_dcom(self.max_number_of_server, lamda))
        if high_bound < low_bound:
            return 0
        if fixed_action < low_bound:
            return 0
        if fixed_action > high_bound:
            return 1
        else:
            return (fixed_action-low_bound)/(high_bound-low_bound)

    # Myopic optimization agent: (not part of the environment)
    # find the corresponding image of the myopic optimization action in the mapping to the [0, 1] range
    def myopic_action_cal(self) -> float:
        lamda, b, h, _ = self.state
        d_op = self.get_dop()
        if b <= d_op + self.server_power_consumption:
            return 0
        else:
            ans = math.inf
            for m in range(1, self.max_number_of_server):
                def f(mu, m, h, lamda):
                    return (1 - self.priority_coefficent) * (mu/(m*self.server_service_rate-mu)+h*(lamda - mu)) + self.priority_coefficent * (self.normalized_unit_depreciation_cost*(self.server_power_consumption*m+self.server_power_consumption/self.lamda_low*mu))
                res = minimize_scalar(f, bounds=(0, np.minimum(lamda, m*self.server_service_rate)), args=(m, h, lamda), method='bounded')
                if res.fun < ans:
                    ans = res.fun
                    params = [m, res.x]
            d_com = self.server_power_consumption*params[0]+self.server_power_consumption/self.lamda_low*params[1]
            return self.fixed_action_cal(d_com)
