import { useState } from 'react';
import DropdownList from 'react-widgets/DropdownList';
import { algorithms } from './algorithms';
import ParamRenderer from './paramRenderer';
import ResultRenderer from './resultRenderer';
import APIS from '../../services/common';
import 'react-widgets/scss/styles.scss';
import './styles.scss';

function useAlgoParams(initParams) {
    const [params, setParams] = useState(initParams);

    function updateParams(key, value) {
        const newParams = params;
        newParams[key] = value;
        setParams(newParams);
    }

    return [params, updateParams];
}


function DetailAlgorithm() {
    const [algorithmName, setAlgorithmName] = useState('');
    const [algoParams, updateParams] = useAlgoParams({});
    const [algoResult, setResult] = useState({});
    const [isRunning, setIsRunning] = useState(false);

    const runAlgorithm = () => {
        setIsRunning(true);
        setResult({});
        APIS.runAlgorithm(algorithmName, algoParams).then((res) => {
            setResult({
                'avgTotal': res.data['avg_total'],
                'avgDelay': res.data['avg_delay'],
                'avgEnergy': res.data['avg_energy'],
                'avgBattery': res.data['avg_battery'],
                'avgBackup': res.data['avg_backup'],
            })
            setIsRunning(false);
        })
        .catch((e) => {
            setIsRunning(false);
        });
    };

    return (
        <>
            <div className="detail-algorithm-view">
                <p className="h1-title-text text-center">
                    Set up algorithm parameters
                </p>
                <div className="component d-flex flex-row">
                    <div className="align-self-center mr-5">
                        <div className="h2-title-text align-middle">
                            Choose an algorithm
                        </div>
                    </div>
                    <div className="algo-dropdown">
                        <DropdownList
                            value={algorithmName}
                            placeholder="Select an algorithm"
                            onChange={(nextAlgorithm) =>
                                setAlgorithmName(nextAlgorithm)
                            }
                            data={algorithms.algorithmNames}
                        />
                    </div>
                </div>
                {algorithmName ? (
                    <div className="component mt-5 mb-2">
                        <div className="h2-title-text align-middle">
                            Set up {algorithmName} algorithm parameters
                        </div>
                        <div className="mt-3 ml-5 h3-title-text align-middle">
                            Set up environment parameters
                        </div>
                        <div>
                            <ParamRenderer
                                params={algorithms.envParams}
                                paramMapping={
                                    algorithms.envMapping
                                }
                                updateParams={updateParams}
                            />
                        </div>
                        <div className="mt-3 ml-5 h3-title-text align-middle">
                            Set up algorithm parameters
                        </div>
                        <div>
                            <ParamRenderer
                                params={algorithms.algoParams}
                                paramMapping={
                                    algorithms.algoMapping
                                }
                                updateParams={updateParams}
                            />
                        </div>
                        <div className="d-flex justify-content-center mt-5">
                            <button
                                type="button"
                                className="btn btn-primary"
                                disabled={isRunning}
                                onClick={(e) => runAlgorithm()}
                            >
                                Run algorithm
                            </button>
                        </div>
                    </div>
                ) : (
                    <></>
                )}
            </div>
            {Object.keys(algoResult).length > 0 ? (
                <div className="detail-algorithm-view">
                    <p className="h1-title-text text-center">
                        Running {algorithmName} algorithm result
                    </p>
                    <div>
                        <ResultRenderer result={algoResult} />
                    </div>
                </div>
            ) : (
                <></>
            )}
        </>
    );
}

export { useAlgoParams, DetailAlgorithm }