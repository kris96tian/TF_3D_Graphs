// static/script.js
document.addEventListener('DOMContentLoaded', function() {
    const generateBtn = document.getElementById('generate-btn');
    const tfSelect = document.getElementById('tf-select');
    const nodeSize = document.getElementById('node-size');
    const colorSelected = document.getElementById('color-selected');
    const colorNeighbors = document.getElementById('color-neighbors');

    generateBtn.addEventListener('click', generateGraph);

    async function generateGraph() {
        const node = tfSelect.value;
        const size = parseInt(nodeSize.value);
        const selectedColor = colorSelected.value;
        const neighborsColor = colorNeighbors.value;

        try {
            const response = await fetch('/get_graph_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ node })
            });

            const data = await response.json();
            createPlot(data, node, size, selectedColor, neighborsColor);
            updateDistances(data.distances, node);
        } catch (error) {
            console.error('Error:', error);
        }
    }

    function createPlot(data, nodeOfInterest, size, selectedColor, neighborsColor) {
        const edgeTrace = {
            type: 'scatter3d',
            mode: 'lines',
            x: data.edge_x,
            y: data.edge_y,
            z: data.edge_z,
            line: {
                width: 0.5,
                color: '#888'
            },
            hoverinfo: 'none'
        };

        const nodeColors = data.nodes.map(node =>
            node === nodeOfInterest ? selectedColor : neighborsColor
        );

        const nodeTrace = {
            type: 'scatter3d',
            mode: 'markers+text',
            x: data.node_x,
            y: data.node_y,
            z: data.node_z,
            text: data.node_text,
            textposition: 'top center',
            hoverinfo: 'text',
            marker: {
                size: size * 1.5,
                color: nodeColors,
                line: {
                    width: 0.5,
                    color: '#888'
                }
            }
        };

        const layout = {
            title: {
                text: `3D Sub-Network of pathways centering: ${nodeOfInterest}`,
                x: 0.5
            },
            showlegend: false,
            scene: {
                xaxis: { showticklabels: false },
                yaxis: { showticklabels: false },
                zaxis: { showticklabels: false },
                aspectmode: 'data',
                camera: {
                    up: { x: 0, y: 0, z: 1 },
                    center: { x: 0, y: 0, z: 0 },
                    eye: { x: 1.5, y: 1.5, z: 1.5 }
                }
            },
            margin: { l: 0, r: 0, b: 0, t: 40 },
            paper_bgcolor: '#121212',
            plot_bgcolor: '#121212',
            template: 'plotly_dark'
        };

        Plotly.newPlot('graph-container', [edgeTrace, nodeTrace], layout);
    }

    function updateDistances(distances, nodeOfInterest) {
        const container = document.getElementById('distances-list');
        const header = document.querySelector('#distances-container h3');

        header.textContent = `'${nodeOfInterest}' relations to neighboring TFs:`;
        container.innerHTML = '';

        Object.entries(distances).forEach(([neighbor, distance]) => {
            const div = document.createElement('div');
            div.className = `distance-item ${distance >= 0 ? 'positive' : 'negative'}`;
            div.textContent = `${neighbor}: ${distance.toFixed(2)}`;
            container.appendChild(div);
        });
    }

    // Generate initial graph
    generateGraph();
});