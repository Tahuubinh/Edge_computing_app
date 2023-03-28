from keras.optimizers import Adam
from keras.layers import Dense
from keras.models import Sequential
from collections import deque
import gym
from . import gym_offload_autoscale
import random
import numpy as np

'''
    Here we implemented a DQN algorithm to compare with PPO.
    * We use a single hidden layer neural network.
    * The implementation is a stub, tbh.
'''


class DQNSolver:
    def __init__(self, observation_space, action_space):
        self.exploration_rate = 1.0

        self.observation_space = observation_space
        self.action_space = action_space
        self.memory = deque(maxlen=1000000)
        # the neural network
        self.model = Sequential()
        self.model.add(Dense(24, input_shape=(observation_space,), activation="relu"))
        self.model.add(Dense(24, activation="relu"))
        self.model.add(Dense(self.action_space, activation="linear"))
        self.model.compile(loss="mse", optimizer=Adam(learning_rate=0.001))

    def remember(self, state, action, reward, next_state, terminal):
        self.memory.append((state, action, reward, next_state, terminal))

    def act(self, state):
        if np.random.rand() < self.exploration_rate:
            return random.randrange(self.action_space)
        q_values = self.model.predict(state)
        return np.argmin(q_values[0])

    def replay(self):
        if len(self.memory) < 20:
            return
        batch = random.sample(self.memory, 20)
        for state, action, reward, next_state, terminal in batch:
            q_upd = reward
            if not terminal:
                q_upd = (reward + 0.95 *
                         np.amin(self.model.predict(next_state)[0]))
            q_val = self.model.predict(state)
            q_val[0][action] = q_upd
            self.model.fit(state, q_val, verbose=0)
        self.exploration_rate *= 0.995  # exploration rate
        self.exploration_rate = max(0.01, self.exploration_rate)


class DQNAlgorithm:
    def __init__(self, time_slots: str, p_coeff: str,
                 timeslot_duration: str, max_number_of_server: str,
                 server_service_rate: str, d_sta: str, coef_dyn: str,
                 server_power_consumption: str, batery_capacity: str,
                 lamda_high: str, lamda_low: str, h_high: str, h_low: str,
                 back_up_cost_coef: str, normalized_unit_depreciation_cost: str,
                 time_steps_per_episode: str, train_time_slots: str, verbose: str,
                 random_seed: str) -> None:
        self.time_slots = int(time_slots)
        self.timeslot_duration = float(int(timeslot_duration)/60)
        self.time_steps_per_episode = int(time_steps_per_episode)
        self.max_number_of_server = int(max_number_of_server)
        self.server_service_rate = int(server_service_rate)
        self.d_sta = int(d_sta)
        self.coef_dyn = float(coef_dyn)
        self.server_power_consumption = int(server_power_consumption)
        self.batery_capacity = int(batery_capacity)
        self.lamda_high = int(lamda_high)
        self.lamda_low = int(lamda_low)
        self.h_high = float(h_high)
        self.h_low = float(h_low)
        self.back_up_cost_coef = float(back_up_cost_coef)
        self.normalized_unit_depreciation_cost = float(normalized_unit_depreciation_cost)
        self.train_time_slots = int(train_time_slots)
        self.p_coeff = float(p_coeff)
        self.verbose = float(verbose)
        self.random_seed = int(random_seed)
        self.rewards_list = []
        self.avg_rewards = []
        self.rewards_time_list = []
        self.avg_rewards_time_list = []
        self.rewards_bak_list = []
        self.avg_rewards_bak_list = []
        self.rewards_bat_list = []
        self.avg_rewards_bat_list = []
        self.avg_rewards_energy_list = []
        self.init_env()

    def init_env(self) -> None:
        self.env = gym.make('offload-autoscale-v0', p_coeff=self.p_coeff,
                            timeslot_duration=self.timeslot_duration, max_number_of_server=self.max_number_of_server,
                            server_service_rate=self.server_service_rate, d_sta=self.d_sta, coef_dyn=self.coef_dyn,
                            server_power_consumption=self.server_power_consumption, batery_capacity=self.batery_capacity,
                            lamda_high=self.lamda_high, lamda_low=self.lamda_low, h_high=self.h_high, h_low=self.h_low,
                            back_up_cost_coef=self.back_up_cost_coef,
                            normalized_unit_depreciation_cost=self.normalized_unit_depreciation_cost,
                            time_steps_per_episode=self.time_steps_per_episode)

        self.observation_space = self.env.observation_space.shape[0]
        action_space = self.env.action_space.shape[0]
        self.solver = DQNSolver(self.observation_space, action_space)

    def train_model(self):
        state = None
        accumulated_step = 0
        while True:
            state = self.env.reset()
            state = np.reshape(state, [1, self.observation_space])
            step = 0
            while True:
                done = False
                action = self.solver.act(state)
                next_state, reward, _, _ = self.env.step(action)
                next_state = np.reshape(next_state, [1, self.observation_space])
                step += 1
                accumulated_step += 1
                if step == self.time_steps_per_episode:
                    done = True
                self.solver.remember(state, action, reward, next_state, done)
                state = next_state
                if done:
                    break
                self.solver.replay()
                if accumulated_step == self.train_time_slots:  # Termination of the entire training process.
                    break
            if accumulated_step == self.train_time_slots:
                break

        return state

    def run(self) -> dict:
        state = self.train_model()
        for i in range(self.time_slots):
            action = self.solver.act(state)
            next_state, reward, _, _ = self.env.step(action)
            next_state = np.reshape(next_state, [1, self.observation_space])
            self.rewards_list.append(1 / reward)
            self.avg_rewards.append(np.mean(self.rewards_list[:]))
            t, bak, bat = self.env.render()
            self.rewards_time_list.append(t)
            self.avg_rewards_time_list.append(
                np.mean(self.rewards_time_list[:]))
            self.rewards_bak_list.append(bak)
            self.avg_rewards_bak_list.append(np.mean(self.rewards_bak_list[:]))
            self.rewards_bat_list.append(bat)
            self.avg_rewards_bat_list.append(np.mean(self.rewards_bat_list[:]))
            self.avg_rewards_energy_list.append(
                self.avg_rewards_bak_list[-1] + self.avg_rewards_bat_list[-1])

        return {
            'avg_total': [float(item) for item in self.avg_rewards],
            'avg_delay': [float(item) for item in self.avg_rewards_time_list],
            'avg_backup': [float(item) for item in self.avg_rewards_bak_list],
            'avg_battery': [float(item) for item in self.avg_rewards_bat_list],
            'avg_energy': [float(item) for item in self.avg_rewards_energy_list],
        }
