import { useState } from 'react';
import { Multiselect } from 'react-widgets';
import { algorithms } from '../DetailAlgorithm/algorithms';
import ParamRenderer from '../DetailAlgorithm/paramRenderer';
import ResultRenderer from '../DetailAlgorithm/resultRenderer';
import { useAlgoParams } from '../DetailAlgorithm';
import APIS from '../../services/common';
import 'react-widgets/scss/styles.scss';
import '../DetailAlgorithm/styles.scss';

export default function Overview() {
    const [algorithmName, setAlgorithmName] = useState([]);
    const [algoParams, updateParams] = useAlgoParams({});
    const [algoResult, setResult] = useState({});
    const [isRunning, setIsRunning] = useState(false);

    const runAlgorithm = () => {
        setIsRunning(true);
        setResult({});
        APIS.getOverviewInfo({
            algo_names: algorithmName.toString(),
            ...algoParams,
        })
        .then((res) => {
            const data = res.data
            const newResult = {
                'avgTotal': {},
                'avgDelay': {},
                'avgEnergy': {},
                'avgBattery': {},
                'avgBackup': {},
            }
            for (const name of algorithmName) {
                newResult['avgTotal'][name] = data[name]['avg_total']
                newResult['avgDelay'][name] = data[name]['avg_delay']
                newResult['avgEnergy'][name] = data[name]['avg_energy']
                newResult['avgBattery'][name] = data[name]['avg_battery']
                newResult['avgBackup'][name] = data[name]['avg_backup']
            }
            setResult(newResult);
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
                        <Multiselect
                            value={algorithmName}
                            placeholder="Select some algorithms"
                            onChange={(nextAlgorithm) =>
                                setAlgorithmName(nextAlgorithm)
                            }
                            data={algorithms.algorithmNames}
                        />
                    </div>
                </div>
                {algorithmName.length > 0 ? (
                    <div className="component mt-5 mb-2">
                        <div className="h2-title-text align-middle">
                            Set up {algorithmName.toString()} algorithm
                            parameters
                        </div>
                        <div className="mt-3 ml-5 h3-title-text align-middle">
                            Set up environment parameters
                        </div>
                        <div>
                            <ParamRenderer
                                params={algorithms.envParams}
                                paramMapping={algorithms.envMapping}
                                updateParams={updateParams}
                            />
                        </div>
                        <div className="mt-3 ml-5 h3-title-text align-middle">
                            Set up algorithm parameters
                        </div>
                        <div>
                            <ParamRenderer
                                params={algorithms.algoParams}
                                paramMapping={algorithms.algoMapping}
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
                <div
                    key={`${Object.keys(algoResult).length}`}
                    className="detail-algorithm-view"
                >
                    <p className="h1-title-text text-center">
                        Running {algorithmName.toString()} algorithm result
                    </p>
                    <div>
                        <ResultRenderer
                            result={algoResult}
                            multiAlgorithms={true}
                        />
                    </div>
                </div>
            ) : (
                <></>
            )}
        </>
    );
}
