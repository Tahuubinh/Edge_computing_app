import Plot from 'react-plotly.js';
import _ from 'lodash';

function AreaGraphRenderer({ delayData, bakData, batteryData }) {
    const layout = {
        width: 800,
        height: 600,
        title: 'Average Costs Graph',
        xaxis: {
            title: {
                text: 'Time slot',
                font: {
                    family: 'Courier New, monospace',
                    size: 18,
                    color: '#7f7f7f',
                },
            },
        },
        yaxis: {
            title: {
                text: 'Average Costs',
                font: {
                    family: 'Courier New, monospace',
                    size: 18,
                    color: '#7f7f7f',
                },
            },
        },
    };

    return (
        <div className="component">
            <Plot
                layout={layout}
                data={[
                    {
                        x: Array.from(Array(delayData.length).keys()),
                        y: delayData,
                        name: 'Delay Cost',
                        stackgroup: 'one',
                    },
                    {
                        x: Array.from(Array(bakData.length).keys()),
                        y: bakData,
                        name: 'Backup Cost',
                        stackgroup: 'one',
                    },
                    {
                        x: Array.from(Array(batteryData.length).keys()),
                        y: batteryData,
                        name: 'Battery Cost',
                        stackgroup: 'one',
                    },
                ]}
            />
        </div>
    );
}

function AvgLineGraphRenderer({ data, title, yaxisLabel }) {
    const layout = {
        width: 800,
        height: 600,
        title: `${title}`,
        xaxis: {
            title: {
                text: 'Time slot',
                font: {
                    family: 'Courier New, monospace',
                    size: 18,
                    color: '#7f7f7f',
                },
            },
        },
        yaxis: {
            title: {
                text: `${yaxisLabel}`,
                font: {
                    family: 'Courier New, monospace',
                    size: 18,
                    color: '#7f7f7f',
                },
            },
        },
    };

    const filterdData = () => {
        const result = []
        for (const key of Object.keys(data)) {
                result.push({
                    x: Array.from(Array(data[key].length).keys()),
                    y: data[key],
                    type: 'scatter',
                    name: key,
                })
        }
        return result
    }

    return (
        <div className="component">
            <Plot
                layout={layout}
                data={filterdData()}
            />
        </div>
    );
}

export default function ResultRenderer({ result, multiAlgorithms }) {
    return (
        <>
            {multiAlgorithms === undefined ? (
                <AreaGraphRenderer
                    key={Object.keys(result).length}
                    delayData={_.get(result, 'avgDelay', [])}
                    bakData={_.get(result, 'avgBackup', [])}
                    batteryData={_.get(result, 'avgBattery', [])}
                />
            ) : (
                <></>
            )}
            {multiAlgorithms !== undefined ? (
                <>
                    <AvgLineGraphRenderer
                        data={result['avgTotal']}
                        title={'Comparing Average Cost'}
                        yaxisLabel={'Time Average Cost'}
                    />
                    <AvgLineGraphRenderer
                        data={result['avgDelay']}
                        title={'Comparing Average Delay cost'}
                        yaxisLabel={'Time Average Delay Cost'}
                    />
                    <AvgLineGraphRenderer
                        data={result['avgBackup']}
                        title={'Comparing Average Backup Cost'}
                        yaxisLabel={'Time Average Backup Cost'}
                    />
                    <AvgLineGraphRenderer
                        data={result['avgBattery']}
                        title={'Comparing Average Battery Cost'}
                        yaxisLabel={'Time Average Battery Cost'}
                    />
                    <AvgLineGraphRenderer
                        data={result['avgEnergy']}
                        title={'Comparing Average Energy Cost'}
                        yaxisLabel={'Time Average Energy Cost'}
                    />
                </>
            ) : (
                <></>
            )}
        </>
    );
}
