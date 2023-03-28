import axios from 'axios';

const API_ROOT = process.env.REACT_APP_API_ROOT || '';

const APIS = {
    getOverviewInfo: (args) =>
        axios.get(`${API_ROOT}/get_overview`, { params: args }),
    runAlgorithm: (algorithm, args) =>
        axios.get(`${API_ROOT}/run_algorithm/${algorithm}`, { params: args }),
};

export default APIS;
