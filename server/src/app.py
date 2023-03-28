from flask import Flask, request
from flask_cors import CORS, cross_origin
from algorithms.ppo2 import PPO2Algorithm
from algorithms.dqn import DQNAlgorithm
from algorithms.a2c import A2CAlgorithm
from algorithms.sac import SACAlgorithm
from algorithms.trpo import TRPOAlgorithm
import json

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

ALGORITHM_MP = {
    'PPO': PPO2Algorithm,
    'DQN': DQNAlgorithm,
    'A2C': A2CAlgorithm,
    'SAC': SACAlgorithm,
    'TRPO': TRPOAlgorithm,
}


@app.route("/get_overview", methods=['GET'])
@cross_origin()
def get_overview_info():
    args = request.args.to_dict()
    algo_names = args['algo_names'].split(',')
    args.pop('algo_names')
    result = {}
    for name in algo_names:
        algorithm = ALGORITHM_MP[name](**args)
        result[name] = algorithm.run()
    return json.dumps(result), 200, {'Content-Type': 'application/json; charset=utf-8'}


@app.route("/run_algorithm/<algorithm_name>", methods=['GET'])
@cross_origin()
def run_algorithm(algorithm_name):
    args = request.args.to_dict()
    algorithm = ALGORITHM_MP[algorithm_name](**args)
    result = algorithm.run()
    return json.dumps(result), 200, {'Content-Type': 'application/json; charset=utf-8'}
