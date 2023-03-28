import { useState, useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { solid } from '@fortawesome/fontawesome-svg-core/import.macro'; // <-- import styles to be used
import { algorithms } from './algorithms';

function InputRenderer({ paramLabel, paramMapping, updateParams }) {
    // const [param, setParam] = useState('');
    const defaultValues = {
    'Priority coefficient': 0.5,
    'Number of servers': 15,
    'Length each time slot': 15,
    'Battery capacity': 2000,
    'Server service rate': 20,
    'Workload (λ)': [20, 100],
    'Network congestion (k)': {lowParam: 0.02, highparam: 0.06},
    'Back up power coefficient (φ)': 0.15,
    'Battery depreciation coefficient (ω)': 0.01,
    'Base station static power': 300,
    'Dynamic power coefficient': 0.5,
    'Server power consumption': 150,
    'Time steps per episode': 96,
    'Training time slots': 2000,
    'Time slots': 100,
    Verbose: 0,
    'Random seed': 1234,
    };
    const [param, setParam] = useState(defaultValues[paramLabel]);

    useEffect(() => {
        setParam(param);
        updateParams(paramMapping, param);
      }, []);

    return (
        <div className="mt-3 ml-5 d-flex flex-row">
            <div className="param-text align-self-center mr-4">
                <div className="align-middle">{paramLabel}</div>
            </div>
            <div className="algo-input">
                <input
                    className="w-100 h-100 p-1"
                    value={param}
                    placeholder="Enter a value"
                    onChange={(event) => {
                        setParam(event.target.value);
                        updateParams(paramMapping, event.target.value);
                    }}
                />
            </div>
            <FontAwesomeIcon
                className="align-self-center ml-2"
                title={algorithms.paramDescription[paramLabel]}
                icon={solid('circle-info')}
            />
        </div>
    );
}

function RangeInputRenderer({ paramLabel, paramMapping, updateParams }) {
    const [lowParam, setLowParam] = useState('');
    const [highparam, setHighParam] = useState('');

    return (
        <div className="mt-3 ml-5 d-flex flex-row">
            <div className="param-text align-self-center mr-4">
                <div className="align-middle">{paramLabel}</div>
            </div>
            <div className="algo-range-input">
                <input
                    className="w-80 h-100 p-1"
                    value={lowParam}
                    placeholder="Enter a low value"
                    onChange={(event) => {
                        setLowParam(event.target.value);
                        updateParams(paramMapping.low, event.target.value);
                    }}
                />
                <FontAwesomeIcon
                    className="align-self-center ml-2"
                    title={algorithms.paramDescription[paramLabel].low}
                    icon={solid('circle-info')}
                />
            </div>
            <div className="algo-range-input">
                <input
                    className="w-80 h-100 p-1"
                    value={highparam}
                    placeholder="Enter a high value"
                    onChange={(event) => {
                        setHighParam(event.target.value);
                        updateParams(paramMapping.high, event.target.value);
                    }}
                />
                <FontAwesomeIcon
                    className="align-self-center ml-2"
                    title={algorithms.paramDescription[paramLabel].high}
                    icon={solid('circle-info')}
                />
            </div>
        </div>
    );
}

const paramRendererMp = {
    'Priority coefficient': InputRenderer,
    'Number of servers': InputRenderer,
    'Length each time slot': InputRenderer,
    'Battery capacity': InputRenderer,
    'Server service rate': InputRenderer,
    'Workload (λ)': RangeInputRenderer,
    'Network congestion (k)': RangeInputRenderer,
    'Back up power coefficient (φ)': InputRenderer,
    'Battery depreciation coefficient (ω)': InputRenderer,
    'Base station static power': InputRenderer,
    'Dynamic power coefficient': InputRenderer,
    'Server power consumption': InputRenderer,
    'Time steps per episode': InputRenderer,
    'Training time slots': InputRenderer,
    'Time slots': InputRenderer,
    Verbose: InputRenderer,
    'Random seed': InputRenderer,
};

export default function ParamRenderer({ params, paramMapping, updateParams }) {
    return (
        <div>
            {params.map((param) => {
                const ParamRenderer = paramRendererMp[param];
                return (
                    <ParamRenderer
                        key={param}
                        paramLabel={param}
                        paramMapping={paramMapping[param]}
                        updateParams={updateParams}
                    />
                );
            })}
        </div>
    );
}
